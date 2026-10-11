from django.contrib import messages
from django.contrib.admin.views.decorators import staff_member_required
from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator
from django.db.models import Q
from django.http import Http404
from django.shortcuts import get_object_or_404, redirect, render
from django.utils.http import url_has_allowed_host_and_scheme
from django.views.decorators.http import require_http_methods, require_POST, require_safe

from . import services
from .forms import JobForm
from .models import Job

PER_PAGE = 20


@require_safe
def job_list(request):
    """Public list of live jobs, with search and filters."""
    jobs = Job.visible()
    q = request.GET.get("q", "").strip()[:100]
    job_type = request.GET.get("type", "")
    work_mode = request.GET.get("mode", "")
    if q:
        jobs = jobs.filter(Q(title__icontains=q) | Q(company__icontains=q) | Q(skills__icontains=q)
                           | Q(location__icontains=q))
    if job_type in Job.JobType.values:
        jobs = jobs.filter(job_type=job_type)
    if work_mode in Job.WorkMode.values:
        jobs = jobs.filter(work_mode=work_mode)
    page = Paginator(jobs, PER_PAGE).get_page(request.GET.get("page"))
    pending = Job.objects.filter(status=Job.Status.PENDING).count() if request.user.is_staff else 0
    return render(request, "jobs/list.html", {
        "page": page, "q": q, "job_type": job_type, "work_mode": work_mode, "pending": pending,
        "job_types": Job.JobType.choices, "work_modes": Job.WorkMode.choices,
        "filtered": bool(q or job_type or work_mode),
    })


@require_safe
def job_detail(request, pk, slug=None):
    job = get_object_or_404(Job.objects.select_related("posted_by"), pk=pk)
    if not services.can_view(request.user, job):
        raise Http404
    if slug != job.get_absolute_url().rstrip("/").rsplit("/", 1)[-1]:
        return redirect(job, permanent=True)      # keep one canonical URL per job
    return render(request, "jobs/detail.html", {"job": job, "can_manage": services.can_manage(request.user, job)})


@login_required
@require_http_methods(["GET", "POST"])
def job_new(request):
    if request.method == "POST":
        if services.over_daily_limit(request.user):
            messages.error(request, f"You can post up to {services.DAILY_POST_LIMIT} jobs a day. Please try again tomorrow.")
            return redirect("job_mine")
        form = JobForm(request.POST)
        if form.is_valid():
            job = form.save(commit=False)
            job.posted_by = request.user
            services.submit(job, request.user)
            if job.status == Job.Status.APPROVED:
                messages.success(request, "Your job is live.")
            else:
                messages.success(request, "Thanks! Your job will appear on the board once an admin approves it.")
            return redirect(job)
    else:
        form = JobForm()
    return render(request, "jobs/form.html", {"form": form, "editing": False})


@login_required
@require_http_methods(["GET", "POST"])
def job_edit(request, pk):
    job = get_object_or_404(Job, pk=pk)
    if not services.can_manage(request.user, job):
        raise Http404
    form = JobForm(request.POST or None, instance=job)
    if request.method == "POST" and form.is_valid():
        job = form.save(commit=False)
        services.submit(job, request.user)
        if job.status == Job.Status.PENDING:
            messages.success(request, "Saved. Your changes will be live once an admin reviews them.")
        else:
            messages.success(request, "Saved.")
        return redirect(job)
    return render(request, "jobs/form.html", {"form": form, "editing": True, "job": job})


@login_required
@require_POST
def job_delete(request, pk):
    job = get_object_or_404(Job, pk=pk)
    if not services.can_manage(request.user, job):
        raise Http404
    job.delete()
    messages.success(request, "Job deleted.")
    return redirect("job_mine")


@login_required
@require_safe
def job_mine(request):
    jobs = Job.objects.filter(posted_by=request.user).order_by("-created_at")
    return render(request, "jobs/mine.html", {"jobs": jobs})


# ---------------------------------------------------------------- review (staff)

@staff_member_required
@require_safe
def job_review(request):
    jobs = Job.objects.filter(status=Job.Status.PENDING).select_related("posted_by").order_by("created_at")
    return render(request, "jobs/review.html", {"jobs": jobs})


@staff_member_required
@require_POST
def job_moderate(request, pk):
    job = get_object_or_404(Job, pk=pk)
    action = request.POST.get("action")
    if action == "approve":
        job.approve(request.user)
        job.save()
        messages.success(request, f"Approved: {job.title}")
    elif action == "reject":
        services.reject(job, request.user, request.POST.get("note", "").strip())
        messages.info(request, f"Not approved: {job.title}")
    else:
        raise Http404
    nxt = request.POST.get("next", "")
    if nxt and url_has_allowed_host_and_scheme(nxt, allowed_hosts={request.get_host()}, require_https=request.is_secure()):
        return redirect(nxt)
    return redirect("job_review")

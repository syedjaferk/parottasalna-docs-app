from django import forms

from .models import Job


class JobForm(forms.ModelForm):
    class Meta:
        model = Job
        fields = ["title", "company", "location", "job_type", "work_mode", "experience", "salary", "skills",
                  "description", "apply_url", "apply_email", "last_date"]
        labels = {"apply_url": "Application link", "apply_email": "Or apply by email", "last_date": "Last date to apply"}
        widgets = {
            "description": forms.Textarea(attrs={"rows": 10, "placeholder": "What the role involves, who you're looking for, how to apply…"}),
            "last_date": forms.DateInput(attrs={"type": "date"}),
            "title": forms.TextInput(attrs={"placeholder": "Backend Developer (Python)"}),
            "company": forms.TextInput(attrs={"placeholder": "Company name"}),
            "location": forms.TextInput(attrs={"placeholder": "Chennai"}),
            "apply_url": forms.URLInput(attrs={"placeholder": "https://…"}),
        }

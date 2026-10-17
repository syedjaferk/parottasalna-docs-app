from django.conf import settings
from django.db import models
from django.utils import timezone


class Plan(models.Model):
    """A paid membership, for example Pro for a year. Prices are stored in paise (1 rupee = 100 paise)."""

    slug = models.SlugField(unique=True)
    name = models.CharField(max_length=80)
    tagline = models.CharField(max_length=200, blank=True)
    features = models.TextField(blank=True, help_text="One benefit per line.")
    price_paise = models.PositiveIntegerField()
    duration_days = models.PositiveSmallIntegerField(default=365)
    payment_url = models.URLField(blank=True, help_text="Your own payment page (e.g. a Razorpay payment link). "
                                  "When set, the Buy button opens it instead of the built-in checkout. You then grant access in the admin.")
    is_active = models.BooleanField(default=True)
    sort_order = models.PositiveSmallIntegerField(default=100)

    class Meta:
        ordering = ["sort_order", "price_paise"]

    def __str__(self):
        return self.name

    @property
    def price_rupees(self):
        return self.price_paise // 100

    @property
    def feature_list(self):
        return [line.strip() for line in self.features.splitlines() if line.strip()]


class Cohort(models.Model):
    """A live, mentor-led batch. Paying reserves a seat and enrols the student in the batch's course."""

    class Status(models.TextChoices):
        OPEN = "open", "Enrolling now"
        RUNNING = "running", "In progress"
        CLOSED = "closed", "Closed"

    slug = models.SlugField(unique=True)
    title = models.CharField(max_length=160)
    summary = models.TextField(blank=True)
    course = models.ForeignKey("courses.Course", null=True, blank=True, on_delete=models.SET_NULL,
                               help_text="Students who pay are enrolled in this course.")
    starts_on = models.DateField(null=True, blank=True)
    schedule = models.CharField(max_length=160, blank=True, help_text="e.g. Mon, Wed, Fri · 8-9 PM IST")
    price_paise = models.PositiveIntegerField(default=0)
    seats = models.PositiveSmallIntegerField(null=True, blank=True, help_text="Leave empty for no limit.")
    payment_url = models.URLField(blank=True, help_text="Your own payment page. When set, 'Reserve my seat' opens it. "
                                  "Add the student to the course in the admin once they have paid.")
    status = models.CharField(max_length=8, choices=Status.choices, default=Status.OPEN)
    is_listed = models.BooleanField(default=True)

    class Meta:
        ordering = ["-status", "starts_on"]

    def __str__(self):
        return self.title

    @property
    def price_rupees(self):
        return self.price_paise // 100

    @property
    def seats_left(self):
        if self.seats is None:
            return None
        taken = Order.objects.filter(cohort=self, status=Order.Status.PAID).count()
        return max(self.seats - taken, 0)

    @property
    def can_reserve(self):
        """Open, has seats left, and can be paid for (built-in checkout needs a price; a payment link does not)."""
        return self.status == self.Status.OPEN and (self.price_paise > 0 or bool(self.payment_url)) and self.seats_left != 0


class Order(models.Model):
    class Status(models.TextChoices):
        CREATED = "created", "Created"
        PAID = "paid", "Paid"
        FAILED = "failed", "Failed"

    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.PROTECT, related_name="orders")
    plan = models.ForeignKey(Plan, null=True, blank=True, on_delete=models.PROTECT)
    cohort = models.ForeignKey(Cohort, null=True, blank=True, on_delete=models.PROTECT)
    amount_paise = models.PositiveIntegerField()
    currency = models.CharField(max_length=3, default="INR")
    status = models.CharField(max_length=8, choices=Status.choices, default=Status.CREATED)
    razorpay_order_id = models.CharField(max_length=64, unique=True)
    razorpay_payment_id = models.CharField(max_length=64, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    paid_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self):
        return f"{self.razorpay_order_id} ({self.status})"

    @property
    def item_name(self):
        item = self.plan or self.cohort
        return str(item) if item else "Order"


class Membership(models.Model):
    """Time-limited Pro access. Several purchases stack: each one extends the end date."""

    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="memberships")
    plan = models.ForeignKey(Plan, on_delete=models.PROTECT)
    order = models.OneToOneField(Order, null=True, blank=True, on_delete=models.SET_NULL)
    starts_at = models.DateTimeField(default=timezone.now)
    ends_at = models.DateTimeField()

    class Meta:
        ordering = ["-ends_at"]

    def __str__(self):
        return f"{self.user} · {self.plan} until {self.ends_at:%Y-%m-%d}"

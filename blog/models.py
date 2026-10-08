from django.db import models
from django.urls import reverse


class Tag(models.Model):
    name = models.CharField(max_length=100, unique=True)
    slug = models.SlugField(max_length=120, unique=True)

    class Meta:
        ordering = ["name"]

    def __str__(self):
        return self.name


class Post(models.Model):
    """A blog post imported from the Obsidian vault (see the import_blog command)."""

    slug = models.SlugField(max_length=200, unique=True)
    title = models.CharField(max_length=300)
    published_at = models.DateTimeField()
    category = models.CharField(max_length=120, blank=True)
    category_slug = models.SlugField(max_length=140, blank=True, db_index=True)
    tags = models.ManyToManyField(Tag, blank=True, related_name="posts")
    body_html = models.TextField(help_text="Rendered and sanitised at import time.")
    excerpt = models.TextField(blank=True)
    reading_minutes = models.PositiveSmallIntegerField(default=1)
    related_slugs = models.JSONField(default=list, blank=True)
    wordpress_url = models.URLField(max_length=500, blank=True,
                                    help_text="Original post on WordPress, used as the canonical URL.")
    source_path = models.CharField(max_length=500, help_text="File in the vault this post came from.")
    is_published = models.BooleanField(default=True, help_text="Untick to hide a post without deleting it.")
    imported_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-published_at"]

    def __str__(self):
        return self.title

    def get_absolute_url(self):
        return reverse("blog_post", args=[self.slug])


class PostAsset(models.Model):
    """A vault file (image) used by a post. Only these files are served, and only for published posts."""

    post = models.ForeignKey(Post, on_delete=models.CASCADE, related_name="assets")
    path = models.CharField(max_length=500, db_index=True, help_text="Path inside the vault.")

    class Meta:
        constraints = [models.UniqueConstraint(fields=["post", "path"], name="uniq_post_asset")]

    def __str__(self):
        return self.path

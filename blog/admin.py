from django.contrib import admin
from django.utils.html import format_html

from .models import Post, Tag


@admin.register(Post)
class PostAdmin(admin.ModelAdmin):
    list_display = ("title", "category", "published_at", "is_published", "reading_minutes", "links")
    list_filter = ("is_published", "category")
    list_editable = ("is_published",)
    search_fields = ("title", "category", "excerpt")
    date_hierarchy = "published_at"
    filter_horizontal = ("tags",)
    readonly_fields = ("slug", "source_path", "wordpress_url", "imported_at", "body_html")
    fields = ("title", "slug", "is_published", "published_at", "category", "tags", "excerpt",
              "source_path", "wordpress_url", "imported_at", "body_html")

    @admin.display(description="")
    def links(self, obj):
        return format_html('<a href="{}">View</a>', obj.get_absolute_url())


@admin.register(Tag)
class TagAdmin(admin.ModelAdmin):
    list_display = ("name", "slug")
    search_fields = ("name",)

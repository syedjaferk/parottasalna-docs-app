from django.contrib.syndication.views import Feed
from django.urls import reverse

from courses import branding

from .models import Post


class LatestPostsFeed(Feed):
    title = f"{branding.NAME} Blog"
    description = branding.TAGLINE

    def link(self):
        return reverse("blog_index")

    def items(self):
        return Post.objects.filter(is_published=True)[:20]

    def item_title(self, item):
        return item.title

    def item_description(self, item):
        return item.excerpt

    def item_pubdate(self, item):
        return item.published_at

    def item_categories(self, item):
        return [item.category] if item.category else []

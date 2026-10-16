import tempfile
from pathlib import Path

from django.test import TestCase, override_settings
from django.urls import reverse

CHAPTER = """# Chapter 1: The Bell — ntfy

> *"A quiet server fails quietly."*

---

## 1. The Night

Meera waited.

![Present](images/here.jpg)
*A caption.*

![Absent](images/gone.jpg)
*Lost caption.*

<script>alert(1)</script>

```bash
curl -d hi ntfy.sh/x
```

## 2. The Fix

Done.

### Author's notes (delete before publishing)
- secret
"""


class BookTests(TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        root = Path(self.tmp.name)
        (root / "images").mkdir()
        (root / "images" / "here.jpg").write_bytes(b"\xff\xd8jpeg")
        (root / "01-ntfy.md").write_text(CHAPTER, encoding="utf-8")
        override = override_settings(BOOK_ROOT=root)
        override.enable()
        self.addCleanup(override.disable)
        self.addCleanup(self.tmp.cleanup)

    def test_index_lists_chapter(self):
        page = self.client.get(reverse("book_index"))
        self.assertContains(page, "The Bell")
        self.assertContains(page, "ntfy")

    def test_chapter_renders_safely(self):
        page = self.client.get(reverse("book_chapter", args=["ntfy"]))
        self.assertContains(page, "<figcaption>A caption.</figcaption>", html=False)
        self.assertContains(page, 'id="1-the-night"')
        self.assertNotContains(page, "<script>alert")
        self.assertNotContains(page, "Lost caption")
        self.assertNotContains(page, "secret")
        self.assertContains(page, "A quiet server fails quietly.")

    def test_media_only_serves_images_in_folder(self):
        self.assertEqual(self.client.get(reverse("book_media", args=["here.jpg"])).status_code, 200)
        self.assertEqual(self.client.get(reverse("book_media", args=["gone.jpg"])).status_code, 404)
        self.assertEqual(self.client.get("/stories/media/..%2F01-ntfy.md").status_code, 404)

    def test_unknown_chapter_404(self):
        self.assertEqual(self.client.get(reverse("book_chapter", args=["nope"])).status_code, 404)

from django.db import migrations


def rename(apps, schema_editor):
    Course = apps.get_model("courses", "Course")
    Course.objects.filter(slug="go-lang", title="40 Days of Go").update(title="Golang from Scratch: Learn Go Step by Step")


class Migration(migrations.Migration):
    dependencies = [("courses", "0008_learning_paths")]
    operations = [migrations.RunPython(rename, migrations.RunPython.noop)]

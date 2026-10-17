from django.db import migrations


def set_defaults(apps, schema_editor):
    """Existing public courses stay free to enrol in; the rest stay invite-only, as they were."""
    Course = apps.get_model("courses", "Course")
    Course.objects.filter(is_common=True).update(access="free")
    Course.objects.filter(is_common=False).update(access="invite")
    Site = apps.get_model("sites", "Site")
    Site.objects.filter(domain="example.com").update(domain="learn.parottasalna.com", name="Parottasalna")


class Migration(migrations.Migration):
    dependencies = [("courses", "0005_catalog_fields"), ("sites", "0002_alter_domain_unique")]
    operations = [migrations.RunPython(set_defaults, migrations.RunPython.noop)]

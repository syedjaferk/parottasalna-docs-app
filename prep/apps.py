from django.apps import AppConfig


class PrepConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "prep"

    def ready(self):
        from django.db.models.signals import post_delete, post_save

        from . import catalog
        from .models import CatalogLookup, CatalogProblem, CatalogSheet, PatternGuide, PlacementQuestion

        for model in (CatalogLookup, CatalogProblem, CatalogSheet, PatternGuide, PlacementQuestion):
            post_save.connect(lambda **kw: catalog.invalidate(), sender=model, weak=False, dispatch_uid=f"prep_invalidate_{model.__name__}_save")
            post_delete.connect(lambda **kw: catalog.invalidate(), sender=model, weak=False, dispatch_uid=f"prep_invalidate_{model.__name__}_del")

from . import services


def attention(request):
    """Header badge for staff: how many things are waiting (job reviews + failed course builds)."""
    user = getattr(request, "user", None)
    if not (user and user.is_authenticated and user.is_staff):
        return {}
    return {"panel_attention": services.attention_count()}

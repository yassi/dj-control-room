from django.conf import settings
from django.templatetags.static import static
from django.utils.html import format_html, mark_safe

DEFAULTS = {
    "LOAD_DEFAULT_CSS": True,
    "EXTRA_CSS": [],
}


def get_config(key):
    user_config = getattr(settings, "DJ_CONTROL_ROOM_SETTINGS", {})
    return user_config.get(key, DEFAULTS[key])


def get_css_context():
    links = []
    for path in get_config("EXTRA_CSS"):
        url = path if path.startswith(("http://", "https://", "//")) else static(path)
        links.append(format_html('<link rel="stylesheet" href="{}">', url))
    return {
        "dj_cr_load_default_css": get_config("LOAD_DEFAULT_CSS"),
        "dj_cr_extra_css": mark_safe("\n".join(links)),
    }

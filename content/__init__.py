from .facts import BIZ, PENDING, CONFIRMED  # noqa: F401
from .pages import PAGES, NAV, LEGACY  # noqa: F401

_slugs = [p["slug"] for p in PAGES]
assert len(_slugs) == len(set(_slugs)), "duplicate slug"
for _p in PAGES:
    for _k in ("title", "desc", "h1", "answer", "blocks"):
        assert _p.get(_k), f"{_p['slug'] or 'home'} is missing {_k}"
for _k in CONFIRMED:
    assert _k in PENDING, f"CONFIRMED has unknown key {_k}"

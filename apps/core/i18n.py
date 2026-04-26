from __future__ import annotations

from django.utils.functional import lazy
from django.utils.translation import get_language


def lang_text(ru: str, kk: str | None = None) -> str:
    language = (get_language() or "ru").split("-", 1)[0]
    if language == "kk":
        return kk or ru
    return ru


lang_text_lazy = lazy(lang_text, str)

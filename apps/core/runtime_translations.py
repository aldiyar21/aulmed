from __future__ import annotations

from django.utils.translation import get_language
from django.utils.translation.trans_real import DjangoTranslation


_SUSPICIOUS_TRANSLATION_CHARS = {
    *{chr(codepoint) for codepoint in range(0x80, 0xA0)},
    "‘",
    "’",
    "‚",
    "“",
    "”",
    "•",
    "–",
    "—",
    "™",
    "‹",
    "›",
    "Ѓ",
    "ѓ",
    "Љ",
    "љ",
    "Њ",
    "њ",
    "Ћ",
    "ћ",
    "Џ",
    "џ",
    "Ў",
    "ў",
}


RUNTIME_TRANSLATIONS = {
    "All medical episodes with quick access to the patient and visit outcome.": {
        "ru": "Все медицинские эпизоды с быстрым доступом к пациенту и результату приёма.",
        "kk": "Пациентке және қабылдау нәтижесіне жылдам қолжетімді барлық медициналық эпизодтар.",
    },
    "Appointment": {"ru": "Запись", "kk": "Жазылу"},
    "Create": {"ru": "Создать", "kk": "Жасау"},
    "Date": {"ru": "Дата", "kk": "Күні"},
    "Destination": {"ru": "Куда", "kk": "Бағыт"},
    "Diagnosis": {"ru": "Диагноз", "kk": "Диагноз"},
    "Download": {"ru": "Скачать", "kk": "Жүктеу"},
    "Employee": {"ru": "Сотрудник", "kk": "Қызметкер"},
    "My encounters": {"ru": "Мои обращения", "kk": "Менің қабылдауларым"},
    "My prescriptions": {"ru": "Мои рецепты", "kk": "Менің рецепттерім"},
    "My referrals": {"ru": "Мои направления", "kk": "Менің жолдамаларым"},
    "No conditions.": {"ru": "Нет состояний.", "kk": "Жағдайлар жоқ."},
    "No encounters found.": {"ru": "Обращения не найдены.", "kk": "Қабылдаулар табылмады."},
    "No encounters.": {"ru": "Обращений нет.", "kk": "Қабылдаулар жоқ."},
    "No measurements yet.": {"ru": "Измерений пока нет.", "kk": "Өлшемдер әзірше жоқ."},
    "No referrals.": {"ru": "Направлений нет.", "kk": "Жолдамалар жоқ."},
    "Number": {"ru": "Номер", "kk": "Нөмір"},
    "Printable": {"ru": "Печать", "kk": "Басып шығару"},
    "Priority": {"ru": "Приоритет", "kk": "Басымдық"},
    "Profile": {"ru": "Профиль", "kk": "Профиль"},
    "Responsible employee": {"ru": "Ответственный сотрудник", "kk": "Жауапты қызметкер"},
    "Result": {"ru": "Результат", "kk": "Нәтиже"},
    "Title": {"ru": "Название", "kk": "Атауы"},
    "Conditions": {"ru": "Состояния", "kk": "Жағдайлар"},
    "Recent encounters": {"ru": "Последние обращения", "kk": "Соңғы қабылдаулар"},
    "Open the patient's measurements history or add new indicators from the doctor side.": {
        "ru": "Откройте историю измерений пациента или добавьте новые показатели со стороны врача.",
        "kk": "Пациенттің өлшемдер тарихын ашыңыз немесе дәрігер жағынан жаңа көрсеткіштер қосыңыз.",
    },
    "In progress": {"ru": "Идёт", "kk": "Өтіп жатыр"},
    "Use patient, encounter, prevention and referral lists for CSV exports and daily registries.": {
        "ru": "Используйте списки пациентов, обращений, профилактики и направлений для CSV-выгрузок и ежедневных реестров.",
        "kk": "CSV экспорттары мен күнделікті тізілімдер үшін пациенттер, қабылдаулар, профилактика және жолдамалар тізімдерін пайдаланыңыз.",
    },
    "Content": {"ru": "Содержание", "kk": "Мазмұны"},
    "Pulse": {"ru": "Пульс", "kk": "Пульс"},
    "Temperature": {"ru": "Температура", "kk": "Температура"},
    "Specialist": {"ru": "Специалист", "kk": "Маман"},
}


def _looks_suspicious_translation(text: str) -> bool:
    return any(char in _SUSPICIOUS_TRANSLATION_CHARS for char in text)


def _runtime_gettext(self, message):
    translated = _runtime_gettext._original(self, message)
    language = (get_language() or "ru").split("-", 1)[0]
    fallback = RUNTIME_TRANSLATIONS.get(message)
    if fallback and (_looks_suspicious_translation(translated) or translated == message):
        return fallback.get(language) or fallback.get("ru") or message
    return translated


def install_runtime_translations() -> None:
    if getattr(DjangoTranslation, "_aulmed_runtime_i18n_installed", False):
        return
    _runtime_gettext._original = DjangoTranslation.gettext
    DjangoTranslation.gettext = _runtime_gettext
    DjangoTranslation._aulmed_runtime_i18n_installed = True

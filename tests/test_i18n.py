from django.utils.translation import gettext, override


def test_ru_runtime_fallback_covers_broken_and_missing_strings():
    with override("ru"):
        assert gettext("In progress") == "Идёт"
        assert (
            gettext("Use patient, encounter, prevention and referral lists for CSV exports and daily registries.")
            == "Используйте списки пациентов, обращений, профилактики и направлений для CSV-выгрузок и ежедневных реестров."
        )
        assert gettext("Content") == "Содержание"
        assert gettext("Pulse") == "Пульс"
        assert gettext("Temperature") == "Температура"
        assert gettext("Specialist") == "Специалист"


def test_kk_runtime_fallback_covers_missing_strings():
    with override("kk"):
        assert gettext("Conditions") == "Жағдайлар"
        assert gettext("Recent encounters") == "Соңғы қабылдаулар"
        assert gettext("Content") == "Мазмұны"
        assert gettext("Specialist") == "Маман"

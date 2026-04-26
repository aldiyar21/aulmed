from __future__ import annotations

from django import forms
from django.contrib.auth.models import User

from apps.core.forms import html5_date_input
from apps.core.i18n import lang_text_lazy
from apps.facilities.models import Facility
from apps.patients.models import Patient


class PatientForm(forms.ModelForm):
    create_portal_account = forms.BooleanField(
        required=False,
        initial=True,
        label=lang_text_lazy("Создать аккаунт пациента", "Пациент аккаунтын құру"),
    )
    portal_username = forms.CharField(
        required=False,
        max_length=150,
        label=lang_text_lazy("Логин пациента", "Пациент логині"),
    )
    portal_password = forms.CharField(
        required=False,
        widget=forms.PasswordInput(render_value=True),
        label=lang_text_lazy("Пароль пациента", "Пациент құпиясөзі"),
    )

    class Meta:
        model = Patient
        fields = [
            "last_name",
            "first_name",
            "middle_name",
            "iin",
            "birth_date",
            "sex",
            "phone",
            "address",
            "settlement_name",
            "facility",
            "social_category",
            "risk_level",
            "attachment_date",
            "notes",
            "is_active",
        ]
        labels = {
            "last_name": lang_text_lazy("Фамилия", "Тегі"),
            "first_name": lang_text_lazy("Имя", "Аты"),
            "middle_name": lang_text_lazy("Отчество", "Әкесінің аты"),
            "iin": lang_text_lazy("ИИН", "ЖСН"),
            "birth_date": lang_text_lazy("Дата рождения", "Туған күні"),
            "sex": lang_text_lazy("Пол", "Жынысы"),
            "phone": lang_text_lazy("Телефон", "Телефон"),
            "address": lang_text_lazy("Адрес", "Мекенжай"),
            "settlement_name": lang_text_lazy("Населенный пункт", "Елді мекен"),
            "facility": lang_text_lazy("Учреждение", "Медициналық ұйым"),
            "social_category": lang_text_lazy("Социальная категория", "Әлеуметтік санат"),
            "risk_level": lang_text_lazy("Группа риска", "Қауіп тобы"),
            "attachment_date": lang_text_lazy("Дата прикрепления", "Тіркелген күні"),
            "notes": lang_text_lazy("Примечания", "Ескертпелер"),
            "is_active": lang_text_lazy("Активен", "Белсенді"),
        }
        widgets = {
            "birth_date": html5_date_input(),
            "attachment_date": html5_date_input(),
            "notes": forms.Textarea(attrs={"rows": 3}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if self.instance.pk and self.instance.patient_user_id:
            self.fields.pop("create_portal_account", None)
            self.fields.pop("portal_username", None)
            self.fields.pop("portal_password", None)
        else:
            self.fields["portal_username"].help_text = lang_text_lazy(
                "Укажите логин для входа пациента в личный кабинет.",
                "Пациенттің жеке кабинетіне кіру логинін көрсетіңіз.",
            )
            self.fields["portal_password"].help_text = lang_text_lazy(
                "Укажите временный пароль для первого входа пациента.",
                "Пациенттің алғашқы кіруіне уақытша құпиясөз көрсетіңіз.",
            )

        self.fields["sex"].choices = [
            ("male", lang_text_lazy("Мужской", "Ер")),
            ("female", lang_text_lazy("Женский", "Әйел")),
        ]

        self.fields["social_category"].choices = [
            ("general", lang_text_lazy("Общая", "Жалпы")),
            ("child", lang_text_lazy("Ребенок", "Бала")),
            ("pregnant", lang_text_lazy("Беременная", "Жүкті")),
            ("elderly", lang_text_lazy("Пожилой", "Егде жастағы")),
            ("disabled", lang_text_lazy("Лицо с инвалидностью", "Мүгедектігі бар адам")),
        ]

        self.fields["risk_level"].choices = [
            ("low", lang_text_lazy("Низкий", "Төмен")),
            ("medium", lang_text_lazy("Средний", "Орташа")),
            ("high", lang_text_lazy("Высокий", "Жоғары")),
        ]


    def clean(self):
        cleaned_data = super().clean()
        if "create_portal_account" not in self.fields:
            return cleaned_data

        if not cleaned_data.get("create_portal_account"):
            return cleaned_data

        username = (cleaned_data.get("portal_username") or "").strip()
        password = cleaned_data.get("portal_password") or ""
        if not username:
            self.add_error("portal_username", lang_text_lazy("Укажите логин пациента.", "Пациент логинін көрсетіңіз."))
        if not password:
            self.add_error("portal_password", lang_text_lazy("Укажите пароль пациента.", "Пациент құпиясөзін көрсетіңіз."))
        if username:
            qs = User.objects.filter(username=username)
            if self.instance.pk and self.instance.patient_user_id:
                qs = qs.exclude(pk=self.instance.patient_user_id)
            if qs.exists():
                self.add_error("portal_username", lang_text_lazy("Этот логин уже занят.", "Бұл логин бос емес."))
        return cleaned_data


class PatientFilterForm(forms.Form):
    q = forms.CharField(required=False, label=lang_text_lazy("Поиск", "Іздеу"))

    settlement_name = forms.CharField(
        required=False,
        label=lang_text_lazy("Населенный пункт", "Елді мекен"),
    )

    facility = forms.ModelChoiceField(
        queryset=Facility.objects.filter(is_active=True),
        required=False,
        label=lang_text_lazy("Учреждение", "Медициналық ұйым"),
    )

    sex = forms.ChoiceField(
        required=False,
        choices=[
            ("", lang_text_lazy("Все", "Барлығы")),
            ("male", lang_text_lazy("Мужской", "Ер")),
            ("female", lang_text_lazy("Женский", "Әйел")),
        ],
        label=lang_text_lazy("Пол", "Жынысы"),
    )

    risk_level = forms.ChoiceField(
        required=False,
        choices=[
            ("", lang_text_lazy("Все", "Барлығы")),
            ("low", lang_text_lazy("Низкий", "Төмен")),
            ("medium", lang_text_lazy("Средний", "Орташа")),
            ("high", lang_text_lazy("Высокий", "Жоғары")),
        ],
        label=lang_text_lazy("Риск", "Қауіп"),
    )

    is_active = forms.TypedChoiceField(
        required=False,
        coerce=lambda value: True if value == "True" else False if value == "False" else None,
        choices=(
            ("", lang_text_lazy("Все", "Барлығы")),
            ("True", lang_text_lazy("Активные", "Белсенді")),
            ("False", lang_text_lazy("Неактивные", "Белсенді емес")),
        ),
        label=lang_text_lazy("Активность", "Белсенділік"),
    )

    age_group = forms.ChoiceField(
        required=False,
        choices=(
            ("", lang_text_lazy("Все", "Барлығы")),
            ("child", lang_text_lazy("Дети", "Балалар")),
            ("adult", lang_text_lazy("Взрослые", "Ересектер")),
            ("elderly", lang_text_lazy("Пожилые", "Егде жастағы")),
        ),
        label=lang_text_lazy("Возрастная группа", "Жас тобы"),
    )

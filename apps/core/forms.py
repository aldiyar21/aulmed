from django import forms


HTML5_DATE_FORMAT = "%Y-%m-%d"
HTML5_DATETIME_LOCAL_FORMAT = "%Y-%m-%dT%H:%M"


def html5_date_input(**attrs):
    return forms.DateInput(format=HTML5_DATE_FORMAT, attrs={"type": "date", **attrs})


def html5_datetime_input(**attrs):
    return forms.DateTimeInput(format=HTML5_DATETIME_LOCAL_FORMAT, attrs={"type": "datetime-local", **attrs})


class DateRangeForm(forms.Form):
    date_from = forms.DateField(required=False, widget=html5_date_input())
    date_to = forms.DateField(required=False, widget=html5_date_input())

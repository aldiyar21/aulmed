from __future__ import annotations

import csv
from datetime import date

from django.http import HttpResponse
from django.utils import timezone


def export_to_csv(filename_prefix: str, headers: list[str], rows: list[list[str]]) -> HttpResponse:
    response = HttpResponse(content_type="text/csv; charset=utf-8")
    response["Content-Disposition"] = (
        f'attachment; filename="{filename_prefix}_{timezone.localdate().isoformat()}.csv"'
    )
    response.write("\ufeff")
    writer = csv.writer(response)
    writer.writerow(headers)
    writer.writerows(rows)
    return response


def calculate_age(birth_date: date) -> int:
    today = timezone.localdate()
    return today.year - birth_date.year - ((today.month, today.day) < (birth_date.month, birth_date.day))

from django.shortcuts import render

from apps.accounts.decorators import roles_required


@roles_required("Администратор системы", "Руководитель")
def reports_view(request):
    return render(request, "reports/index.html")

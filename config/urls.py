from django.conf import settings
from django.conf.urls import handler403, handler404, handler500
from django.contrib import admin
from django.contrib.auth import views as auth_views
from django.contrib.staticfiles.urls import staticfiles_urlpatterns
from django.urls import include, path

from apps.core import views as core_views

urlpatterns = [
    path("admin/", admin.site.urls),
    path("login/", auth_views.LoginView.as_view(template_name="registration/login.html"), name="login"),
    path("logout/", auth_views.LogoutView.as_view(), name="logout"),
    path("", include("apps.core.urls")),
    path("accounts/", include("apps.accounts.urls")),
    path("facilities/", include("apps.facilities.urls")),
    path("patients/", include("apps.patients.urls")),
    path("encounters/", include("apps.encounters.urls")),
    path("visits/", include("apps.visits.urls")),
    path("prevention/", include("apps.prevention.urls")),
    path("referrals/", include("apps.referrals.urls")),
    path("reports/", include("apps.reports.urls")),
]

handler403 = core_views.permission_denied_view
handler404 = core_views.page_not_found_view
handler500 = core_views.server_error_view

if settings.DEBUG:
    urlpatterns += staticfiles_urlpatterns()

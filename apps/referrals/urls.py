from django.urls import path

from . import views

urlpatterns = [
    path("", views.referral_list, name="referral-list"),
    path("create/", views.referral_create, name="referral-create"),
    path("export/", views.referral_export_csv, name="referral-export"),
    path("<int:pk>/edit/", views.referral_update, name="referral-update"),
]

from django.urls import path

from . import views

urlpatterns = [
    path("consultations/", views.consultation_list, name="consultation-list"),
    path("consultations/<int:pk>/", views.consultation_detail, name="consultation-detail"),
    path("consultations/<int:pk>/consent/", views.consultation_consent, name="consultation-consent"),
    path("consultations/<int:pk>/room/", views.consultation_room, name="consultation-room"),
    path("consultations/<int:pk>/start/", views.consultation_start, name="consultation-start"),
    path("consultations/<int:pk>/complete/", views.consultation_complete, name="consultation-complete"),
    path("consultations/<int:pk>/cancel/", views.consultation_cancel, name="consultation-cancel"),
    path("consultations/<int:pk>/print/", views.printable_consultation_summary, name="printable-consultation-summary"),
    path("teleconsiliums/", views.teleconsilium_list, name="teleconsilium-list"),
    path("teleconsiliums/create/", views.teleconsilium_create_view, name="teleconsilium-create"),
    path("teleconsiliums/<int:pk>/", views.teleconsilium_detail, name="teleconsilium-detail"),
    path("teleconsiliums/<int:pk>/edit/", views.teleconsilium_update_view, name="teleconsilium-update"),
    path("teleconsiliums/<int:pk>/room/", views.teleconsilium_room, name="teleconsilium-room"),
    path("teleconsiliums/<int:pk>/complete/", views.teleconsilium_complete_view, name="teleconsilium-complete"),
]

from django.conf.urls import include, url
from django.urls import path

from django.contrib import admin
from rest_framework import routers
from rest_framework.urlpatterns import format_suffix_patterns
from OneToOne import views

router = routers.SimpleRouter()

router.register(r'Machines', views.MachineViewSet, basename="machines_list")
router.register(r'MainPacks', views.MainPackViewSet, basename="main_packs_list")
router.register(r'Technicians', views.TechnicianViewSet, basename="technicians_list")
router.register(r'Filters', views.FilterViewSet, basename="filters_list")
router.register(r'Cases', views.CaseViewSet, basename="cases_list")

urlpatterns = [
]
urlpatterns += router.urls

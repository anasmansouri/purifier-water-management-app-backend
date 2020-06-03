from django.conf.urls import include, url
from django.urls import path

from django.contrib import admin
from rest_framework import routers
from rest_framework.urlpatterns import format_suffix_patterns
from OneToOne import views

router = routers.SimpleRouter()
router.register(r'accounts', views.StudentViewSet, basename="students_list")
router.register(r'Machines', views.MachineViewSet, basename="machines_list")
router.register(r'MainPacks', views.MainPackViewSet, basename="main_packs_list")
router.register(r'Technicians', views.TechnicianViewSet, basename="technicians_list")
router.register(r'Filters', views.FilterViewSet, basename="filters_list")
router.register(r'Cases', views.CaseViewSet, basename="cases_list")

urlpatterns = [
    path('prerigstration/', views.preregistration_view),
    path('registration/', views.registration_view),
    path('verify_email/', views.verify_email),
    path('api-token-auth/', views.CustomAuthToken.as_view()),
    path('logout/', views.logout),
    path('forgotpassword/', views.forgotpassword),
    path('update_password/', views.updada_password),
    path('update_contact_name/', views.updada_contact_name),
    path('update_email_address/', views.updada_email_address),

]
urlpatterns += router.urls

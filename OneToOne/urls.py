from django.conf.urls import include, url
from django.urls import path

from django.contrib import admin
from rest_framework import routers
from rest_framework.urlpatterns import format_suffix_patterns
from OneToOne import views

router = routers.SimpleRouter()
router.register(r'accounts', views.StudentViewSet, basename="students_list")

urlpatterns = [
    path('prerigstration/', views.preregistration_view),
    path('registration/', views.registration_view),
    path('verify_email/', views.verify_email),
    path('api-token-auth/', views.CustomAuthToken.as_view()),
    path('logout/', views.logout),
    path('forgotpassword/', views.forgotpassword)
]
urlpatterns += router.urls

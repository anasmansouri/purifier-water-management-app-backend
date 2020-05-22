from django.conf.urls import include, url
from django.urls import path

from django.contrib import admin
from rest_framework import routers
from rest_framework.urlpatterns import format_suffix_patterns
from OneToOne import views

router = routers.SimpleRouter()
router.register(r'accounts', views.StudentViewSet, basename="students_list")

urlpatterns = [
    path('admin/', admin.site.urls)
    , path('security/', include('OneToOne.urls'))
]
urlpatterns += router.urls

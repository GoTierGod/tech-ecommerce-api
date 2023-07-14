from django.contrib import admin
from django.urls import path, include
from rest_framework_simplejwt.views import (
    TokenRefreshView,
)
from . import views

urlpatterns = [
    path("", views.get_routers),
    path("admin/", admin.site.urls),
    path("api/", include("api.urls")),
    path("api/token/", views.MyTokenObtainPairView.as_view(), name="token_obtain_pair"),
    path("api/token/refresh/", TokenRefreshView.as_view(), name="token_refresh"),
]

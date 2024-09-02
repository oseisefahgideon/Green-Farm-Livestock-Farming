from django.urls import include, path

urlpatterns = [
    path("auth/", include("authentication.urls")),
    path("account/", include("account.urls")),
    path("management/", include("management.urls")),
]

from .views import CreateUserView, RetrieveUpdateDeleteUserView, FarmRetrieveUpdateDeleteView
from django.urls import path


urlpatterns = [
    path("user/register/", CreateUserView.as_view(), name="register"),
    path("user/", RetrieveUpdateDeleteUserView.as_view(), name="retrieve_update_delete"),
    path(
        "farm/<pk>/",
        FarmRetrieveUpdateDeleteView.as_view(),
        name="farm",
    ),
]
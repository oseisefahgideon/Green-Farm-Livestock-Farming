from .views import CreateUserView, RetrieveUpdateDeleteUserView
from django.urls import path


urlpatterns = [
    path("user/register/", CreateUserView.as_view(), name="register"),
    path("user/", RetrieveUpdateDeleteUserView.as_view(), name="retrieve_update_delete"),
]
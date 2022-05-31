from django.urls import path
from users import views

urlpatterns = [
    path('phone-register/', views.AuthSmsSendView.as_view(), name="phoneuser-create"),
    path('register/', views.UserCreateAPIView.as_view(), name='user-create'),
    path("profile/add/", views.UserPatchAPIView.as_view()),
    path("profile/", views.UserProfileAPIView.as_view()),
    path("profile_list/", views.ProfileListAPIView.as_view()),
    path("interest/", views.UserInterestAPIView.as_view()),
    path("interest_list/", views.InterestListAPIView.as_view()),
]

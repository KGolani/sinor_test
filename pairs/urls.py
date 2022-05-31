from django.urls import path

from .views import LocationView, MatchingView, MetoYou, YoutoMe, TestView

urlpatterns = [
   path('', LocationView.as_view()),
   path('/match', MatchingView.as_view()),
   path('/mylike', MetoYou.as_view()),
   path('/youlike', YoutoMe.as_view()),
   path('/test',TestView.as_view()),
]
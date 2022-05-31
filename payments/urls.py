from django.urls import path

from .views      import PaymentView,SchedulesView,SchedulesCancleView,ReadyPayment

urlpatterns = [
   path('/pay',PaymentView.as_view()),
   path('/callback',SchedulesView.as_view()),
   path('/ready',ReadyPayment.as_view()),
   path('/cancle',SchedulesCancleView.as_view())
]
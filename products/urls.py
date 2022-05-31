from django.urls import path

from .views      import ProductView,PointView,CouponView,NoticeView,EventView

urlpatterns = [
   path('/product',ProductView.as_view()),
   path('/point',PointView.as_view()),
   path('/coupon',CouponView.as_view()),
   path('/notice',NoticeView.as_view()),
   path('/event',EventView.as_view())
]
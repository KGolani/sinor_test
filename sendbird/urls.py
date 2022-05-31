from django.urls import path

from sendbird.views import SendbirdMAUView, SendbirdDAUView, SendbirdWebhookCategoriesView, SendbirdWebhookView, \
    SendbirdReportView

urlpatterns = [
    path('/mau', SendbirdMAUView.as_view()),
    path('/dau', SendbirdDAUView.as_view()),
    path('/webhook/categories', SendbirdWebhookCategoriesView.as_view()),
    path('/callback', SendbirdWebhookView.as_view()),
    path('/report', SendbirdReportView.as_view()), # 테스트용도
]

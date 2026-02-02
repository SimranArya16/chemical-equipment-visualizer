from django.urls import path
from .views import FileUploadView, DataSummaryView, UploadHistoryView, GeneratePDFView

urlpatterns = [
    path('upload/', FileUploadView.as_view(), name='upload'),
    path('summary/', DataSummaryView.as_view(), name='summary'),
    path('history/', UploadHistoryView.as_view(), name='history'),
    path('pdf/', GeneratePDFView.as_view(), name='pdf'),
]
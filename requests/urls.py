from django.urls import path
from . import views
from .views import RequestPDFView

urlpatterns = [
    # ... другие URL ...
    path('request/<int:pk>/pdf/', RequestPDFView.as_view(), name='request_pdf'),
]
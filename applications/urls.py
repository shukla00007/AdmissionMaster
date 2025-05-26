from django.urls import path
from django.conf import settings
from django.conf.urls.static import static

from . import views

urlpatterns = [
    path('', views.home, name='home'),
    path('login/', views.login_view, name='login'),
    path('register/', views.register_view, name='register'),
    path('logout/', views.logout_view, name='logout'),
    path('dashboard/', views.dashboard, name='dashboard'),
    path('application/select/', views.select_application, name='select_application'),
    path('application/<int:application_id>/personal/', views.personal_info, name='personal_info'),
    path('application/<int:application_id>/education/', views.education_info, name='education_info'),
    path('application/<int:application_id>/documents/', views.documents_upload, name='documents_upload'),
    path('application/<int:application_id>/preview/', views.preview_application, name='preview_application'),
    path('application/<int:application_id>/submit/', views.submit_application, name='submit_application'),
    path('application/<int:application_id>/download/', views.download_application, name='download_application'),
    path('check-status/', views.check_status, name='check_status'),
# Removed contact URL pattern as per user request to revert changes
]

# Add media URL patterns for development
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
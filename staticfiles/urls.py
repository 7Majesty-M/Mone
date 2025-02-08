from .views import *
from django.urls import path
from django.conf import settings
from django.conf.urls.static import static

from .views import custom_404

urlpatterns = [
    path('', index, name='index'),
    path('about/', about_us, name='about'),
    path('classes/', classes, name='classes'),
    path('register/', UserRegisterView.as_view(), name='register'),
    path('login/', UserLoginView.as_view(), name='login'),
    path('logout/', custom_logout_view, name='logout'),
    path('profile/<int:user_id>/', profile_view, name='profile'),
    path('confirm-email/<str:token>/', confirm_email, name='confirm_email'),
    path('resend-confirmation-email/', resend_confirmation_email, name='resend_confirmation_email'),
    path('request-password-reset/', request_password_reset, name='request_password_reset'),
    path('reset-password/<str:token>/', reset_password, name='reset_password'),
    path('menu/', menu_list, name='menu_list'),
    path('contact-page/', contact, name='contact'),
    path('schedule/', schedule, name='schedule'),
    path('404/', view_404, name='404'),
    path('gallery/', gallery, name='gallery'),
    path('404/', custom_404, name='404'),
    path("set-language/<str:lang>/", set_language, name="set_language"),
]

if settings.DEBUG:
        urlpatterns += static(settings.MEDIA_URL,
                              document_root=settings.MEDIA_ROOT)
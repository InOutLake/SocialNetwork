from django.urls import path
from django.conf.urls import include
from .views import profile_list, profile_detail, main, register, activate

app_name = 'meetter'

urlpatterns = [
    path('accounts/', include('django.contrib.auth.urls')),
    path('accounts/register/', register, name='register'),
    path('main/', main, name='main'),
    path('profile_list/', profile_list, name='profile_list'),
    path('profile_detail/<int:pk>/', profile_detail, name='profile_detail'),
    path('activate/(?P<uidb64>[0-9A-Za-z_\-]+)/(?P<token>[0-9A-Za-z]{1,13}-[0-9A-Za-z]{1,20})/', activate,
         name='activate'),
]

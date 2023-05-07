from django.urls import path,include
from . import views
from . import create_user



urlpatterns = [
    path('home/', views.home, name='home'),
    path('inbox/', views.inbox_view, name='inbox'),
    path('userdata/', create_user.userdata,),
    path("accounts/", include("django.contrib.auth.urls")),

    path(r'ticket/<int:ticket_id>', views.ticket_detail_view, name='ticket_detail'),
    path(r'ticket/create', views.ticket_create_view, name='ticket_create'),


]   
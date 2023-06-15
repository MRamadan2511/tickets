from django.urls import path,include
from . import views
from . import create_user



from .views import TicketDetailView, TicketCommentView, TicketUpdateWarehouseView,TicketUpdateTagToView, TicketListView

urlpatterns = [
    
]



urlpatterns = [
    path('home/', views.home, name='home'),
    path('inbox/', TicketListView.as_view(), name='inbox'),
    path('dashboard/', views.dashboard, name='dashboard'),
    
    path('userdata/', create_user.userdata,),
    path("accounts/", include("django.contrib.auth.urls")),

    # path(r'update_wh_tag/<int:ticket_id>', views.update_wh_tag, name='update_wh_tag'),
    # path(r'ticket/<int:ticket_id>', views.ticket_detail_view, name='ticket_detail'),
    
    path(r'ticket/create', views.ticket_create_view, name='ticket_create'),


    path('ticket/<int:pk>/', TicketDetailView.as_view(), name='ticket_detail'),
    path('ticket/<int:pk>/comment/', TicketCommentView.as_view(), name='ticket_comment'),
    path('ticket/<int:pk>/update_warehouse/', TicketUpdateWarehouseView.as_view(), name='ticket_update_warehouse'),
    path('ticket/<int:pk>/update_tag/', TicketUpdateTagToView.as_view(), name='ticket_update_tag'),
]
 
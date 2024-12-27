from django.urls import path




from .views import (
    UserView,
    create_team,
    create_attendance,
    user_list,
    team_list,
    attendance_list,
    login_view,
    reset_password,
    dashboard_view,
    set_new_password,
    magic_link,
    logout_view,
    check_in_view,
    check_out_view,
    attendance_view,
    timer_info
)
urlpatterns = [
    path('user/create/', UserView.as_view(), name='user_create'),
    path('user/<int:pk>/', UserView.as_view(), name='user_detail'),
    path('user/<int:pk>/update/', UserView.as_view(), name='user_update'),
    path('user/<int:pk>/delete/', UserView.as_view(), name='user_delete'),
    path('create_team/', create_team, name='create_team'),
    path('create_attendance/', create_attendance, name='create_attendance'),
    path('users/', user_list, name='user_list'),
    path('teams/', team_list, name='team_list'),
    
    path('login/', login_view.as_view(), name='login'),
    path('reset_password/', reset_password, name='reset_password'),
    path('dashboard/', dashboard_view, name='dashboard'), 
    path('set_new_password/<uidb64>/<token>/', set_new_password, name='set_new_password'),
    path('magic_link/', magic_link, name='magic_link'),
    path('logout/',logout_view, name='logout'),
    path('check_in/',check_in_view, name='check_in'),
    path('check_out/',check_out_view, name='check_out'),
    path('attendance/<str:timeframe>',attendance_view,name='attendance'),
    path('timer_info/',timer_info,name='timer_info'),


]

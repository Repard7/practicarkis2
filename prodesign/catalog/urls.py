from django.urls import path
from catalog import views

urlpatterns = [
    #Все
    # Все
    path('', views.index_view, name='index'),
    path('login/', views.login_view, name='login'),
    path('register/', views.register_view, name='register'),

    # Только пользователь зарегистрированный
    path('request/', views.user_request_list_view, name='user_requests'),
    path('logout/', views.logout_view, name='logout'),
    path('request/delete/<int:pk>/', views.deleting_request_view, name='delete'),
    path('request/create/', views.creating_request_view, name='create'),
    path('profile', views.profile_view, name='profile'),

    # Только админ
    path('superadmin/', views.admin_panel_include_all_requests_view, name='admin_panel'),
    path('request/edit/<int:pk>/', views.edit_request_view, name='edit_request'),
    path('category', views.category_view, name='category'),
    path('category/<int:pk>', views.deleting_category_view, name='delete_category'),
]

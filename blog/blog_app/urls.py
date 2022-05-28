from . import views
from django.urls import path

urlpatterns = [
    path('', views.PostList.as_view(), name='home'),
    # path('<slug:slug>/', views.PostDetail.as_view(), name='post_detail'),
    path('detail/<slug:slug>/', views.post_detail, name='post_detail'),
    path('edit/<slug:slug>/', views.edit_detail, name='edit_detail'),
    path('login/', views.login_form, name='login_form'),
    path('login/authenticate/', views.login_authenticate, name='login_authenticate'),
    path('logout/', views.logout_user, name='logout_user'),
    path('register/', views.register_form, name='register_form'),
    path('register/create-user/', views.create_user, name='create_user'),
    path('draft-list/', views.DraftList.as_view(), name='draft_list'),
    # path('draft-list/draft-detail/<slug:slug>/', views.draft_detail, name='draft_detail'),
    path('post-list/', views.PostedList.as_view(), name='post_list'),
    # path('post-list/post-detail/<slug:slug>/', views.post_detail, name='post_detail'),
    path('user-detail/', views.user_detail, name='user_detail'),
    path('create-post/', views.create_post, name='create_post'),
    path('delete-post/<slug:slug>/', views.delete_post, name='delete_post'),
]
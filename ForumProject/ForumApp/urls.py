from django.urls import path
from .views import *




urlpatterns = [
    path('', category_list_view, name='home_page'),
    path('categories/', category_list_view, name='categories_page'),
    path('categories/create/', create_category_view, name='create_category'),
    path('categories/<uuid:category_id>/posts/', category_posts_view, name='category_posts'),
    path('categories/<uuid:category_id>/posts/create/', create_post_view, name='create_post'),
    path('categories/<slug:category_slug>/posts/<uuid:post_id>/', post_view, name='post_detail'),
    path('categories/<slug:category_slug>/posts/<uuid:post_id>/like/', toggle_post_like, name='toggle_post_like'),
    path('categories/<uuid:category_id>/delete/', delete_category_view, name='delete_category'),

    path('posts/<uuid:post_id>/delete/', delete_post_view, name='delete_post'),

    path('comments/<uuid:comment_id>/like/', toggle_comment_like, name='toggle_comment_like'),
    path('comments/<uuid:comment_id>/delete/', delete_comment_view, name='delete_comment'),

    path('login/', login_view, name='login_page'),
    path('logout/', logout_view, name='logout'),
    path('register/', register_view, name='register_page'),

    path('profile/', profile_view, name='profile_page'),
    path('profile/edit/', edit_profile, name='edit_profile'),
    path('profile/change-password/', change_password, name='change_password'),
]
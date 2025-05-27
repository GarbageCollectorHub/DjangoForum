from django.shortcuts import render, redirect
from django.http import HttpRequest
from django.contrib import messages
import os
from django.contrib.auth import login, logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import AuthenticationForm
from django.shortcuts import get_object_or_404
from django.views.decorators.http import require_POST
from django.http import JsonResponse
from django.contrib.auth.forms import PasswordChangeForm
from django.contrib.auth import update_session_auth_hash
from django.http import HttpResponseForbidden

from .models import Category, Post, Comment
from .forms import CategoryForm, RegisterForm, ProfileForm, PostForm, CommentForm



def category_list_view(request:HttpRequest):
    categories = Category.objects.all()
    context = {
        'categories': categories,
        'page_title': 'Categories',
    }
    return render(request, 'forum/category_list.html', context)


@login_required(login_url='login_page')
def create_category_view(request: HttpRequest):
    if request.method == 'POST':
        form = CategoryForm(request.POST, request.FILES)
        if form.is_valid():
            category = form.save(commit=False)
            category.created_by = request.user
            category.save()
            messages.success(request, "Category created successfully")
            return redirect('categories_page')
    else:
        form = CategoryForm()

    context = {
        'form': form,
        'page_title': 'Create category',
    }
    return render(request, 'forum/create_category.html', context)

    

def category_posts_view(request:HttpRequest, category_id):
    category = get_object_or_404(Category, id=category_id)
    posts = category.posts.all()
    context = {
        'category': category,
        'posts': posts,
        'page_title': f'{category.title} posts'
    }
    return render(request, 'forum/category_posts.html', context)


@login_required(login_url='login_page')
def create_post_view(request: HttpRequest, category_id):
    category = get_object_or_404(Category, id=category_id)
    if request.method == 'POST':
        form = PostForm(request.POST)
        if form.is_valid():
            post = form.save(commit=False)
            post.category = category
            post.created_by = request.user
            post.save()
            messages.success(request, 'Post created successfully!')
            return redirect('category_posts', category_id=category.id)
    else:
        form = PostForm()
    context = {
        'form': form,
        'category': category,
        'page_title': 'Create Post'
    }
    return render(request, 'forum/create_post.html', context)



def post_view(request: HttpRequest, category_slug: str, post_id):
    category = get_object_or_404(Category, slug=category_slug)
    post = get_object_or_404(Post, id=post_id, category=category)
    if request.method == 'POST':
        if not request.user.is_authenticated:
            return redirect('login_page')      
        form = CommentForm(request.POST)
        if form.is_valid():
            comment = form.save(commit=False)
            comment.post = post
            comment.created_by = request.user
            comment.save()
            return redirect('post_detail', category_slug=category.slug, post_id=post.id)
    else:
        form = CommentForm()

    context = {
        'form': form,
        'post': post,
        'comments': post.comments.all(),
        'page_title': f'Post: {post.title}'
    }
    return render(request, 'forum/post.html', context)




### Delete POST ###

@login_required(login_url='login_page')
def delete_post_view(request:HttpRequest, post_id):
    post = get_object_or_404(Post, id=post_id)
    if request.method == 'POST' and request.user == post.created_by:
        post.delete()
        messages.success(request, 'Post deleted successfully.')
        return redirect('categories_page')
    return HttpResponseForbidden("You are not allowed to delete this post.")
    

@login_required(login_url='login_page')
def delete_category_view(request:HttpRequest, category_id):
    category = get_object_or_404(Category, id = category_id)
    if request.method == 'POST' and request.user == category.created_by:
        if category.icon:
            icon_path = category.icon.path
            if os.path.exists(icon_path):
                os.remove(icon_path)
        category.delete()
        messages.success(request, 'Category deleted successfully.')
        return redirect('categories_page')
    return HttpResponseForbidden("You are not allowed to delete this category.")


@login_required(login_url='login_page')
def delete_comment_view(request:HttpRequest, comment_id):
    comment = get_object_or_404(Comment, id=comment_id)
    if request.method == 'POST' and request.user == comment.created_by:
        category_slug = comment.post.category.slug
        post_id = comment.post.id
        comment.delete()
        messages.success(request, 'Comment deleted successfully.')
        return redirect('post_detail', category_slug=category_slug, post_id=post_id)
    return redirect('post_detail', category_slug=comment.post.category.slug, post_id=comment.post.id)



###     Auth View     ###

def login_view(request: HttpRequest):
    if request.method == "POST":
        form = AuthenticationForm(request, data=request.POST)
        if form.is_valid():
            user = form.get_user()
            print("logged in:", user)
            login(request, user)
            return redirect("home_page")
    else:
        form = AuthenticationForm()

    context = {
        "form": form,
        "page_title": "Login",
    }
    return render(request, 'auth/login.html', context)


def register_view(request: HttpRequest):
    if request.method == "POST":
        form = RegisterForm(request.POST, request.FILES)
        if form.is_valid():
            user = form.save()
            login(request, user)
            return redirect("home_page")
    else:
        form = RegisterForm()

    context = {
        "form": form,
        "page_title": "Register",
    }
    return render(request, "auth/register.html", context)

    
###     Profile Views       ###

def logout_view(request:HttpRequest):
    logout(request)
    return redirect("login_page")


@login_required(login_url='login_page')
def profile_view(request:HttpRequest):
    return render(request, 'user/profile.html', {'user': request.user, "page_title": "Profile"})


@login_required(login_url='login_page')
def edit_profile(request:HttpRequest):
    user = request.user
    old_avatar = user.avatar.path if user.avatar else None
    if request.method == 'POST':
        form = ProfileForm(request.POST, request.FILES, instance=user)
        if form.is_valid():
            if old_avatar and 'avatar' in request.FILES:
                if os.path.exists(old_avatar):
                    os.remove(old_avatar)
            form.save()
            return redirect('profile_page')
    else:
        form = ProfileForm(instance=user)
    return render(request, 'user/edit_profile.html', {'form': form})


@login_required(login_url='login_page')
def change_password(request:HttpRequest):
    if request.method == 'POST':
        form = PasswordChangeForm(user=request.user, data=request.POST)
        if form.is_valid():
            user = form.save()
            update_session_auth_hash(request, user) # обнолвяем сессию юзера после смены пароля
            messages.success(request, 'Password changed successfully.')
            return redirect('profile_page')
    else:
        form = PasswordChangeForm(user=request.user)
    return render(request, 'user/change_password.html', {'form': form})


###     Likes View      ###
@login_required
@require_POST
def toggle_comment_like(request:HttpRequest, comment_id):
    comment = get_object_or_404(Comment, id=comment_id)
    user = request.user
    if user in comment.likes.all():
        comment.likes.remove(user)
        liked = False
    else:
        comment.likes.add(user)
        liked = True

    return JsonResponse({
        'likes_count': comment.likes.count(),
        'liked': liked,
    })


@login_required(login_url='login_page')
def toggle_post_like(request:HttpRequest, category_slug, post_id):
    post = get_object_or_404(Post, id=post_id, category__slug=category_slug)
    user = request.user
    if user in post.likes.all():
        post.likes.remove(user)
        liked = False
    else:
        post.likes.add(user)
        liked = True

    return JsonResponse({
        'likes_count': post.likes.count(),
        'liked': liked,
    })
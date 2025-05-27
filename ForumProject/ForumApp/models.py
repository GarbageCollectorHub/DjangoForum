from django.db import models
from django.utils.text import slugify
from uuid import uuid4
from django.contrib.auth.models import AbstractBaseUser, PermissionsMixin, BaseUserManager
from django.core.validators import MinLengthValidator
import os
from unidecode import unidecode


# Variables 
title_max_length = 100
description_max_length = 255
content_max_length = 1020


# Functions

def unique_file_name(instance, filename):
    extension = filename.split('.')[-1]
    new_filename = f"{uuid4().hex}.{extension}"
    return os.path.join("category_icons", new_filename)


def generate_unique_slug(title, model_class):
    base_slug = slugify(unidecode(title))
    if not base_slug:
        base_slug = str(uuid4())[:8]

    slug = base_slug
    counter = 1

    while model_class.objects.filter(slug=slug).exists():
        slug = f"{base_slug}-{counter}"
        counter += 1

    return slug


# Models

class CustomUserManager(BaseUserManager):
    def create_user(self, email, password, **extra_fields):
        if not email:
            raise ValueError("Email is required")
        email = self.normalize_email(email)
        user = self.model(email = email, **extra_fields)
        user.set_password(password)
        user.save()
        return user
    
    def create_superuser(self, email, password, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        return self.create_user(email, password, **extra_fields)


class User(AbstractBaseUser, PermissionsMixin):
    email = models.EmailField(unique=True)
    username = models.CharField(max_length=30, validators=[MinLengthValidator(3)], unique=True)
    full_name = models.CharField(max_length=255)
    birth_date = models.DateField(null=True, blank=True)
    avatar = models.ImageField(upload_to='avatars/', null=True, blank=True)

    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['full_name', 'username']

    objects = CustomUserManager()

    def __str__(self):
        return f"{self.username}"
    


class Category(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid4, editable=False)
    title = models.CharField(null=False, unique=True, max_length = title_max_length)
    slug = models.SlugField(unique=True, blank=True)
    description = models.TextField(max_length = description_max_length)
    icon = models.ImageField(upload_to=unique_file_name, blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    created_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)

    class Meta:
        db_table = "categories"
        ordering = ['-created_at']

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = generate_unique_slug(self.title, Category)
        super().save(*args, **kwargs)

    def __str__(self):
        return self.title



class Post(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid4, editable=False)
    title = models.CharField(max_length = title_max_length)
    content = models.TextField(max_length = content_max_length)
    created_at = models.DateTimeField(auto_now_add=True)
    created_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)
    category = models.ForeignKey(Category, related_name='posts', on_delete=models.CASCADE)
    likes = models.ManyToManyField(User, related_name="liked_posts", blank=True)

    class Meta:
        db_table = "posts"
        ordering = ['-created_at']

    def __str__(self):
        return self.title



class Comment(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid4, editable=False)
    content = models.TextField(max_length = content_max_length, validators=[MinLengthValidator(5)])
    created_at = models.DateTimeField(auto_now_add=True)
    created_by = models.ForeignKey(User, on_delete=models.CASCADE)
    post = models.ForeignKey(Post, related_name='comments', on_delete=models.CASCADE)


    likes = models.ManyToManyField(User, related_name="liked_comments", blank=True)

    class Meta:
        db_table = 'comments'
        ordering = ['-created_at']

    def __str__(self):
        return f'Comment by {self.created_by.username} on {self.post.title}'

from django.contrib import admin
from .models import *

# Register your models here.



@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ('id', 'title', 'slug', 'created_at', 'created_by', 'icon', 'description' )
    list_filter = ('title', 'created_by')

admin.site.register(Post)

# admin.site.register(Comment)

@admin.register(Comment)
class CommentAdmin(admin.ModelAdmin):
    list_display = ('id', 'likes_count', 'created_at', 'created_by', 'content', 'post')

    def likes_count(self, obj):
        return obj.likes.count()
    likes_count.short_description = 'Likes'
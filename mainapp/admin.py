from django.contrib import admin
from .models import User, Post, Comment, PostReaction, CommentReaction
# Register your models here.
#@admin.register(User)
#class CustomUserAdmin(admin.ModelAdmin):
#    pass
admin.site.register(User)
admin.site.register(Post)
admin.site.register(Comment)
admin.site.register(PostReaction)
admin.site.register(CommentReaction)

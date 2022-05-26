from django.contrib import admin
from .models import ActivationCode, User, Post, Comment, PostReaction, CommentReaction


admin.site.register(User)
admin.site.register(Post)
admin.site.register(Comment)
admin.site.register(PostReaction)
admin.site.register(CommentReaction)
admin.site.register(ActivationCode)

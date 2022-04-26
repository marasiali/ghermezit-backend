from rest_framework import serializers
from .models import Post, Comment, PostReaction, CommentReaction

class PostSerializer(serializers.ModelSerializer):
    author = serializers.ReadOnlyField(source='author.username')
    likes = serializers.IntegerField()
    class Meta:
        model = Post
        fields = ['id', 'title', 'content', 'author', 'created_at', 'likes']

class PostReactionSerializer(serializers.ModelSerializer):
    class Meta:
        model = PostReaction
        fields = ['id']

class CommentCreateSerializer(serializers.ModelSerializer):
    author = serializers.ReadOnlyField(source='author.username')
    class Meta:
        model = Comment
        fields = ['id', 'content', 'author', 'created_at']

class CommentRetrieveSerializer(serializers.ModelSerializer):
    author = serializers.ReadOnlyField(source='author.username')
    likes = serializers.IntegerField()
    class Meta:
        model = Comment
        fields = ['id', 'content', 'author', 'post', 'created_at', 'likes']


class CommentReactionSerializer(serializers.ModelSerializer):
    class Meta:
        model = CommentReaction
        fields = ['id']

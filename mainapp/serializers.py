from rest_framework import serializers
from .models import Post, Comment, PostReaction, CommentReaction


class PostSerializer(serializers.ModelSerializer):
    author = serializers.ReadOnlyField(source='author.username')
    likes = serializers.SerializerMethodField()

    class Meta:
        model = Post
        fields = ['id', 'title', 'content', 'author', 'created_at', 'likes']

    def get_likes(self, post):
        likes = PostReaction.objects.filter(post=post, isLike=True).count() - PostReaction.objects.filter(post=post,
                                                                                                          isLike=False).count()
        return likes


class PostReactionSerializer(serializers.ModelSerializer):
    class Meta:
        model = PostReaction
        fields = ['id']


class CommentSerializer(serializers.ModelSerializer):
    author = serializers.ReadOnlyField(source='author.username')
    likes = serializers.SerializerMethodField()

    class Meta:
        model = Comment
        fields = ['id', 'content', 'author', 'post', 'created_at', 'likes']

    def get_likes(self, comment):
        likes = CommentReaction.objects.filter(comment=comment, isLike=True).count() - CommentReaction.objects.filter(
            comment=comment, isLike=False).count()
        return likes


class CommentReactionSerializer(serializers.ModelSerializer):
    class Meta:
        model = CommentReaction
        fields = ['id']

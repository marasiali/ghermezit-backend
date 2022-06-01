from rest_framework import serializers
from .models import Post, Comment, PostReaction, CommentReaction
from rest_captcha.serializers import RestCaptchaSerializer

class CaptchaSerializer(RestCaptchaSerializer):
    pass

class PostSerializer(serializers.ModelSerializer):
    author = serializers.ReadOnlyField(source='author.username')
    like_status = serializers.SerializerMethodField()
    likes = serializers.ReadOnlyField()

    def get_like_status(self, obj):
        if self.context['request'].user.is_authenticated:
            try:
                react_obj = obj.postreaction_set.get(author=self.context['request'].user)
                if react_obj.isLike:
                    return 1
                else:
                    return -1
            except PostReaction.DoesNotExist:
                return 0
        return None

    class Meta:
        model = Post
        fields = ['id', 'title', 'content', 'author', 'created_at', 'like_status', 'likes']

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
    like_status = serializers.SerializerMethodField()
    likes = serializers.ReadOnlyField()

    def get_like_status(self, obj):
        if self.context['request'].user.is_authenticated:
            try:
                react_obj = obj.commentreaction_set.get(author=self.context['request'].user)
                if react_obj.isLike:
                    return 1
                else:
                    return -1
            except CommentReaction.DoesNotExist:
                return 0
        return None
    
    class Meta:
        model = Comment
        fields = ['id', 'content', 'author', 'post', 'created_at', 'like_status', 'likes']

class CommentReactionSerializer(serializers.ModelSerializer):
    class Meta:
        model = CommentReaction
        fields = ['id']

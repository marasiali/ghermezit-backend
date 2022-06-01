from rest_framework import serializers
from .models import ActivationCode, Post, Comment, PostReaction, CommentReaction, User
from django.db import transaction
from dj_rest_auth.registration.serializers import RegisterSerializer

class EmailPhonenumberRegisterSerializer(RegisterSerializer):
    phone_number = serializers.CharField(max_length=20, required=False)

    def validate(self, data):
        if 'email' not in data and 'phone_number' not in data :
            raise serializers.ValidationError("You must provide an email or a phone number!")
        if 'email' in data and 'phone_number' in data :
            raise serializers.ValidationError("You must provide an email or a phone number, not both!")
        return data

    def validate_phone_number(self, value):
        if value and User.objects.filter(phone_number=value).exists():
            raise serializers.ValidationError("This phone number has already registered!")
        return value

    @transaction.atomic
    def save(self, request):
        user = super().save(request)
        user.phone_number = self.data.get('phone_number')
        user.save()
        return user

    def get_cleaned_data(self):
        cleaned_data = super().get_cleaned_data()
        cleaned_data['phone_number'] = self.data.get('phone_number')
        return cleaned_data


class ActivationCodeSerializer(serializers.Serializer):
    phone_number = serializers.CharField(max_length=20)
    code = serializers.CharField(max_length=6)


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

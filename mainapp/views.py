from django.shortcuts import get_object_or_404, render
from rest_framework import generics, permissions, mixins, status
from rest_framework.exceptions import ValidationError
from rest_framework.response import Response

from .models import Post, PostReaction, Comment, CommentReaction
from .serializers import CommentCreateSerializer, PostSerializer, PostReactionSerializer, CommentRetrieveSerializer, CommentReactionSerializer
from .permissions import IsAuthorOrReadOnly


class PostList(generics.ListCreateAPIView):
    queryset = Post.objects.all()
    serializer_class = PostSerializer
    permission_classes=[permissions.IsAuthenticatedOrReadOnly]

    def perform_create(self, serializer):
        serializer.save(author=self.request.user)

class PostRetrieveDestroy(generics.RetrieveDestroyAPIView):
    queryset = Post.objects.all()
    serializer_class = PostSerializer
    permission_classes=[permissions.IsAuthenticatedOrReadOnly, IsAuthorOrReadOnly]

class PostLikeCreate(generics.CreateAPIView, mixins.DestroyModelMixin):
    serializer_class = PostReactionSerializer
    permission_classes=[permissions.IsAuthenticated]

    def get_queryset(self):
        self.this_post = get_object_or_404(Post, pk=self.kwargs['pk'])
        return PostReaction.objects.filter(author=self.request.user, post=self.this_post)

    def perform_create(self, serializer):
        react_object = self.get_queryset().first()
        if react_object:
            if react_object.isLike:
                raise ValidationError("You have already liked this post!")
            else:
                react_object.isLike=True
                react_object.save()
        else:
            serializer.save(author=self.request.user, post=self.this_post, isLike=True)

    def delete(self, request, *args, **kwargs):
        deleted_react_count, _ = self.get_queryset().delete()
        if deleted_react_count != 0:
            return Response(status=status.HTTP_204_NO_CONTENT)
        else:
            raise ValidationError("You never liked this post!")

class PostDislikeCreate(generics.CreateAPIView, mixins.DestroyModelMixin):
    serializer_class = PostReactionSerializer
    permission_classes=[permissions.IsAuthenticated]

    def get_queryset(self):
        self.this_post = get_object_or_404(Post, pk=self.kwargs['pk'])
        return PostReaction.objects.filter(author=self.request.user, post=self.this_post)

    def perform_create(self, serializer):
        react_object = self.get_queryset().first()
        if react_object:
            if not react_object.isLike:
                raise ValidationError("You have already disliked this post!")
            else:
                react_object.isLike = False
                react_object.save()
        else:
            serializer.save(author=self.request.user, post=self.this_post, isLike=False)
        
    def delete(self, request, *args, **kwargs):
        deleted_react_count, _ = self.get_queryset().delete()
        if deleted_react_count != 0:
            return Response(status=status.HTTP_204_NO_CONTENT)
        else:
            raise ValidationError("You never disliked this post!")

class CommentList(generics.ListCreateAPIView):
    permission_classes=[permissions.IsAuthenticatedOrReadOnly]

    def get_queryset(self):
        post = get_object_or_404(Post, pk=self.kwargs['pk'])
        return Comment.objects.filter(post=post)

    def get_serializer_class(self):
        if self.request.method == 'POST':
            return CommentCreateSerializer
        return CommentRetrieveSerializer

    def perform_create(self, serializer):
        post = get_object_or_404(Post, pk=self.kwargs['pk'])
        serializer.save(author=self.request.user, post=post)

class CommentRetrieveDestroy(generics.RetrieveDestroyAPIView):
    queryset = Comment.objects.all()
    serializer_class = CommentRetrieveSerializer
    permission_classes=[permissions.IsAuthenticatedOrReadOnly, IsAuthorOrReadOnly]


class CommentLikeCreate(generics.CreateAPIView, mixins.DestroyModelMixin):
    serializer_class = CommentReactionSerializer
    permission_classes=[permissions.IsAuthenticated]

    def get_queryset(self):
        self.comment = Comment.objects.get(pk=self.kwargs['pk'])
        return CommentReaction.objects.filter(author=self.request.user, comment=self.comment)

    def perform_create(self, serializer):
        react_object = self.get_queryset().first()
        if react_object:
            if react_object.isLike:
                raise ValidationError("You have already liked this comment!")
            else:
                react_object.isLike=True
                react_object.save()
        else:
            serializer.save(author=self.request.user, comment=self.comment, isLike=True)
        
    def delete(self, request, *args, **kwargs):
        deleted_react_count, _ = self.get_queryset().delete()
        if deleted_react_count != 0:
            return Response(status=status.HTTP_204_NO_CONTENT)
        else:
            raise ValidationError("You never liked this comment!")

class CommentDislikeCreate(generics.CreateAPIView, mixins.DestroyModelMixin):
    serializer_class = CommentReactionSerializer
    permission_classes=[permissions.IsAuthenticated]

    def get_queryset(self):
        self.comment = Comment.objects.get(pk=self.kwargs['pk'])
        return CommentReaction.objects.filter(author=self.request.user, comment=self.comment)

    def perform_create(self, serializer):
        react_object = self.get_queryset().first()
        if react_object:
            if not react_object.isLike:
                raise ValidationError("You have already disliked this comment!")
            else:
                react_object.isLike=False
                react_object.save()
        else:
            serializer.save(author=self.request.user, comment=self.comment, isLike=False)

    def delete(self, request, *args, **kwargs):
        deleted_react_count, _ = self.get_queryset().delete()
        if deleted_react_count != 0:
            return Response(status=status.HTTP_204_NO_CONTENT)
        else:
            raise ValidationError("You never disliked this comment!")
    
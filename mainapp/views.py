from django.shortcuts import render
from rest_framework import generics, permissions, mixins, status
from rest_framework.exceptions import ValidationError
from rest_framework.response import Response
from .models import Post, PostReaction, Comment, CommentReaction
from .serializers import PostSerializer, PostReactionSerializer, CommentSerializer, CommentReactionSerializer
# Create your views here.

class PostList(generics.ListAPIView):
    queryset = Post.objects.all()
    serializer_class = PostSerializer

class PostRetrieveDestroy(generics.RetrieveDestroyAPIView):
    queryset = Post.objects.all()
    serializer_class = PostSerializer
    permission_classes=[permissions.IsAuthenticatedOrReadOnly]

    def delete(self, request, *args, **kwargs):
        post = Post.objects.filter(pk=self.kwargs['pk'], author=self.request.user)
        if post.exists():
            return self.destroy(request, *args, **kwargs)
        else:
            raise ValidationError("This is not your post to delete!")

class PostCreate(generics.CreateAPIView):
    serializer_class = PostSerializer
    permission_classes=[permissions.IsAuthenticated]

    def perform_create(self, serializer):
        serializer.save(author=self.request.user)

class PostLikeCreate(generics.CreateAPIView, mixins.DestroyModelMixin):
    serializer_class = PostReactionSerializer
    permission_classes=[permissions.IsAuthenticated]

    def get_queryset(self):
        author = self.request.user
        post = Post.objects.get(pk=self.kwargs['pk'])
        return PostReaction.objects.filter(author=author, post=post)

    def perform_create(self, serializer):
        if self.get_queryset().exists():
            object = self.get_queryset().first()
            if object.isLike:
                raise ValidationError("You have already liked this post!")
            else :
                object.isLike=True
                object.save()
        else:
            post = Post.objects.get(pk=self.kwargs['pk'])
            serializer.save(author=self.request.user, post=post, isLike=True)

    def delete(self, request, *args, **kwargs):
        if self.get_queryset().exists():
            self.get_queryset().delete()
            return Response(status=status.HTTP_204_NO_CONTENT)
        else:
            raise ValidationError("You never liked this post!")

class PostDislikeCreate(generics.CreateAPIView, mixins.DestroyModelMixin):
    serializer_class = PostReactionSerializer
    permission_classes=[permissions.IsAuthenticated]

    def get_queryset(self):
        author = self.request.user
        post = Post.objects.get(pk=self.kwargs['pk'])
        return PostReaction.objects.filter(author=author, post=post)

    def perform_create(self, serializer):
        if self.get_queryset().exists():
            object = self.get_queryset().first()
            if object.isLike==False:
                raise ValidationError("You have already disliked this post!")
            else :
                object.isLike=False
                object.save()
        else:
            post = Post.objects.get(pk=self.kwargs['pk'])
            serializer.save(author=self.request.user, post=post, isLike=False)

    def delete(self, request, *args, **kwargs):
        if self.get_queryset().exists():
            self.get_queryset().delete()
            return Response(status=status.HTTP_204_NO_CONTENT)
        else:
            raise ValidationError("You never diliked this post!")

class CommentList(generics.ListAPIView):
    queryset = Comment.objects.all()
    serializer_class = CommentSerializer

class CommentRetrieveDestroy(generics.RetrieveDestroyAPIView):
    queryset = Comment.objects.all()
    serializer_class = CommentSerializer
    permission_classes=[permissions.IsAuthenticatedOrReadOnly]

    def delete(self, request, *args, **kwargs):
        comment = Comment.objects.filter(pk=self.kwargs['pk'], author=self.request.user)
        if comment.exists():
            return self.destroy(request, *args, **kwargs)
        else:
            raise ValidationError("This is not your comment to delete!")

class CommentCreate(generics.CreateAPIView):
    serializer_class = CommentSerializer
    permission_classes=[permissions.IsAuthenticated]

    def perform_create(self, serializer):
        serializer.save(author=self.request.user)

class CommentLikeCreate(generics.CreateAPIView, mixins.DestroyModelMixin):
    serializer_class = CommentReactionSerializer
    permission_classes=[permissions.IsAuthenticated]

    def get_queryset(self):
        author = self.request.user
        comment = Comment.objects.get(pk=self.kwargs['pk'])
        return CommentReaction.objects.filter(author=author, comment=comment)

    def perform_create(self, serializer):
        if self.get_queryset().exists():
            object = self.get_queryset().first()
            if object.isLike:
                raise ValidationError("You have already liked this comment!")
            else :
                object.isLike=True
                object.save()
        else:
            comment = Comment.objects.get(pk=self.kwargs['pk'])
            serializer.save(author=self.request.user, comment=comment, isLike=True)

    def delete(self, request, *args, **kwargs):
        if self.get_queryset().exists():
            self.get_queryset().delete()
            return Response(status=status.HTTP_204_NO_CONTENT)
        else:
            raise ValidationError("You never liked this comment!")

class CommentDislikeCreate(generics.CreateAPIView, mixins.DestroyModelMixin):
    serializer_class = CommentReactionSerializer
    permission_classes=[permissions.IsAuthenticated]

    def get_queryset(self):
        author = self.request.user
        comment = Comment.objects.get(pk=self.kwargs['pk'])
        return CommentReaction.objects.filter(author=author, comment=comment)

    def perform_create(self, serializer):
        if self.get_queryset().exists():
            object = self.get_queryset().first()
            if object.isLike==False:
                raise ValidationError("You have already disliked this comment!")
            else :
                object.isLike=False
                object.save()
        else:
            comment = Comment.objects.get(pk=self.kwargs['pk'])
            serializer.save(author=self.request.user, comment=comment, isLike=False)

    def delete(self, request, *args, **kwargs):
        if self.get_queryset().exists():
            self.get_queryset().delete()
            return Response(status=status.HTTP_204_NO_CONTENT)
        else:
            raise ValidationError("You never diliked this comment!")

from django.http import Http404
from django.shortcuts import get_object_or_404, render
from django.db.models import Count, Q
from rest_framework import generics, permissions, mixins, status, filters
from rest_framework.exceptions import ValidationError
from rest_framework.response import Response

from mainapp.pagination import CommentPagination, PostPagination

from .models import Post, PostReaction, Comment, CommentReaction, UserProfile
from .serializers import CommentCreateSerializer, PostSerializer, PostReactionSerializer, CommentRetrieveSerializer, \
    CommentReactionSerializer, UserProfileSerializer
from .permissions import IsAuthorOrReadOnly


class PostListCreate(generics.ListCreateAPIView):
    """For filter results based on a condition, use the `filter` query parameter with one of the following values:
        
        - `liked`

        - `disliked`

        - `me`
    """
    serializer_class = PostSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]
    pagination_class = PostPagination
    filter_backends = [filters.OrderingFilter, filters.SearchFilter]
    ordering_fields = ['created_at', 'likes']
    search_fields = ['title', 'content']

    def get_queryset(self):
        filter_param = self.request.query_params.get('filter')
        if filter_param == 'liked':
            queryset = Post.objects.filter(postreaction__isLike=True)
        elif filter_param == 'disliked':
            queryset = Post.objects.filter(postreaction__isLike=False)
        elif filter_param == 'me':
            queryset = Post.objects.filter(author=self.request.user)
        else:
            queryset = Post.objects.all()
        queryset = queryset.annotate(
            likes=Count('postreaction', filter=Q(postreaction__isLike=True)) - Count('postreaction', filter=Q(
                postreaction__isLike=False))
        )
        return queryset

    def perform_create(self, serializer):
        serializer.save(author=self.request.user)


class PostRetrieveDestroy(generics.RetrieveDestroyAPIView):
    queryset = Post.objects.all()
    serializer_class = PostSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly, IsAuthorOrReadOnly]


class PostLikeCreate(generics.CreateAPIView, mixins.DestroyModelMixin):
    serializer_class = PostReactionSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        self.this_post = get_object_or_404(Post, pk=self.kwargs['pk'])
        return PostReaction.objects.filter(author=self.request.user, post=self.this_post)

    def perform_create(self, serializer):
        react_object = self.get_queryset().first()
        if react_object:
            if react_object.isLike:
                raise ValidationError("You have already liked this post!")
            else:
                react_object.isLike = True
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
    permission_classes = [permissions.IsAuthenticated]

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


class CommentListCreate(generics.ListCreateAPIView):
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]
    filter_backends = [filters.OrderingFilter]
    ordering_fields = ['created_at', 'likes']
    pagination_class = CommentPagination

    def get_queryset(self):
        post = get_object_or_404(Post, pk=self.kwargs['pk'])
        queryset = Comment.objects.filter(post=post)
        queryset = queryset.annotate(
            likes=Count('commentreaction', filter=Q(commentreaction__isLike=True)) - Count('commentreaction', filter=Q(
                commentreaction__isLike=False))
        )
        return queryset

    def get_serializer_class(self):
        if self.request.method == 'POST':
            return CommentCreateSerializer
        return CommentRetrieveSerializer

    def perform_create(self, serializer):
        post = get_object_or_404(Post, pk=self.kwargs['pk'])
        serializer.save(author=self.request.user, post=post)


class CommentRetrieveDestroy(generics.RetrieveDestroyAPIView):
    serializer_class = CommentRetrieveSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly, IsAuthorOrReadOnly]

    def get_queryset(self):
        try:
            queryset = Comment.objects.filter(pk=self.kwargs['pk'])
            queryset = queryset.annotate(
                likes=Count('commentreaction', filter=Q(commentreaction__isLike=True)) - Count('commentreaction',
                                                                                               filter=Q(
                                                                                                   commentreaction__isLike=False))
            )
        except Comment.DoesNotExist:
            raise Http404('Comment does not exist')
        return queryset


class CommentLikeCreate(generics.CreateAPIView, mixins.DestroyModelMixin):
    serializer_class = CommentReactionSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        self.comment = Comment.objects.get(pk=self.kwargs['pk'])
        return CommentReaction.objects.filter(author=self.request.user, comment=self.comment)

    def perform_create(self, serializer):
        react_object = self.get_queryset().first()
        if react_object:
            if react_object.isLike:
                raise ValidationError("You have already liked this comment!")
            else:
                react_object.isLike = True
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
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        self.comment = Comment.objects.get(pk=self.kwargs['pk'])
        return CommentReaction.objects.filter(author=self.request.user, comment=self.comment)

    def perform_create(self, serializer):
        react_object = self.get_queryset().first()
        if react_object:
            if not react_object.isLike:
                raise ValidationError("You have already disliked this comment!")
            else:
                react_object.isLike = False
                react_object.save()
        else:
            serializer.save(author=self.request.user, comment=self.comment, isLike=False)

    def delete(self, request, *args, **kwargs):
        deleted_react_count, _ = self.get_queryset().delete()
        if deleted_react_count != 0:
            return Response(status=status.HTTP_204_NO_CONTENT)
        else:
            raise ValidationError("You never disliked this comment!")


class UserProfileUpdate(generics.UpdateAPIView):
    serializer_class = UserProfileSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return UserProfile.objects.filter(user=self.request.user)

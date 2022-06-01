from django.http import Http404
from django.shortcuts import get_object_or_404, render
from django.db.models import Count, Q
from django.contrib.auth import get_user_model
from rest_framework import generics, permissions, mixins, status, filters, serializers
from rest_framework.views import APIView
from rest_framework.exceptions import ValidationError
from rest_framework.response import Response
from dj_rest_auth.registration.views import RegisterView as DefaultRegisterView
from drf_spectacular.utils import extend_schema, inline_serializer
from mainapp.pagination import CommentPagination, PostPagination
from mainapp.utils import generate_and_send_activation_code

from .models import ActivationCode, Post, PostReaction, Comment, CommentReaction
from .serializers import ActivationCodeSerializer, CommentCreateSerializer, PasswordResetConfirmByPhoneActivationCodeSerializer, PostSerializer, PostReactionSerializer, CommentRetrieveSerializer, CommentReactionSerializer
from .permissions import IsAuthorOrReadOnly
import requests
from persiantools.jdatetime import JalaliDate


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

            
class SendPhonenumberActivationCode(APIView):
    @extend_schema(
        request=inline_serializer(
           name='phone_number',
           fields={
               'phone_number': serializers.CharField(),
           }
        )
    )
    def post(self, request, *args, **kwargs):
        try:
            user = get_user_model().objects.get(phone_number=request.data.get('phone_number'))
        except get_user_model().DoesNotExist:
            raise ValidationError({'message': 'This phone number doesn\'nt exist!'})
        if user.activationcode_set.exists() and user.activationcode_set.first().is_fresh():
            raise ValidationError({'message': 'Cannot send new activation code within 120 seconds!'})
        generate_and_send_activation_code(user)
        return Response({'message': 'Activation code has been sent!'})

class ActivatePhonenumber(generics.GenericAPIView):
    serializer_class = ActivationCodeSerializer

    def post(self, request, *args, **kwargs):
        activation_code_serializer = self.get_serializer(data=request.data)
        if activation_code_serializer.is_valid():
            phone_number = activation_code_serializer.validated_data['phone_number']
            code = activation_code_serializer.validated_data['code']
            try:
                activation_code_object = ActivationCode.objects.get(user__phone_number=phone_number, code=code)
                if not activation_code_object.is_fresh():
                    raise ActivationCode.DoesNotExist
            except ActivationCode.DoesNotExist as e:
                raise ValidationError({'message': 'The activation code is invalid or expired!'})
            
            activation_code_object.user.is_phone_number_activated = True
            activation_code_object.user.save()
            activation_code_object.delete()
            return Response({'message': 'User activated successfully.'})
        else:
            raise ValidationError({'message': activation_code_serializer.errors})


class PasswordResetConfirmByPhoneActivationCode(generics.GenericAPIView):
    serializer_class = PasswordResetConfirmByPhoneActivationCodeSerializer

    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response({'detail': 'New password has been saved.'})
        
class RegisterView(DefaultRegisterView):
    def get_response_data(self, user):
        return {'detail': 'User registered successfully!'}

    def perform_create(self, serializer):
        user = serializer.save(self.request)
        email = user.emailaddress_set.first()
        if email:
            email.send_confirmation()
        return user

class DayOccasions(APIView):
    def get(self, request):
        day = JalaliDate.today().day
        month = JalaliDate.today().month
        year = JalaliDate.today().year
        api_url = "http://persiancalapi.ir/jalali/{year}/{month}/{day}".format(year=year, month=month, day=day)
        response = requests.get(api_url)
        dayOccasions = response.json()
        return Response(dayOccasions)

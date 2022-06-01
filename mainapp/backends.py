from django.contrib.auth.backends import ModelBackend
from django.forms import ValidationError
from .models import User
from allauth.account.auth_backends import AuthenticationBackend

class EmailOrPhoneModelBackend(AuthenticationBackend):

    def user_can_authenticate(self, user):
        email = user.emailaddress_set.first()
        if (email and not email.verified) or (user.phone_number and not user.is_phone_number_activated):
            raise ValidationError('User is not activated!')
        return super().user_can_authenticate(user)

    def authenticate(self, request, username=None, password=None):
        if '@' in username:
            kwargs = {'email': username}
        else:
            kwargs = {'phone_number': username}
        try:
            user = User.objects.get(**kwargs)
            if user.check_password(password) and self.user_can_authenticate(user):
                return user
        except User.DoesNotExist:
            return None

    def get_user(self, user_id):
        try:
            return User.objects.get(pk=user_id)
        except User.DoesNotExist:
            return None

from random import randint
from django.db.models.signals import post_save, pre_save
from django.dispatch import receiver

from mainapp.models import ActivationCode, Comment, User
from django.core.mail import send_mail
from .utils import generate_and_send_activation_code

@receiver(post_save, sender=Comment)
def send_email_notification_for_comment(sender, instance, created, **kwargs):
    msg = f"""
        <h3>You have a new comment on your post ("{instance.post.title}").</h3> <br>
        <br>
        <b>{instance.author.username}</b> wrote: <br>
        <p><i>{instance.content}</i></p>
    """
    send_mail(
        subject='Germezit: You have a new comment',
        message="",
        html_message=msg,
        from_email=None,
        recipient_list=[instance.post.author.email],
    )

@receiver(pre_save, sender=User)
def send_activation_code(sender, instance: User, **kwargs):
    if instance.id is not None:
        previous = User.objects.get(id=instance.id)
        if previous.phone_number != instance.phone_number:
            generate_and_send_activation_code(instance)

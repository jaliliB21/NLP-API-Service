from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver
from channels.layers import get_channel_layer
from asgiref.sync import async_to_sync

from .models import CustomUser


@receiver(post_save, sender=CustomUser)
def announce_user_change(sender, instance, created, **kwargs):
    """
    Signal handler that is called every time a CustomUser object is saved.
    It broadcasts a message to the 'users_updates' group.
    """
    channel_layer = get_channel_layer()
    
    # Prepare the data to be sent
    user_data = {
        'id': instance.id,
        'username': instance.username,
        'email': instance.email,
        'full_name': instance.full_name,
        'email_verified': instance.is_email_verified,
    }
    
    message = {
        'action': 'created' if created else 'updated',
        'user': user_data,
    }

    # Send the message to the group
    async_to_sync(channel_layer.group_send)(
        'users_updates',
        {
            'type': 'user.update', # This corresponds to the method name in the consumer
            'message': message
        }
    )


@receiver(post_delete, sender=CustomUser)
def announce_user_deletion(sender, instance, **kwargs):
    """
    Signal handler that is called every time a CustomUser object is deleted.
    """
    channel_layer = get_channel_layer()
    
    message = {
        'action': 'deleted',
        'user_id': instance.id, # For deletion, we just need the ID
    }

    # Send the message to the group
    async_to_sync(channel_layer.group_send)(
        'users_updates',
        {
            'type': 'user.update',
            'message': message
        }
    )
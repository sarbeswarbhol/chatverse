from django.db import models
from django.contrib.auth.models import User
from django.utils.text import slugify
from django.contrib.contenttypes.fields import GenericForeignKey
from django.contrib.contenttypes.models import ContentType
import uuid

# ------------------------
# Group Chat Room
# ------------------------

class GroupRoom(models.Model):
    ROOM_TYPE_CHOICES = (
        ('public', 'Public'),
        ('private', 'Private'),
    )

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=100, unique=True)
    slug = models.SlugField(unique=True, blank=True)
    description = models.TextField(blank=True)
    owner = models.ForeignKey(User, on_delete=models.CASCADE, related_name='owned_group_rooms')
    members = models.ManyToManyField(User, related_name='group_rooms', blank=True)
    room_type = models.CharField(max_length=10, choices=ROOM_TYPE_CHOICES, default='public')
    password = models.CharField(max_length=128, blank=True)
    is_deleted = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.name} ({self.room_type})"

# ------------------------
# Direct (1-on-1) Room
# ------------------------

class DirectRoom(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user1 = models.ForeignKey(User, on_delete=models.CASCADE, related_name='direct_chats_user1')
    user2 = models.ForeignKey(User, on_delete=models.CASCADE, related_name='direct_chats_user2')
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('user1', 'user2')

    def __str__(self):
        return f"Chat between {self.user1.username} & {self.user2.username}"

# ------------------------
# Message Model (Generic)
# ------------------------

class Message(models.Model):
    sender = models.ForeignKey(User, on_delete=models.CASCADE)
    content = models.TextField()
    is_deleted = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    # Generic relation to either GroupRoom or DirectRoom
    content_type = models.ForeignKey(ContentType, on_delete=models.CASCADE)
    object_id = models.UUIDField()
    room = GenericForeignKey('content_type', 'object_id')

    class Meta:
        ordering = ['created_at']

    def __str__(self):
        return f"[Message] {self.pk} by {self.sender.username}"

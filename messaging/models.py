from django.db import models
from django.utils import timezone
from accounts.models import User
from products.models import Product

NULL = {"null": True, "blank": True}


class Conversation(models.Model):
    """Conversation between users"""
    
    CONVERSATION_TYPES = [
        ('general', 'General'),
        ('product_inquiry', 'Product Inquiry'),
        ('order_support', 'Order Support'),
        ('technical_support', 'Technical Support'),
        ('complaint', 'Complaint'),
        ('suggestion', 'Suggestion'),
    ]
    
    # Participants
    participants = models.ManyToManyField(User, related_name='conversations')
    created_by = models.ForeignKey(User, on_delete=models.CASCADE, related_name='created_conversations')
    
    # Conversation details
    title = models.CharField(max_length=200, **NULL)
    conversation_type = models.CharField(max_length=20, choices=CONVERSATION_TYPES, default='general')
    product = models.ForeignKey(Product, on_delete=models.CASCADE, **NULL)
    
    # Status
    is_active = models.BooleanField(default=True)
    is_resolved = models.BooleanField(default=False)
    priority = models.CharField(max_length=10, choices=[
        ('low', 'Low'),
        ('medium', 'Medium'),
        ('high', 'High'),
        ('urgent', 'Urgent'),
    ], default='medium')
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    last_message_at = models.DateTimeField(**NULL)
    
    class Meta:
        ordering = ['-last_message_at', '-created_at']
    
    def __str__(self):
        return f"Conversation {self.id} - {self.title or 'No title'}"
    
    @property
    def unread_count(self):
        """Get unread message count for a specific user"""
        return self.messages.filter(is_read=False).count()
    
    def get_other_participant(self, user):
        """Get the other participant in a two-person conversation"""
        return self.participants.exclude(id=user.id).first()


class Message(models.Model):
    """Individual messages in conversations"""
    
    MESSAGE_TYPES = [
        ('text', 'Text'),
        ('image', 'Image'),
        ('file', 'File'),
        ('system', 'System'),
        ('order_update', 'Order Update'),
    ]
    
    conversation = models.ForeignKey(Conversation, on_delete=models.CASCADE, related_name='messages')
    sender = models.ForeignKey(User, on_delete=models.CASCADE, related_name='sent_messages')
    
    # Message content
    message_type = models.CharField(max_length=20, choices=MESSAGE_TYPES, default='text')
    content = models.TextField(**NULL)
    attachment_url = models.URLField(**NULL)
    attachment_name = models.CharField(max_length=255, **NULL)
    attachment_size = models.PositiveIntegerField(**NULL)
    
    # Message status
    is_read = models.BooleanField(default=False)
    is_edited = models.BooleanField(default=False)
    is_deleted = models.BooleanField(default=False)
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    read_at = models.DateTimeField(**NULL)
    
    class Meta:
        ordering = ['created_at']
    
    def __str__(self):
        return f"Message from {self.sender.email} in conversation {self.conversation.id}"
    
    def mark_as_read(self, user):
        """Mark message as read for a specific user"""
        if not self.is_read:
            self.is_read = True
            self.read_at = timezone.now()
            self.save()


class MessageReadStatus(models.Model):
    """Track read status of messages by users"""
    
    message = models.ForeignKey(Message, on_delete=models.CASCADE, related_name='read_status')
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='message_read_status')
    read_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        unique_together = ['message', 'user']
    
    def __str__(self):
        return f"{self.user.email} read message {self.message.id}"


class ConversationParticipant(models.Model):
    """Track participant status in conversations"""
    
    conversation = models.ForeignKey(Conversation, on_delete=models.CASCADE, related_name='participant_status')
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='conversation_participant_status')
    joined_at = models.DateTimeField(auto_now_add=True)
    left_at = models.DateTimeField(**NULL)
    is_active = models.BooleanField(default=True)
    last_read_at = models.DateTimeField(**NULL)
    
    class Meta:
        unique_together = ['conversation', 'user']
    
    def __str__(self):
        return f"{self.user.email} in conversation {self.conversation.id}"


# SupportTicket moved to accounts.models to avoid conflicts

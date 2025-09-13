from django.contrib import admin
from .models import Conversation, Message, MessageReadStatus, ConversationParticipant


@admin.register(Conversation)
class ConversationAdmin(admin.ModelAdmin):
    list_display = ['id', 'title', 'conversation_type', 'is_active', 'is_resolved', 'created_at']
    list_filter = ['conversation_type', 'is_active', 'is_resolved', 'created_at']
    search_fields = ['title', 'participants__email']
    readonly_fields = ['created_at', 'updated_at']


@admin.register(Message)
class MessageAdmin(admin.ModelAdmin):
    list_display = ['id', 'conversation', 'sender', 'message_type', 'is_read', 'created_at']
    list_filter = ['message_type', 'is_read', 'is_edited', 'created_at']
    search_fields = ['content', 'sender__email']


@admin.register(MessageReadStatus)
class MessageReadStatusAdmin(admin.ModelAdmin):
    list_display = ['message', 'user', 'read_at']
    list_filter = ['read_at']


@admin.register(ConversationParticipant)
class ConversationParticipantAdmin(admin.ModelAdmin):
    list_display = ['conversation', 'user', 'is_active', 'joined_at']
    list_filter = ['is_active', 'joined_at']


# SupportTicket moved to accounts.models

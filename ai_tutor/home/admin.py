from django.contrib import admin
from django.utils.html import format_html
from django.urls import reverse
from django.utils.safestring import mark_safe
from .models import Tool, LLMConfiguration, ChatSession, ChatMessage

@admin.register(Tool)
class ToolAdmin(admin.ModelAdmin):
    list_display = ['display_name', 'name', 'provider', 'tool_type', 'is_active', 'created_at']
    list_filter = ['provider', 'is_active', 'created_at']
    search_fields = ['name', 'display_name', 'description']
    readonly_fields = ['created_at', 'updated_at']

    fieldsets = (
        ('Informazioni Base', {
            'fields': ('name', 'display_name', 'description', 'is_active')
        }),
        ('Configurazione Tecnica', {
            'fields': ('provider', 'tool_type', 'configuration'),
            'description': 'Configurazione del tool per l\'API del provider'
        }),
        ('Metadati', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )

@admin.register(LLMConfiguration)
class LLMConfigurationAdmin(admin.ModelAdmin):
    list_display = [
        'name', 'provider', 'model_name', 'temperature', 'max_tokens',
        'is_active', 'is_default', 'created_at'
    ]
    list_filter = ['is_active', 'is_default', 'provider', 'created_at']
    search_fields = ['name', 'description', 'model_name', 'system_prompt']
    readonly_fields = ['created_at', 'updated_at']

    fieldsets = (
        ('Informazioni Base', {
            'fields': ('name', 'description', 'is_active', 'is_default')
        }),
        ('Configurazione LLM e API', {
            'fields': ('provider', 'model_name', 'api_key', 'base_url'),
            'description': 'Configurazione del provider e modello LLM'
        }),
        ('Tools Abilitati', {
            'fields': ('tools',),
            'description': 'Seleziona i tool da abilitare (es: web search, code interpreter). I tool devono essere compatibili con il provider selezionato.'
        }),
        ('Contesto e Prompt', {
            'fields': ('system_prompt', 'additional_context'),
            'description': 'Definisci il comportamento e le informazioni aggiuntive per l\'AI'
        }),
        ('Parametri del Modello', {
            'fields': (
                'temperature', 'max_tokens', 'top_p',
                'frequency_penalty', 'presence_penalty'
            ),
            'description': 'Parametri per controllare il comportamento del modello'
        }),
        ('Parametri Avanzati', {
            'fields': ('model_parameters', 'stream', 'timeout', 'retry_attempts'),
            'classes': ('collapse',),
            'description': 'Parametri specifici del modello e configurazioni tecniche'
        }),
        ('Metadati', {
            'fields': ('created_by', 'created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )

    filter_horizontal = ['tools']  # Interfaccia migliore per ManyToMany

    def save_model(self, request, obj, form, change):
        if not change:  # Se è un nuovo oggetto
            obj.created_by = request.user
        super().save_model(request, obj, form, change)

class ChatMessageInline(admin.TabularInline):
    model = ChatMessage
    extra = 0
    readonly_fields = ['timestamp', 'tokens_used']
    fields = ['role', 'content', 'timestamp', 'tokens_used']
    
    def has_add_permission(self, request, obj=None):
        return False  # I messaggi vengono creati automaticamente

@admin.register(ChatSession)
class ChatSessionAdmin(admin.ModelAdmin):
    list_display = ['session_id', 'user', 'configuration', 'message_count', 'created_at']
    list_filter = ['configuration', 'created_at', 'user']
    search_fields = ['session_id', 'user__username', 'configuration__name']
    readonly_fields = ['session_id', 'created_at', 'updated_at']
    inlines = [ChatMessageInline]
    
    def message_count(self, obj):
        count = obj.messages.count()
        return format_html('<span style="color: blue;">{}</span>', count)
    message_count.short_description = "Messaggi"
    
    fieldsets = (
        ('Informazioni Sessione', {
            'fields': ('session_id', 'user', 'configuration')
        }),
        ('Metadati', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )

@admin.register(ChatMessage)
class ChatMessageAdmin(admin.ModelAdmin):
    list_display = ['session', 'role', 'content_short', 'tokens_used', 'timestamp']
    list_filter = ['role', 'timestamp', 'session__configuration']
    search_fields = ['content', 'session__session_id']
    readonly_fields = ['timestamp']
    
    def content_short(self, obj):
        return obj.content[:100] + "..." if len(obj.content) > 100 else obj.content
    content_short.short_description = "Contenuto"
    
    fieldsets = (
        ('Messaggio', {
            'fields': ('session', 'role', 'content', 'tokens_used', 'timestamp')
        }),
    )
    
    def has_add_permission(self, request, obj=None):
        return False  # I messaggi vengono creati automaticamente

# Configurazione del sito admin
admin.site.site_header = "AI Tutor - Pannello Amministrazione"
admin.site.site_title = "AI Tutor Admin"
admin.site.index_title = "Gestione Sistema AI Tutor"

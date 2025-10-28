from django.db import models
from django.contrib.auth.models import User
from django.core.validators import MinValueValidator, MaxValueValidator
import json

class Tool(models.Model):
    """Tool disponibili per i modelli LLM (web search, code interpreter, file search, etc.)"""

    # Informazioni base
    name = models.CharField(
        max_length=100,
        unique=True,
        help_text="Nome identificativo del tool (es: web_search, code_interpreter)"
    )
    display_name = models.CharField(
        max_length=200,
        help_text="Nome visualizzato nell'admin (es: Web Search, Code Interpreter)"
    )
    description = models.TextField(
        help_text="Descrizione delle funzionalità del tool"
    )

    # Configurazione tecnica
    provider = models.CharField(
        max_length=100,
        choices=[
            ('openai', 'OpenAI'),
            ('anthropic', 'Anthropic'),
            ('google', 'Google'),
            ('universal', 'Universale'),
        ],
        default='universal',
        help_text="Provider che supporta questo tool"
    )

    tool_type = models.CharField(
        max_length=100,
        help_text="Tipo di tool per l'API (es: 'web_search', 'code_interpreter', 'file_search')"
    )

    # Configurazione JSON per parametri specifici del tool
    configuration = models.JSONField(
        default=dict,
        blank=True,
        help_text="Configurazione specifica del tool in formato JSON. Es: {'type': 'web_search'} per OpenAI"
    )

    # Stato
    is_active = models.BooleanField(
        default=True,
        help_text="Tool attivo e disponibile per l'uso"
    )

    # Metadati
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.display_name} ({self.provider})"

    class Meta:
        verbose_name = "Tool"
        verbose_name_plural = "Tools"
        ordering = ['provider', 'display_name']

class LLMConfiguration(models.Model):
    """Configurazione unificata per LLM - include modello, API, contesto e parametri"""

    # Informazioni base
    name = models.CharField(max_length=200, help_text="Nome della configurazione")
    description = models.TextField(blank=True, help_text="Descrizione della configurazione")

    # Configurazione LLM e API
    provider = models.CharField(
        max_length=100,
        choices=[
            ('openai', 'OpenAI'),
            ('anthropic', 'Anthropic'),
            ('google', 'Google'),
            ('custom', 'Custom'),
        ],
        default='openai',
        help_text="Provider del servizio LLM"
    )
    model_name = models.CharField(
        max_length=200,
        help_text="Nome del modello (es: gpt-4, claude-3-opus, gemini-pro)"
    )
    api_key = models.CharField(
        max_length=500,
        help_text="API Key per il provider"
    )
    base_url = models.URLField(
        blank=True,
        null=True,
        help_text="URL base personalizzato per l'API (opzionale)"
    )

    # Contesto e prompt di sistema
    system_prompt = models.TextField(
        blank=True,
        help_text="Prompt di sistema per definire il comportamento dell'AI"
    )
    additional_context = models.TextField(
        blank=True,
        help_text="Informazioni aggiuntive da includere nel contesto (dati, regole, conoscenze)"
    )

    # Parametri del modello (valori comuni)
    temperature = models.FloatField(
        default=0.7,
        validators=[MinValueValidator(0.0), MaxValueValidator(2.0)],
        help_text="Controlla la creatività (0.0 = deterministico, 2.0 = molto creativo)"
    )
    max_tokens = models.IntegerField(
        default=512,
        validators=[MinValueValidator(1), MaxValueValidator(128000)],
        help_text="Numero massimo di token nella risposta"
    )
    top_p = models.FloatField(
        default=1.0,
        validators=[MinValueValidator(0.0), MaxValueValidator(1.0)],
        help_text="Controlla la diversità delle risposte (nucleus sampling)"
    )

    # Parametri specifici per alcuni provider
    frequency_penalty = models.FloatField(
        default=0.0,
        validators=[MinValueValidator(-2.0), MaxValueValidator(2.0)],
        help_text="Penalità per la ripetizione (OpenAI)"
    )
    presence_penalty = models.FloatField(
        default=0.0,
        validators=[MinValueValidator(-2.0), MaxValueValidator(2.0)],
        help_text="Penalità per introdurre nuovi argomenti (OpenAI)"
    )

    # Parametri avanzati specifici del modello (JSON)
    model_parameters = models.JSONField(
        default=dict,
        blank=True,
        help_text="Parametri aggiuntivi specifici del modello (formato JSON). Es: top_k, stop_sequences, etc."
    )

    # Configurazioni tecniche
    stream = models.BooleanField(
        default=True,
        help_text="Abilita streaming delle risposte"
    )
    timeout = models.IntegerField(
        default=30,
        help_text="Timeout in secondi"
    )
    retry_attempts = models.IntegerField(
        default=3,
        help_text="Numero di tentativi in caso di errore"
    )

    # Stato e metadati
    is_active = models.BooleanField(default=True)
    is_default = models.BooleanField(default=False, help_text="Configurazione predefinita")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    created_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)

    # Tools abilitati per questa configurazione
    tools = models.ManyToManyField(
        Tool,
        blank=True,
        related_name='configurations',
        help_text="Tool abilitati per questa configurazione (es: web search, code interpreter)"
    )

    def __str__(self):
        return f"{self.name} ({self.provider}: {self.model_name})"

    def get_full_context(self):
        """Restituisce il contesto completo (system_prompt + additional_context)"""
        context_parts = []

        if self.system_prompt:
            context_parts.append(self.system_prompt)

        if self.additional_context:
            context_parts.append("\n\nInformazioni aggiuntive:")
            context_parts.append(self.additional_context)

        return "\n".join(context_parts) if context_parts else ""

    def get_api_parameters(self):
        """Restituisce tutti i parametri per la richiesta API al LLM"""
        # Parametri base comuni a tutti i provider
        params = {
            'model': self.model_name,
            'temperature': self.temperature,
            'max_tokens': self.max_tokens,
            'top_p': self.top_p,
            'stream': self.stream,
        }

        # Aggiungi parametri specifici OpenAI se applicabili
        if self.provider == 'openai':
            params['frequency_penalty'] = self.frequency_penalty
            params['presence_penalty'] = self.presence_penalty

        # Aggiungi parametri personalizzati dal campo JSON
        if self.model_parameters:
            params.update(self.model_parameters)

        return params

    def get_client_config(self):
        """Restituisce la configurazione per il client API"""
        config = {
            'api_key': self.api_key,
            'timeout': self.timeout,
        }

        if self.base_url:
            config['base_url'] = self.base_url

        return config

    def get_tools(self):
        """Restituisce i tools attivi formattati per l'API del provider"""
        active_tools = self.tools.filter(is_active=True)

        if not active_tools.exists():
            return []

        tools_list = []
        for tool in active_tools:
            # Filtra solo i tool compatibili con il provider
            if tool.provider not in [self.provider, 'universal']:
                continue

            # Formato specifico per provider
            if self.provider == 'openai':
                # OpenAI usa il formato: {"type": "web_search"} o {"type": "code_interpreter"}
                tool_config = tool.configuration.copy() if tool.configuration else {}
                if 'type' not in tool_config:
                    tool_config['type'] = tool.tool_type
                tools_list.append(tool_config)
            elif self.provider == 'anthropic':
                # Anthropic potrebbe avere formato diverso
                tools_list.append({
                    'name': tool.name,
                    'type': tool.tool_type,
                    **(tool.configuration or {})
                })
            else:
                # Formato generico
                tools_list.append({
                    'type': tool.tool_type,
                    **(tool.configuration or {})
                })

        return tools_list

    def save(self, *args, **kwargs):
        # Se questa è la configurazione predefinita, rimuovi il flag dalle altre
        if self.is_default:
            LLMConfiguration.objects.filter(is_default=True).exclude(pk=self.pk).update(is_default=False)
        super().save(*args, **kwargs)

    class Meta:
        verbose_name = "Configurazione LLM"
        verbose_name_plural = "Configurazioni LLM"
        ordering = ['-is_default', '-created_at']

class ChatSession(models.Model):
    """Sessioni di chat per tracciare le conversazioni"""
    user = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True)
    configuration = models.ForeignKey(LLMConfiguration, on_delete=models.CASCADE)
    session_id = models.CharField(max_length=100, unique=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    # Sistema Agenti - Tracking dello stato
    agent_phase = models.CharField(
        max_length=50,
        choices=[
            ('analyze', 'Analisi iniziale'),
            ('interview', 'Raccolta informazioni'),
            ('data_collection', 'Raccolta dati'),
            ('refine', 'Raffinamento'),
            ('validate', 'Validazione'),
            ('complete', 'Completato'),
        ],
        default='analyze',
        help_text="Fase corrente del sistema agenti"
    )
    collected_info = models.JSONField(
        default=dict,
        blank=True,
        help_text="Informazioni raccolte durante il dialogo (obiettivo, contesto, vincoli, formato output, etc.)"
    )
    identified_issues = models.JSONField(
        default=list,
        blank=True,
        help_text="Lista di problemi identificati nel prompt iniziale"
    )
    iteration_count = models.IntegerField(
        default=0,
        help_text="Numero di iterazioni di raffinamento"
    )
    confidence_score = models.FloatField(
        default=0.0,
        validators=[MinValueValidator(0.0), MaxValueValidator(100.0)],
        help_text="Punteggio di confidence (0-100) sulla completezza delle informazioni raccolte"
    )

    def __str__(self):
        return f"Chat {self.session_id} - {self.configuration.name} [{self.agent_phase}] ({self.confidence_score:.0f}%)"

    class Meta:
        verbose_name = "Sessione Chat"
        verbose_name_plural = "Sessioni Chat"

class ChatMessage(models.Model):
    """Messaggi delle conversazioni"""
    session = models.ForeignKey(ChatSession, on_delete=models.CASCADE, related_name='messages')
    role = models.CharField(max_length=20, choices=[
        ('user', 'Utente'),
        ('assistant', 'Assistente'),
        ('system', 'Sistema'),
    ])
    content = models.TextField()
    timestamp = models.DateTimeField(auto_now_add=True)
    tokens_used = models.IntegerField(null=True, blank=True, help_text="Token utilizzati per questo messaggio")
    
    def __str__(self):
        return f"{self.role}: {self.content[:50]}..."
    
    class Meta:
        ordering = ['timestamp']
        verbose_name = "Messaggio Chat"
        verbose_name_plural = "Messaggi Chat"

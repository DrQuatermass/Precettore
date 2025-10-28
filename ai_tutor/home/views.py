from django.shortcuts import render, get_object_or_404
from django.http import StreamingHttpResponse, JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator
from django.views import View
import json
import logging
import uuid
from openai import OpenAI
from .models import LLMConfiguration, ChatSession, ChatMessage
from .agent_prompts import get_agent_prompt

# Configura logging
logger = logging.getLogger(__name__)

# ============================================================================
# SISTEMA AGENTI - Funzioni Helper
# ============================================================================

def calculate_confidence_score(collected_info, agent_phase):
    """
    Calcola un punteggio di confidence (0-100) basato sulle informazioni raccolte.

    Args:
        collected_info: Dict con informazioni raccolte
        agent_phase: Fase corrente dell'agente

    Returns:
        float: Punteggio 0-100
    """
    score = 0.0

    # Pesi per ogni tipo di informazione
    weights = {
        'obiettivo': 35.0,      # CRITICO - senza questo non si può fare nulla
        'contesto': 25.0,       # IMPORTANTE - definisce lo scenario
        'vincoli': 20.0,        # UTILE - migliora qualità
        'output_format': 10.0,  # UTILE - struttura la risposta
        'role': 10.0            # OPZIONALE - affina il tono
    }

    # Calcola score base sulle info presenti
    for key, weight in weights.items():
        if collected_info.get(key):
            # Aggiungi peso base
            score += weight

            # Bonus per risposte dettagliate (> 20 caratteri)
            if len(str(collected_info[key])) > 20:
                score += weight * 0.2  # +20% se dettagliata

    # Penalità se siamo in fasi avanzate ma manca l'obiettivo
    if agent_phase in ['refine', 'validate'] and not collected_info.get('obiettivo'):
        score *= 0.3  # Penalità del 70%

    # Bonus progressivo per numero di informazioni diverse
    info_count = sum(1 for v in collected_info.values() if v)
    if info_count >= 4:
        score += 10  # Bonus per completezza
    elif info_count >= 3:
        score += 5

    # Cap a 100
    return min(score, 100.0)


def get_confidence_thresholds():
    """
    Restituisce le soglie di confidence per le transizioni di fase.

    Returns:
        dict: Soglie per ogni transizione
    """
    return {
        'interview_to_refine': 20.0,     # Minimo per iniziare a raffinare
        'refine_to_validate': 65.0,      # Buona base per validare
        'validate_to_complete': 80.0,    # Alta confidence per completare
        'force_interview': 40.0,         # Sotto questa soglia, torna sempre a intervista
    }


def determine_next_phase(session, user_message):
    """
    Determina la prossima fase del sistema agenti basandosi sullo stato della sessione,
    sul confidence score e sulla qualità del prompt.

    Il sistema è ADATTIVO: salta fasi non necessarie se il prompt è già buono.

    Args:
        session: ChatSession object
        user_message: Messaggio dell'utente

    Returns:
        str: Prossima fase ('analyze', 'interview', 'data_collection', 'refine', 'validate', 'complete')
    """
    current_phase = session.agent_phase
    collected_info = session.collected_info
    iteration_count = session.iteration_count
    confidence = session.confidence_score

    # Ottieni le soglie di confidence
    thresholds = get_confidence_thresholds()

    # Prima interazione: sempre analisi
    if current_phase == 'analyze' and iteration_count == 0:
        return 'analyze'

    # Dopo l'analisi: DECISIONE INTELLIGENTE basata sul confidence iniziale
    if current_phase == 'analyze' and iteration_count > 0:
        # Se il prompt iniziale è già molto buono (>= 80%), salta direttamente a validate
        if confidence >= thresholds['validate_to_complete']:
            logger.info(f"⚡ Skip to validate: prompt già ottimo (confidence={confidence:.1f}%)")
            return 'validate'

        # Se il prompt è buono (>= 65%), salta direttamente a refine
        if confidence >= thresholds['refine_to_validate']:
            logger.info(f"⚡ Skip to refine: prompt già buono (confidence={confidence:.1f}%)")
            return 'refine'

        # Se ha già obiettivo chiaro ma manca dettagli (40-65%), vai a data_collection
        if confidence >= thresholds['force_interview'] and collected_info.get('obiettivo'):
            logger.info(f"⚡ Go to data_collection: obiettivo chiaro, servono dati (confidence={confidence:.1f}%)")
            return 'data_collection'

        # Altrimenti inizia con l'intervista per capire obiettivi/contesto
        logger.info(f"📋 Start interview: prompt vago (confidence={confidence:.1f}%)")
        return 'interview'

    # Se siamo in intervista: decidi se servono dati specifici o se possiamo raffinare
    if current_phase == 'interview':
        # Se abbiamo obiettivo chiaro ma confidence bassa: servono dati
        if collected_info.get('obiettivo') and confidence < thresholds['refine_to_validate']:
            return 'data_collection'
        # Se confidence è già buona: raffina direttamente
        if confidence >= thresholds['refine_to_validate']:
            logger.info(f"⚡ Skip data_collection: info sufficienti (confidence={confidence:.1f}%)")
            return 'refine'
        # Altrimenti continua intervista
        return 'interview'

    # Se siamo in data_collection: dopo la risposta utente, raffina
    if current_phase == 'data_collection':
        return 'refine'

    # Se siamo in raffinamento: decidi basandoti sul confidence score
    if current_phase == 'refine':
        # Se confidence è troppo bassa, torna a data_collection
        if confidence < thresholds['force_interview']:
            return 'data_collection'

        # Se abbiamo buona confidence, valida
        if confidence >= thresholds['refine_to_validate']:
            # Doppio check: deve avere almeno obiettivo
            if collected_info.get('obiettivo'):
                return 'validate'

        # Altrimenti continua a raccogliere dati
        return 'data_collection'

    # Se siamo in validazione: decidi basandoti su confidence e risposta utente
    if current_phase == 'validate':
        # Se l'utente chiede modifiche esplicite: torna a data_collection
        user_wants_changes = any(keyword in user_message.lower()
                                for keyword in ['modifica', 'cambia', 'aggiungi', 'togli', 'migliora', 'però', 'ma'])

        if user_wants_changes:
            return 'data_collection'

        # Se confidence è molto alta (>= 80) e utente non chiede modifiche: completa
        if confidence >= thresholds['validate_to_complete']:
            return 'complete'

        # Se confidence è media ma utente approva: completa
        user_approves = any(keyword in user_message.lower()
                           for keyword in ['ok', 'bene', 'perfetto', 'va bene', 'si', 'sì', 'ottimo', 'procedi'])

        if user_approves and confidence >= thresholds['refine_to_validate']:
            return 'complete'

        # Altrimenti chiedi ulteriori dettagli
        return 'data_collection'

    return current_phase


def extract_info_from_response(user_message, current_phase, collected_info, configuration):
    """
    Estrae informazioni strutturate dalla risposta dell'utente usando l'LLM stesso.
    Molto più accurato del semplice pattern matching.

    Args:
        user_message: Messaggio dell'utente
        current_phase: Fase corrente
        collected_info: Dict con info già raccolte
        configuration: LLMConfiguration per fare la chiamata di estrazione

    Returns:
        dict: Informazioni aggiornate
    """
    # Se è la prima risposta o una risposta molto breve, usa approccio semplificato
    if len(user_message.strip()) < 5:
        return collected_info.copy()

    # Costruisci un prompt di estrazione strutturata
    extraction_prompt = f"""Analizza la seguente risposta dell'utente e estrai informazioni strutturate per costruire un prompt ottimale.

RISPOSTA UTENTE:
"{user_message}"

INFORMAZIONI GIÀ RACCOLTE:
{json.dumps(collected_info, ensure_ascii=False, indent=2)}

COMPITO:
Identifica quale tipo di informazione fornisce l'utente e classificala in UNA di queste categorie:
- obiettivo: Lo scopo/task principale (es: "creare un articolo", "generare codice", "scrivere email")
- contesto: Scenario d'uso, pubblico target, background (es: "per studenti", "in ambito aziendale")
- vincoli: Limitazioni su lunghezza, tono, stile (es: "500 parole", "tono formale", "semplice")
- output_format: Formato della risposta desiderato (es: "lista puntata", "JSON", "markdown")
- role: Ruolo che l'AI dovrebbe assumere (es: "esperto di marketing", "tutor paziente")

Rispondi SOLO con un JSON in questo formato:
{{
  "category": "obiettivo|contesto|vincoli|output_format|role|nessuna",
  "value": "testo estratto dalla risposta utente (usa le sue parole, non parafrasare)",
  "confidence": 0.0-1.0
}}

REGOLE:
- Se la risposta non contiene info utili, usa category="nessuna"
- Mantieni il testo originale dell'utente in "value"
- Non inventare informazioni non presenti
- Se l'utente fornisce più info, priorità all'aspetto più rilevante"""

    try:
        # Chiama l'LLM per estrarre info
        client = OpenAI(api_key=configuration.api_key, timeout=10)

        response = client.chat.completions.create(
            model=configuration.model_name,
            messages=[
                {"role": "system", "content": "Sei un assistente che estrae informazioni strutturate. Rispondi SOLO con JSON valido."},
                {"role": "user", "content": extraction_prompt}
            ],
            temperature=0.3,  # Bassa temperatura per output più deterministico
            max_tokens=200
        )

        result_text = response.choices[0].message.content.strip()

        # Parse JSON response
        # Rimuovi eventuali markdown code blocks
        if result_text.startswith('```'):
            result_text = result_text.split('```')[1]
            if result_text.startswith('json'):
                result_text = result_text[4:]

        extraction_result = json.loads(result_text.strip())

        # Aggiorna collected_info se l'estrazione ha alta confidence
        updated_info = collected_info.copy()

        category = extraction_result.get('category', 'nessuna')
        value = extraction_result.get('value', '')
        confidence = extraction_result.get('confidence', 0.0)

        # Solo se confidence > 0.5 e categoria valida
        if confidence > 0.5 and category in ['obiettivo', 'contesto', 'vincoli', 'output_format', 'role']:
            if category == 'vincoli':
                # Per vincoli, aggiungi invece di sovrascrivere
                if updated_info.get('vincoli'):
                    updated_info['vincoli'] += ' | ' + value
                else:
                    updated_info['vincoli'] = value
            else:
                # Per altri campi, aggiorna solo se vuoto o se nuovo valore è più dettagliato
                if not updated_info.get(category) or len(value) > len(updated_info.get(category, '')):
                    updated_info[category] = value

        logger.info(f"Extraction: category={category}, confidence={confidence:.2f}, value_length={len(value)}")

        return updated_info

    except Exception as e:
        # Fallback: se l'estrazione LLM fallisce, usa approccio keyword semplificato
        logger.warning(f"LLM extraction failed: {str(e)}, using fallback keyword extraction")
        return extract_info_fallback(user_message, collected_info)


def extract_info_fallback(user_message, collected_info):
    """
    Fallback method: estrazione basata su keyword semplici.
    Usato solo se l'estrazione LLM fallisce.
    """
    updated_info = collected_info.copy()
    message_lower = user_message.lower()

    # Obiettivo
    if any(word in message_lower for word in ['creare', 'generare', 'scrivere', 'fare', 'produrre', 'voglio', 'vorrei']):
        if not updated_info.get('obiettivo'):
            updated_info['obiettivo'] = user_message

    # Contesto/Pubblico
    if any(word in message_lower for word in ['per', 'studenti', 'professionisti', 'bambini', 'utenti', 'clienti', 'pubblico']):
        if not updated_info.get('contesto'):
            updated_info['contesto'] = user_message

    # Vincoli (lunghezza, tono)
    if any(word in message_lower for word in ['parole', 'caratteri', 'paragrafi', 'breve', 'lungo',
                                               'formale', 'informale', 'tecnico', 'semplice']):
        if not updated_info.get('vincoli'):
            updated_info['vincoli'] = user_message
        else:
            updated_info['vincoli'] += ' | ' + user_message

    # Formato output
    if any(word in message_lower for word in ['lista', 'elenco', 'tabella', 'json', 'markdown', 'html']):
        if not updated_info.get('output_format'):
            updated_info['output_format'] = user_message

    # Ruolo
    if any(word in message_lower for word in ['esperto', 'tutor', 'assistente', 'consulente', 'come']):
        if not updated_info.get('role'):
            updated_info['role'] = user_message

    return updated_info


def build_agent_context(session, user_message=None):
    """
    Costruisce il contesto per l'agente corrente.

    Args:
        session: ChatSession object
        user_message: Messaggio corrente dell'utente (opzionale)

    Returns:
        dict: Contesto formattato per l'agente
    """
    # Trova il primo messaggio utente (prompt originale)
    original_message = session.messages.filter(role='user').first()
    original_prompt = original_message.content if original_message else "N/A"

    # Costruisci il prompt raffinato dalle info raccolte
    refined_prompt = build_refined_prompt(session.collected_info)

    context = {
        'original_prompt': original_prompt,
        'identified_issues': session.identified_issues,
        'collected_info': session.collected_info,
        'iteration_count': session.iteration_count,
        'refined_prompt': refined_prompt,
        'confidence_score': round(session.confidence_score, 1)
    }

    return context


def build_refined_prompt(collected_info):
    """
    Costruisce un prompt raffinato strutturato dalle informazioni raccolte.

    Args:
        collected_info: Dict con informazioni raccolte

    Returns:
        str: Prompt formattato
    """
    if not collected_info:
        return ""

    sections = []

    if collected_info.get('role'):
        sections.append(f"**Ruolo**: {collected_info['role']}")

    if collected_info.get('contesto'):
        sections.append(f"**Contesto**: {collected_info['contesto']}")

    if collected_info.get('obiettivo'):
        sections.append(f"**Obiettivo**: {collected_info['obiettivo']}")

    if collected_info.get('vincoli'):
        sections.append(f"**Vincoli**: {collected_info['vincoli']}")

    if collected_info.get('output_format'):
        sections.append(f"**Formato Output**: {collected_info['output_format']}")

    return "\n".join(sections)


# ============================================================================
# VIEWS
# ============================================================================

def homepage(request):
    """Mostra la pagina HTML per l'interfaccia LLM con configurazioni disponibili"""
    # Ottieni le configurazioni attive
    configurations = LLMConfiguration.objects.filter(is_active=True)
    context = {
        'configurations': configurations
    }
    return render(request, 'homepage.html', context)

@csrf_exempt
def llm_api(request):
    """API endpoint per le richieste LLM con configurazioni personalizzate"""
    if request.method != "POST":
        return JsonResponse({"error": "Metodo non consentito"}, status=405)

    try:
        data = json.loads(request.body)
        prompt = data.get("prompt", "")
        configuration_id = data.get("configuration_id")
        session_id = data.get("session_id")
        
        # Ottieni la configurazione
        if configuration_id:
            configuration = get_object_or_404(LLMConfiguration, id=configuration_id, is_active=True)
        else:
            # Usa la configurazione predefinita
            configuration = LLMConfiguration.objects.filter(is_default=True, is_active=True).first()
            if not configuration:
                configuration = LLMConfiguration.objects.filter(is_active=True).first()
                if not configuration:
                    return JsonResponse({"error": "Nessuna configurazione LLM disponibile"}, status=400)
        
        logger.info(f"Richiesta LLM: config={configuration.name}, prompt_length={len(prompt)}")

        # Gestisci la sessione di chat
        if session_id:
            try:
                session = ChatSession.objects.get(session_id=session_id)
            except ChatSession.DoesNotExist:
                session = None
        else:
            session = None
            
        if not session:
            session = ChatSession.objects.create(
                session_id=str(uuid.uuid4()),
                configuration=configuration,
                user=request.user if request.user.is_authenticated else None
            )

        def stream():
            try:
                # Invia session_id e fase agente come primo messaggio
                yield "data: " + json.dumps({
                    "session_id": session.session_id,
                    "content": "",
                    "agent_phase": session.agent_phase
                }) + "\n\n"

                # ============================================================================
                # SISTEMA AGENTI - Logica di orchestrazione
                # ============================================================================

                # Determina la fase successiva in base allo stato della sessione
                next_phase = determine_next_phase(session, prompt)

                # Estrai informazioni dalla risposta dell'utente (se non è la prima iterazione)
                if session.iteration_count > 0:
                    updated_info = extract_info_from_response(
                        prompt,
                        session.agent_phase,
                        session.collected_info,
                        configuration  # Passa la configurazione per l'estrazione LLM
                    )
                    session.collected_info = updated_info

                # Calcola il confidence score basato sulle info raccolte
                confidence = calculate_confidence_score(session.collected_info, next_phase)
                session.confidence_score = confidence

                # Incrementa il contatore di iterazioni
                session.iteration_count += 1

                # Aggiorna la fase
                session.agent_phase = next_phase
                session.save()

                # Log per debugging
                logger.info(f"Session {session.session_id}: Phase={next_phase}, Confidence={confidence:.1f}%, Info={list(session.collected_info.keys())}")

                # Invia aggiornamento di fase e confidence al frontend
                yield "data: " + json.dumps({
                    "agent_phase": next_phase,
                    "confidence_score": round(confidence, 1),
                    "content": ""
                }) + "\n\n"

                # Costruisci il contesto per l'agente
                agent_context = build_agent_context(session, prompt)

                # Ottieni il prompt specifico per l'agente corrente
                agent_system_prompt = get_agent_prompt(next_phase, agent_context)

                # ============================================================================
                # Prepara i messaggi per la conversazione
                # ============================================================================
                messages = []

                # Usa il prompt dell'agente come system message
                if agent_system_prompt:
                    messages.append({"role": "system", "content": agent_system_prompt})
                else:
                    # Fallback al contesto della configurazione
                    full_context = configuration.get_full_context()
                    if full_context:
                        messages.append({"role": "system", "content": full_context})

                # Aggiungi la cronologia della conversazione (ultimi 6 messaggi per mantenere contesto ma limitare token)
                previous_messages = session.messages.all().order_by('-timestamp')[:6]
                previous_messages = reversed(list(previous_messages))  # Riordina cronologicamente
                for msg in previous_messages:
                    messages.append({"role": msg.role, "content": msg.content})

                # Aggiungi il nuovo messaggio dell'utente
                messages.append({"role": "user", "content": prompt})

                # Salva il messaggio dell'utente
                user_message = ChatMessage.objects.create(
                    session=session,
                    role='user',
                    content=prompt
                )

                # Ottieni i parametri dalla configurazione
                params = configuration.get_api_parameters()
                client_config = configuration.get_client_config()

                # Ottieni i tools abilitati
                tools = configuration.get_tools()
                if tools:
                    params['tools'] = tools
                    logger.info(f"Tools abilitati per questa richiesta: {[t.get('type', t) for t in tools]}")

                # Configura il client OpenAI (supporta anche API custom)
                client = OpenAI(**client_config)

                response = client.chat.completions.create(
                    messages=messages,
                    **params
                )

                assistant_content = ""

                for chunk in response:
                    if chunk.choices and len(chunk.choices) > 0:
                        delta = chunk.choices[0].delta
                        if hasattr(delta, 'content') and delta.content:
                            assistant_content += delta.content
                            yield "data: " + json.dumps({"content": delta.content}) + "\n\n"

                # Salva la risposta dell'assistente
                if assistant_content:
                    ChatMessage.objects.create(
                        session=session,
                        role='assistant',
                        content=assistant_content
                    )

                yield "data: [DONE]\n\n"

            except Exception as e:
                logger.error(f"Errore durante streaming: {str(e)}")
                yield "data: " + json.dumps({"content": f"Errore: {str(e)}"}) + "\n\n"
                yield "data: [DONE]\n\n"

        return StreamingHttpResponse(stream(), content_type="text/event-stream")
        
    except json.JSONDecodeError:
        logger.error("Errore parsing JSON")
        return JsonResponse({"error": "JSON non valido"}, status=400)
    except Exception as e:
        logger.error(f"Errore generico: {str(e)}")
        return JsonResponse({"error": str(e)}, status=500)

def get_configurations(request):
    """API endpoint per ottenere le configurazioni disponibili"""
    configurations = LLMConfiguration.objects.filter(is_active=True).values(
        'id', 'name', 'description', 'provider', 'model_name'
    )
    return JsonResponse(list(configurations), safe=False)

def get_session_history(request, session_id):
    """API endpoint per ottenere la cronologia di una sessione"""
    try:
        session = ChatSession.objects.get(session_id=session_id)
        messages = session.messages.all().order_by('timestamp').values(
            'role', 'content', 'timestamp'
        )
        return JsonResponse(list(messages), safe=False)
    except ChatSession.DoesNotExist:
        return JsonResponse({"error": "Sessione non trovata"}, status=404)

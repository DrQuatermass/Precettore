#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Script per popolare il database con tools predefiniti
"""
import os
import sys
import django
from pathlib import Path

# Fix encoding for Windows console
if sys.platform == 'win32':
    import io
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8')

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'ai_tutor.settings')
django.setup()

from home.models import Tool

def create_tools():
    """Crea tools predefiniti per OpenAI"""
    
    print("Creazione tools predefiniti...")
    
    # 1. Web Search (OpenAI)
    web_search, created = Tool.objects.get_or_create(
        name="web_search",
        defaults={
            'display_name': 'Web Search',
            'description': 'Permette al modello di effettuare ricerche sul web per trovare informazioni aggiornate',
            'provider': 'openai',
            'tool_type': 'web_search',
            'configuration': {'type': 'web_search'},
            'is_active': True
        }
    )
    print(f"  {'✓ Creato' if created else '  Esistente'}: {web_search.display_name}")
    
    # 2. Code Interpreter (OpenAI)
    code_interpreter, created = Tool.objects.get_or_create(
        name="code_interpreter",
        defaults={
            'display_name': 'Code Interpreter',
            'description': 'Permette al modello di eseguire codice Python e lavorare con file',
            'provider': 'openai',
            'tool_type': 'code_interpreter',
            'configuration': {'type': 'code_interpreter'},
            'is_active': True
        }
    )
    print(f"  {'✓ Creato' if created else '  Esistente'}: {code_interpreter.display_name}")
    
    # 3. File Search (OpenAI)
    file_search, created = Tool.objects.get_or_create(
        name="file_search",
        defaults={
            'display_name': 'File Search',
            'description': 'Permette al modello di cercare e analizzare contenuti nei file caricati',
            'provider': 'openai',
            'tool_type': 'file_search',
            'configuration': {'type': 'file_search'},
            'is_active': True
        }
    )
    print(f"  {'✓ Creato' if created else '  Esistente'}: {file_search.display_name}")
    
    print("\n✅ Tools creati con successo!")
    print("\n📋 Tools disponibili:")
    for tool in Tool.objects.filter(is_active=True):
        print(f"  • {tool.display_name} ({tool.provider})")
        print(f"    └─ {tool.description}")

if __name__ == "__main__":
    create_tools()

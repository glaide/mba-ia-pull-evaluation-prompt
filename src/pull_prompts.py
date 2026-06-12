"""
Script para fazer pull de prompts do LangSmith Prompt Hub.

Este script:
1. Conecta ao LangSmith usando credenciais do .env
2. Faz pull dos prompts do Hub
3. Salva localmente em prompts/bug_to_user_story_v1.yml

SIMPLIFICADO: Usa serialização nativa do LangChain para extrair prompts.
"""

import os
import sys
from pathlib import Path
from dotenv import load_dotenv
from langchain import hub
from langsmith import Client  # Interação com LangSmith API

from utils import save_yaml, check_env_vars, print_section_header

load_dotenv()

PROMPTS_TO_PULL = [
    "bug_to_user_story_v1",
]


def pull_prompts_from_langsmith():
    client = Client()
    output_dir = Path("prompts")
    output_dir.mkdir(exist_ok=True)

    for prompt_name in PROMPTS_TO_PULL:
        print(f"Pulling prompt: {prompt_name}")
        prompt = client.pull_prompt(prompt_name)
             
        # Serialização nativa do LangChain
        prompt_data = prompt.to_json()

        output_file = output_dir / f"{prompt_name}.yml"

        save_yaml(prompt_data, output_file)

        print(f"Saved: {output_file}")


def main():
    """Função principal"""
    print_section_header("Pulling prompts from LangSmith")
    try:
        pull_prompts_from_langsmith()
        return 0
    except Exception as e:
        print(f"Error: {e}")
        return 1



if __name__ == "__main__":
    sys.exit(main())

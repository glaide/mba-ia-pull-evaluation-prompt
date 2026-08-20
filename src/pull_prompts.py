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
from langsmith import Client

from utils import save_yaml, check_env_vars, print_section_header

load_dotenv()

PROMPT_NAME = "bug_to_user_story_v1"
OUTPUT_FILE = Path("prompts_teste") / f"{PROMPT_NAME}.yml"


def pull_prompts_from_langsmith():
    username = os.getenv("USERNAME_LANGSMITH_HUB", "")
    hub_prompt_name = f"{username}/{PROMPT_NAME}"

    print(f"Pulling prompt: {hub_prompt_name}")
    client = Client()
    prompt = client.pull_prompt(
        hub_prompt_name,
        dangerously_pull_public_prompt=True,
    )
    save_yaml(prompt.to_json(), OUTPUT_FILE)
    print(f"Saved: {OUTPUT_FILE}")


def main():
    print_section_header("Pulling prompts from LangSmith")
    if not check_env_vars(["LANGSMITH_API_KEY", "USERNAME_LANGSMITH_HUB"]):
        return 1
    try:
        pull_prompts_from_langsmith()
        return 0
    except Exception as e:
        print(f"Error: {e}")
        return 1


if __name__ == "__main__":
    sys.exit(main())
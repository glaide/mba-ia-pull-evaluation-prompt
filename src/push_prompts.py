"""
Script para fazer push de prompts otimizados ao LangSmith Prompt Hub.

Este script:
1. Lê os prompts otimizados de prompts/bug_to_user_story_v2.yml
2. Valida os prompts
3. Faz push PÚBLICO para o LangSmith Hub
4. Adiciona metadados (tags, descrição, técnicas utilizadas)

SIMPLIFICADO: Código mais limpo e direto ao ponto.
"""

import os
import sys
from pathlib import Path

from dotenv import load_dotenv
from langchain_classic import hub
from langchain_core.prompts import ChatPromptTemplate
from utils import (
    load_yaml,
    check_env_vars,
    print_section_header,
    validate_prompt_structure,
)

load_dotenv()

PROMPT_KEY = "bug_to_user_story_v2"
PROMPT_NAME = "bug_to_user_story_v2"
INPUT_FILE = Path("prompts") / f"{PROMPT_NAME}.yml"


def _build_tags(prompt_data: dict) -> list[str]:
    tags = list(prompt_data.get("tags", []))
    for technique in prompt_data.get("techniques_applied", []):
        if technique not in tags:
            tags.append(technique)
    return tags


def _build_readme(prompt_data: dict) -> str:
    description = prompt_data.get("description", "")
    version = prompt_data.get("version", "")
    techniques = prompt_data.get("techniques_applied", [])

    lines = [description, "", f"Version: {version}", "", "Techniques applied:"]
    lines.extend(f"- {technique}" for technique in techniques)
    return "\n".join(lines)


def validate_prompt(prompt_data: dict) -> tuple[bool, list]:
    """
    Valida estrutura básica de um prompt (versão simplificada).

    Args:
        prompt_data: Dados do prompt

    Returns:
        (is_valid, errors) - Tupla com status e lista de erros
    """
    is_valid, errors = validate_prompt_structure(prompt_data)

    user_prompt = prompt_data.get("user_prompt", "").strip()
    if not user_prompt:
        errors.append("user_prompt está vazio")

    system_prompt = prompt_data.get("system_prompt", "")
    combined = f"{system_prompt}\n{user_prompt}"
    if "{bug_report}" not in combined:
        errors.append("system_prompt ou user_prompt deve conter a variável {bug_report}")

    if "TODO" in user_prompt:
        errors.append("user_prompt ainda contém TODOs")

    return (len(errors) == 0, errors)


def push_prompt_to_langsmith(prompt_name: str, prompt_data: dict) -> bool:
    """
    Faz push do prompt otimizado para o LangSmith Hub (PÚBLICO).

    Args:
        prompt_name: Nome do prompt
        prompt_data: Dados do prompt

    Returns:
        True se sucesso, False caso contrário
    """
    username = os.getenv("USERNAME_LANGSMITH_HUB", "")
    hub_prompt_name = f"{username}/{prompt_name}"

    try:
        prompt_template = ChatPromptTemplate.from_messages([
            ("system", prompt_data["system_prompt"]),
            ("human", prompt_data["user_prompt"]),
        ])

        print(f"Pushing prompt: {hub_prompt_name}")
        url = hub.push(
            hub_prompt_name,
            prompt_template,
            new_repo_is_public=True,
            new_repo_description=prompt_data.get("description", ""),
            tags=_build_tags(prompt_data),
            readme=_build_readme(prompt_data),
        )
        print(f"Pushed: {url}")
        return True

    except Exception as e:
        print(f"Error: {e}")
        return False


def main():
    """Função principal"""
    print_section_header("Pushing optimized prompts to LangSmith")
    if not check_env_vars(["LANGSMITH_API_KEY", "USERNAME_LANGSMITH_HUB"]):
        return 1

    raw = load_yaml(str(INPUT_FILE))
    if not raw:
        return 1

    prompt_data = raw.get(PROMPT_KEY, raw)

    is_valid, errors = validate_prompt(prompt_data)
    if not is_valid:
        print("Validation errors:")
        for err in errors:
            print(f"  - {err}")
        return 1

    success = push_prompt_to_langsmith(PROMPT_NAME, prompt_data)
    return 0 if success else 1


if __name__ == "__main__":
    sys.exit(main())

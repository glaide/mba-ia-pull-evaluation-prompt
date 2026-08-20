"""
Testes automatizados para validação de prompts.
"""
import pytest
import yaml
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from utils import validate_prompt_structure

PROMPT_FILE = Path(__file__).parent.parent / "prompts" / "bug_to_user_story_v2.yml"
PROMPT_KEY = "bug_to_user_story_v2"


def load_prompts(file_path: str):
    with open(file_path, "r", encoding="utf-8") as f:
        return yaml.safe_load(f)


def get_v2_prompt():
    data = load_prompts(str(PROMPT_FILE))
    return data[PROMPT_KEY]


class TestPrompts:
    def test_prompt_has_system_prompt(self):
        prompt = get_v2_prompt()
        assert "system_prompt" in prompt
        assert prompt["system_prompt"].strip()

    def test_prompt_has_role_definition(self):
        prompt = get_v2_prompt()
        system_prompt = prompt["system_prompt"]
        assert "Você é um" in system_prompt
        assert "Product Owner" in system_prompt

    def test_prompt_mentions_format(self):
        prompt = get_v2_prompt()
        system_prompt = prompt["system_prompt"]
        assert "História de Usuário" in system_prompt
        assert "**Título:**" in system_prompt
        assert "Critérios de Aceite" in system_prompt

    def test_prompt_has_few_shot_examples(self):
        prompt = get_v2_prompt()
        system_prompt = prompt["system_prompt"]
        assert "Exemplo 1 — Entrada:" in system_prompt
        assert "Exemplo 1 — Saída:" in system_prompt
        assert "Exemplo 2 — Entrada:" in system_prompt
        assert "Exemplo 2 — Saída:" in system_prompt

    def test_prompt_no_todos(self):
        prompt = get_v2_prompt()
        combined = f"{prompt.get('system_prompt', '')}\n{prompt.get('user_prompt', '')}"
        assert "TODO" not in combined
        assert "[TODO]" not in combined

    def test_minimum_techniques(self):
        prompt = get_v2_prompt()
        techniques = prompt.get("techniques_applied", [])
        assert len(techniques) >= 2
        is_valid, errors = validate_prompt_structure(prompt)
        assert is_valid, errors


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])

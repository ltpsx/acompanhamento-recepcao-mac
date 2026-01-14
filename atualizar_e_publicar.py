#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Script de automação para atualizar e publicar o acompanhamento MAC
Pode ser executado manualmente ou via n8n/cron
"""

import subprocess
import sys
import io
import json
from datetime import datetime
from pathlib import Path

# Configurar stdout para UTF-8
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')

# Configurações
REPO_DIR = Path(__file__).parent
SCRIPT_NAME = "gerar_acompanhamento.py"
HTML_FILE = "Acompanhamento_recepcao_mac.html"
TIMESTAMP_FILE = ".ultima_atualizacao.json"


def log(message):
    """Imprime mensagem com timestamp"""
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    print(f"[{timestamp}] {message}")


def run_command(command, description):
    """Executa um comando e retorna o resultado"""
    log(f"{description}...")
    try:
        result = subprocess.run(
            command,
            cwd=REPO_DIR,
            shell=True,
            capture_output=True,
            text=True,
            check=True
        )
        log(f"✓ {description} - Sucesso")
        return True, result.stdout
    except subprocess.CalledProcessError as e:
        log(f"✗ {description} - Erro: {e.stderr}")
        return False, e.stderr


def main():
    log("=== Iniciando atualização do Acompanhamento MAC ===")

    # Mostrar informações sobre a última verificação
    timestamp_path = REPO_DIR / TIMESTAMP_FILE
    if timestamp_path.exists():
        try:
            timestamp_data = json.loads(timestamp_path.read_text(encoding="utf-8"))
            log(f"Última verificação: {timestamp_data.get('ultima_verificacao', 'N/A')}")
            log(f"Última atualização com mudanças: {timestamp_data.get('ultima_atualizacao', 'N/A')}")
        except:
            pass

    # 1. Gerar novo HTML
    success, output = run_command(
        f"python {SCRIPT_NAME}",
        "Gerando HTML atualizado"
    )
    if not success:
        log("Erro ao gerar HTML. Abortando.")
        sys.exit(1)

    # 2. Verificar se o HTML tem mudanças
    log("Verificando mudanças no HTML...")
    result = subprocess.run(
        f"git diff --exit-code {HTML_FILE}",
        cwd=REPO_DIR,
        shell=True,
        capture_output=True
    )

    # Se exit code = 0, não há mudanças
    if result.returncode == 0:
        log("✓ Nenhuma mudança detectada nos dados. Script rodou com sucesso.")
        sys.exit(0)
    else:
        log("✓ Mudanças detectadas nos dados, criando commit...")

    # 3. Adicionar arquivos ao git (HTML e JSON de timestamp)
    success, _ = run_command(
        f"git add {HTML_FILE} {TIMESTAMP_FILE}",
        "Adicionando arquivos ao Git"
    )
    if not success:
        log("Erro ao adicionar arquivos. Abortando.")
        sys.exit(1)

    # 4. Fazer commit
    commit_msg = f"Atualização automática - {datetime.now().strftime('%d/%m/%Y %H:%M')}"
    success, _ = run_command(
        f'git commit -m "{commit_msg}"',
        "Criando commit"
    )
    if not success:
        log("Erro ao criar commit. Abortando.")
        sys.exit(1)

    # 5. Fazer push
    success, _ = run_command(
        "git push",
        "Enviando para GitHub"
    )
    if not success:
        log("Erro ao fazer push. Abortando.")
        sys.exit(1)

    log("=== Atualização concluída com sucesso! ===")
    log(f"Site será atualizado em: https://ltpsx.github.io/acompanhamento-recepcao-mac/{HTML_FILE}")
    sys.exit(0)


if __name__ == "__main__":
    main()

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
import time
from datetime import datetime
from pathlib import Path

# Configurar stdout para UTF-8
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')

# Configurações
REPO_DIR = Path(__file__).parent
SCRIPT_NAME = "gerar_acompanhamento.py"
HTML_FILE = "Acompanhamento_recepcao_mac.html"
TIMESTAMP_FILE = ".ultima_atualizacao.json"
LOG_FILE = REPO_DIR / "atualizar_e_publicar.log"


def log(message):
    """Imprime mensagem com timestamp e salva em arquivo"""
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    log_message = f"[{timestamp}] {message}"
    print(log_message)

    # Também salva em arquivo para diagnóstico
    try:
        with open(LOG_FILE, "a", encoding="utf-8") as f:
            f.write(log_message + "\n")
    except:
        pass  # Não falhar se não conseguir escrever log


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

    # 0. Sincronizar com remote antes de começar (pull)
    log("Sincronizando com repositório remoto...")
    result = subprocess.run(
        "git pull --rebase",
        cwd=REPO_DIR,
        shell=True,
        capture_output=True,
        text=True
    )
    if result.returncode != 0:
        # Se falhar o pull, pode ser porque não há conexão ou não há mudanças
        error_lower = result.stderr.lower()
        log(f"⚠ Pull falhou (pode ser normal): {result.stderr.strip()}")

        # Verifica se é erro de conexão
        if "could not resolve host" in error_lower or "failed to connect" in error_lower:
            log("⚠ Sem conexão com GitHub. Continuando mesmo assim...")
        # Verifica se é porque tem mudanças locais (não é problema)
        elif "unstaged changes" in error_lower or "uncommitted changes" in error_lower:
            log("✓ Mudanças locais detectadas, continuando normalmente...")
        # Verifica se é conflito real
        elif "conflict" in error_lower:
            log("✗ ERRO: Conflito detectado no repositório!")
            log("Execute 'git status' e resolva os conflitos manualmente.")
            sys.exit(1)
        else:
            log("⚠ Erro desconhecido no pull, mas continuando...")
    else:
        log("✓ Sincronização bem-sucedida")

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

    # 5. Fazer push com retry
    max_retries = 3
    retry_count = 0
    push_success = False

    while retry_count < max_retries and not push_success:
        if retry_count > 0:
            log(f"Tentativa {retry_count + 1} de {max_retries}...")
            # Tenta sincronizar novamente antes do retry
            subprocess.run("git pull --rebase", cwd=REPO_DIR, shell=True, capture_output=True)

        success, error_msg = run_command(
            "git push",
            "Enviando para GitHub"
        )

        if success:
            push_success = True
        else:
            retry_count += 1
            if retry_count < max_retries:
                log(f"⚠ Tentativa falhou. Tentando novamente em 2 segundos...")
                time.sleep(2)

    if not push_success:
        log("✗ Erro ao fazer push após múltiplas tentativas.")
        log("⚠ O commit foi criado localmente mas não foi enviado ao GitHub.")
        log("Execute 'git push' manualmente quando houver conexão.")
        sys.exit(1)

    log("=== Atualização concluída com sucesso! ===")
    log(f"Site será atualizado em: https://ltpsx.github.io/acompanhamento-recepcao-mac/{HTML_FILE}")
    sys.exit(0)


if __name__ == "__main__":
    main()

# Integração com n8n - Acompanhamento MAC

Este guia explica como configurar a automação completa usando n8n para atualizar automaticamente o sistema de acompanhamento.

## 📋 Visão Geral

O workflow do n8n irá:
1. Executar automaticamente em intervalos definidos
2. Gerar o HTML atualizado com os dados das planilhas
3. Fazer commit e push para o GitHub
4. O GitHub Pages atualiza o site automaticamente
5. (Opcional) Enviar notificações sobre o status

## 🚀 Opções de Automação

### Opção 1: Script Python Simples (Recomendado para Iniciantes)

Execute manualmente ou com agendador do Windows:

```bash
python atualizar_e_publicar.py
```

**Agendar no Windows Task Scheduler:**
1. Abra o Agendador de Tarefas
2. Criar Tarefa Básica
3. Nome: "Atualizar Acompanhamento MAC"
4. Gatilho: Diariamente às 8h, 14h e 18h
5. Ação: Iniciar um programa
   - Programa: `python`
   - Argumentos: `atualizar_e_publicar.py`
   - Iniciar em: `C:\Users\compr\OneDrive\Recepção e Conferência de Mercadorias`

### Opção 2: n8n (Recomendado para Automação Avançada)

## 🔧 Configuração do n8n

### Passo 1: Instalar n8n

```bash
# Via NPM (Node.js necessário)
npm install -g n8n

# Ou via Docker
docker run -it --rm --name n8n -p 5678:5678 n8nio/n8n
```

### Passo 2: Importar Workflow

1. Acesse n8n: http://localhost:5678
2. Clique em "Import from File"
3. Selecione o arquivo `n8n-workflow.json`
4. O workflow será importado com todos os nós configurados

### Passo 3: Configurar os Nós

#### 1. Schedule Trigger (Agendador)

**Configuração padrão:** A cada 30 minutos
```cron
*/30 * * * *
```

**Outras opções:**
- A cada 15 minutos: `*/15 * * * *`
- A cada hora: `0 * * * *`
- A cada 2 horas: `0 */2 * * *`
- Diariamente às 8h: `0 8 * * *`
- Segunda a Sexta às 9h e 17h: `0 9,17 * * 1-5`

#### 2. Execute Python Script

**Comando:**
```bash
cd "C:\Users\compr\OneDrive\Recepção e Conferência de Mercadorias" && python gerar_acompanhamento.py
```

**Ajustes necessários:**
- Ajuste o caminho se necessário
- Certifique-se de que Python está no PATH

#### 3. Git Push

**Comando:**
```bash
cd "C:\Users\compr\OneDrive\Recepção e Conferência de Mercadorias" && git add Acompanhamento_recepcao_mac.html && git commit -m "Atualização automática" && git push
```

#### 4. Notificações (Opcional)

Você pode configurar notificações via:
- **Discord**: Webhook para canal
- **Telegram**: Bot + Chat ID
- **Email**: SMTP
- **Slack**: Webhook

**Exemplo Discord:**
1. Vá em Server Settings → Integrations → Webhooks
2. Crie um novo webhook
3. Copie a URL
4. No n8n, adicione no nó Discord

## 📊 Workflow Detalhado

```
┌─────────────────┐
│ Schedule Trigger│ → Executa no horário definido
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│  Run Python     │ → Gera HTML atualizado
│     Script      │    (gerar_acompanhamento.py)
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│   Git Commit    │ → Commit + Push para GitHub
│   and Push      │
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│ Check Success   │ → Verifica se teve sucesso
└────────┬────────┘
         │
    ┌────┴────┐
    ▼         ▼
┌────────┐ ┌────────┐
│Success │ │ Error  │ → Notificações
│ Alert  │ │ Alert  │
└────────┘ └────────┘
```

## 🔔 Configuração de Notificações

### Discord

1. Crie um Webhook no seu servidor Discord
2. No n8n, adicione nó "Discord"
3. Configure:
   - **Webhook URL**: Cole a URL do webhook
   - **Message**: Personalize a mensagem

**Exemplos de mensagens:**
```
✅ Acompanhamento MAC atualizado com sucesso!
📊 Total: {{$json["total"]}} itens
🟢 Prontas: {{$json["ready"]}}
🟡 Pendentes: {{$json["pending"]}}
🕐 {{$now.format("DD/MM/YYYY HH:mm")}}
```

### Telegram

1. Crie um bot com @BotFather
2. Obtenha o token
3. Obtenha seu Chat ID (use @userinfobot)
4. Configure no n8n:
   - **Token**: Token do bot
   - **Chat ID**: Seu chat ID

## 🐛 Troubleshooting

### Erro: Python não encontrado
**Solução**: Adicione Python ao PATH do sistema

### Erro: Git não encontrado
**Solução**: Instale Git e adicione ao PATH

### Erro: Permission denied (push)
**Solução**: Configure credenciais do Git
```bash
git config --global credential.helper wincred
```

### HTML não atualiza no GitHub Pages
**Solução**:
- Aguarde 2-5 minutos (delay do GitHub Pages)
- Limpe cache do navegador (Ctrl + F5)
- Verifique se o commit foi feito: https://github.com/ltpsx/acompanhamento-recepcao-mac/commits

## 📝 Logs e Monitoramento

### Ver logs do n8n
- Interface: Clique em "Executions" no menu lateral
- Cada execução mostra detalhes de sucesso/erro

### Ver logs do script Python
```bash
python atualizar_e_publicar.py > logs.txt 2>&1
```

## 🎯 Melhorias Futuras

1. **Backup automático**: Salvar cópia das planilhas antes de processar
2. **Validação de dados**: Verificar integridade antes de publicar
3. **Estatísticas por email**: Enviar resumo diário
4. **Alertas inteligentes**: Notificar sobre mercadorias pendentes há muito tempo
5. **Dashboard**: Criar dashboard com histórico de dados

## 📞 Suporte

- **GitHub Issues**: https://github.com/ltpsx/acompanhamento-recepcao-mac/issues
- **n8n Docs**: https://docs.n8n.io/
- **Python Docs**: https://docs.python.org/3/

---

🤖 Sistema criado com Claude Code

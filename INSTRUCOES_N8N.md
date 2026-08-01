# Instruções para Configurar Workflow n8n

## Problema Resolvido

O script `atualizar_e_publicar.py` agora está mais robusto e trata os seguintes problemas que causavam falhas intermitentes:

1. **Sincronização com repositório remoto** - Faz pull antes de começar
2. **Retry automático no push** - Tenta 3 vezes se falhar
3. **Tratamento de erros de conexão** - Não falha se estiver offline temporariamente
4. **Logs detalhados** - Salva logs em `atualizar_e_publicar.log` para diagnóstico
5. **Melhor tratamento de mudanças locais** - Não falha se houver arquivos modificados localmente

## Configuração no n8n

### Opção 1: Execute Node (Recomendado)

```json
{
  "command": "python",
  "args": ["atualizar_e_publicar.py"],
  "cwd": "C:\\Users\\compr\\OneDrive\\Recepção e Conferência de Mercadorias",
  "timeout": 60000
}
```

### Opção 2: Execute Command

```
cd "C:\Users\compr\OneDrive\Recepção e Conferência de Mercadorias" && python atualizar_e_publicar.py
```

## Schedule Recomendado

- **Intervalo**: A cada 30 minutos
- **Horário**: 08:00 - 18:00 (dias úteis)
- **Timezone**: America/Sao_Paulo

## Como Verificar Problemas

### 1. Verificar logs do script
```bash
cd "C:\Users\compr\OneDrive\Recepção e Conferência de Mercadorias"
type atualizar_e_publicar.log
```

### 2. Verificar status do repositório
```bash
cd "C:\Users\compr\OneDrive\Recepção e Conferência de Mercadorias"
git status
git log --oneline -5
```

### 3. Executar manualmente para testar
```bash
cd "C:\Users\compr\OneDrive\Recepção e Conferência de Mercadorias"
python atualizar_e_publicar.py
```

## Códigos de Saída

- **0**: Sucesso (com ou sem mudanças)
- **1**: Erro crítico (conflito, falha no commit, etc.)

O script agora NÃO falha por:
- Falta de conexão temporária
- Mudanças locais não commitadas em outros arquivos
- Falhas momentâneas no push (tenta 3 vezes)

## Estrutura de Arquivos

```
├── atualizar_e_publicar.py          # Script principal (ATUALIZADO)
├── gerar_acompanhamento.py          # Gera o HTML
├── Acompanhamento_recepcao_mac.html # HTML gerado
├── .ultima_atualizacao.json         # Timestamp da última atualização
├── atualizar_e_publicar.log         # Logs detalhados (não commitado)
└── INSTRUCOES_N8N.md                # Este arquivo
```

## Melhorias Implementadas

### 1. Sincronização Automática
Antes de gerar o HTML, o script tenta sincronizar com o repositório remoto usando `git pull --rebase`. Se falhar por motivos não críticos (mudanças locais, sem conexão), continua normalmente.

### 2. Retry no Push
Se o push falhar, o script tenta mais 2 vezes com intervalo de 2 segundos. Antes de cada retry, tenta fazer pull novamente.

### 3. Logs Persistentes
Todos os logs são salvos em `atualizar_e_publicar.log` para facilitar diagnóstico de problemas intermitentes.

### 4. Tratamento de Erros Inteligente
O script diferencia entre:
- **Erros críticos**: Conflitos no git → Aborta e pede intervenção manual
- **Erros recuperáveis**: Sem conexão, mudanças locais → Continua ou tenta novamente
- **Erros temporários**: Falha no push → Retry automático

## Configuração no n8n (Detalhada)

### Node: Schedule Trigger
```
Mode: Every X
Value: 30
Unit: Minutes
```

### Node: Execute Command (com tratamento de erro)

**Command:**
```
python atualizar_e_publicar.py
```

**Working Directory:**
```
C:\Users\compr\OneDrive\Recepção e Conferência de Mercadorias
```

**Options:**
- Timeout: 60000 (60 segundos)
- Continue On Fail: false (queremos saber quando falha de verdade)

### Node: Error Handler (Opcional)

Se quiser receber notificação quando falhar:

**IF Node:**
- Condition: `{{ $json.code }} !== 0`

**Then: Send Email/Slack/Telegram**
- Assunto: "Erro na atualização do Acompanhamento MAC"
- Mensagem: `{{ $json.stderr }}`

## Solução de Problemas Comuns

### Problema: "You have unstaged changes"
**Solução**: Normal, o script agora trata isso automaticamente.

### Problema: "could not resolve host"
**Solução**: Normal se estiver offline temporariamente. O commit é criado localmente e será enviado na próxima execução.

### Problema: "conflict"
**Solução**: REQUER INTERVENÇÃO MANUAL
```bash
cd "C:\Users\compr\OneDrive\Recepção e Conferência de Mercadorias"
git status
git pull --rebase
# Resolver conflitos manualmente
git add .
git rebase --continue
```

### Problema: Script não detecta mudanças mas deveria
**Solução**: Verificar se o arquivo HTML foi realmente modificado
```bash
cd "C:\Users\compr\OneDrive\Recepção e Conferência de Mercadorias"
python gerar_acompanhamento.py
git diff Acompanhamento_recepcao_mac.html
```

## Monitoramento

Para monitorar a saúde do sistema, verifique periodicamente:

1. **Frequência de commits**: Deve ter commits regulares quando há mudanças
   ```bash
   git log --oneline --since="1 day ago"
   ```

2. **Tamanho do arquivo de log**: Se crescer muito, pode indicar muitos erros
   ```bash
   cd "C:\Users\compr\OneDrive\Recepção e Conferência de Mercadorias"
   dir atualizar_e_publicar.log
   ```

3. **Status do repositório**: Não deve ter commits pendentes por muito tempo
   ```bash
   git status
   ```

## Contato

Em caso de problemas persistentes, verifique:
1. O arquivo de log `atualizar_e_publicar.log`
2. O status do repositório com `git status`
3. A conectividade com GitHub
4. As credenciais do Git (se pedir senha toda vez, configure SSH)

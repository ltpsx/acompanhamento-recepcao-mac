# Sistema de Acompanhamento de Recepção MAC

Sistema de controle e acompanhamento de recepção e conferência de mercadorias para as lojas MAC (Araçatuba, Birigui e Presidente Prudente).

## 📋 Descrição

Este sistema consolida os dados de recepção de mercadorias das três lojas MAC e gera relatórios em Excel e HTML com interface moderna e interativa.

## 🎨 Características

- **Design Material Design 3**: Interface moderna com tons de preto, branco e cinza
- **Cores por Cidade**:
  - 🔵 Araçatuba - Azul
  - 🟢 Prudente - Verde
  - 🟠 Birigui - Laranja
- **Filtro por Cidade**: Selecione uma cidade específica ou visualize todas
- **Status Visual**: Indicadores de "Pronta para Venda" (quando FIN e LIB estão preenchidos) ou "Pendente"
- **Estatísticas em Tempo Real**: Total de itens, prontas e pendentes
- **Responsivo**: Funciona em desktop e mobile

## 📁 Estrutura de Arquivos

```
.
├── gerar_acompanhamento.py          # Script principal
├── Acompanhamento_recepcao_mac.html # Relatório HTML gerado
├── Acompanhamento_recepcao_mac.xlsx # Planilha consolidada
├── Mac Araçatuba Recepção e Conferência.xlsx
├── Mac Birigui Recepção e Conferência.xlsx
├── Mac Prudente Recepção e Conferência.xlsx
└── README.md
```

## 🚀 Como Usar

### Pré-requisitos

- Python 3.7 ou superior
- Pandas instalado (`pip install pandas openpyxl`)

### Executar

```bash
python gerar_acompanhamento.py
```

O script irá:
1. Ler as planilhas das três lojas
2. Consolidar os dados
3. Gerar `Acompanhamento_recepcao_mac.xlsx`
4. Gerar `Acompanhamento_recepcao_mac.html`

### Visualizar

Abra o arquivo `Acompanhamento_recepcao_mac.html` em qualquer navegador web.

## 📊 Colunas da Planilha

- **CIDADE**: Cidade da loja (Araçatuba, Birigui ou Prudente)
- **N.F.**: Número da Nota Fiscal
- **DATA**: Data de recepção
- **NOME DO FORNECEDOR**: Nome do fornecedor
- **FIN.**: Status de finalização
- **LIB.**: Status de liberação
- **STATUS**: Pronta para Venda (quando FIN e LIB estão preenchidos) ou Pendente

## 🔄 Atualização

Para atualizar o relatório com novos dados:
1. Atualize as planilhas das lojas
2. Execute novamente o script `python gerar_acompanhamento.py`
3. Atualize a página HTML no navegador

## 📝 Observações

- As planilhas Excel (.xlsx, .xlsm) não são versionadas no Git
- Apenas o código-fonte e os relatórios gerados são versionados
- A mercadoria está "Pronta para Venda" somente quando FIN. e LIB. estão ambos preenchidos

## 📄 Licença

Uso interno MAC Atacado.

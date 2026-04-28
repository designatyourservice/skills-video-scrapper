---
name: video-to-roteiro
description: Transcreve um arquivo de vídeo local em roteiro técnico detalhado em português, com câmera, enquadramento, iluminação, paleta de cores, descrição física de cenas/pessoas/objetos e timeframe de cada cena. Use quando o usuário pedir transcrição, roteiro, decupagem ou análise técnica de vídeo.
allowed-tools: Bash, Read, Write
argument-hint: <caminho-do-video> [arquivo-saida.md]
---

# video-to-roteiro

Esta skill envia um arquivo de vídeo local para a API Gemini do Google e gera um único arquivo `roteiro.md` em português do Brasil contendo um roteiro técnico cena-a-cena com:

- Timeframe (início/fim) de cada cena.
- Câmera inferida, lente, profundidade de campo e estabilização.
- Enquadramento e movimentos.
- Iluminação.
- Paleta de cores com hex aproximados.
- Descrição física de locais, pessoas e objetos.
- Falas literais e rubricas.

## Quando usar

Acione esta skill quando o usuário pedir:
- Transcrição/decupagem técnica de vídeo.
- Roteiro a partir de vídeo gravado.
- Análise de fotografia, enquadramento ou direção de arte de um vídeo.

## Como executar

Quando invocada, faça os passos abaixo em ordem.

### 1. Validar pré-requisitos

```bash
test -n "${GEMINI_API_KEY:-}" || { echo "ERRO: defina GEMINI_API_KEY (https://aistudio.google.com/apikey) antes de rodar."; exit 1; }
```

Se `GEMINI_API_KEY` não estiver definida, peça ao usuário para exportá-la e pare.

### 2. Validar argumentos

- `$0` deve apontar para um arquivo existente. Se não, mostre: `ERRO: arquivo de vídeo não encontrado: <caminho>`.
- `$1` é opcional; se ausente, use `roteiro.md` no diretório atual.

### 3. Instalar dependências (idempotente)

```bash
pip install -q -r "${CLAUDE_SKILL_DIR}/requirements.txt"
```

### 4. Processar o vídeo

```bash
python "${CLAUDE_SKILL_DIR}/scripts/process_video.py" "$0" "${1:-roteiro.md}"
```

O script faz upload via Files API, espera o estado `ACTIVE`, chama `gemini-2.5-pro` e grava o markdown no caminho de saída.

### 5. Confirmar e mostrar prévia

Após a execução bem-sucedida, leia as primeiras ~60 linhas do arquivo de saída e mostre ao usuário, em português, indicando o caminho completo do roteiro gerado.

## Erros comuns

- **`GEMINI_API_KEY` ausente** → pedir para exportar.
- **Arquivo > 2 GB** → orientar a comprimir/cortar o vídeo (limite da Files API).
- **Cota excedida / 429** → orientar a aguardar e tentar novamente.

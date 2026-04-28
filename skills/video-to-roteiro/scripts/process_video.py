#!/usr/bin/env python3
"""Envia um vídeo local para a API Gemini e grava um roteiro técnico em markdown (PT-BR)."""

from __future__ import annotations

import os
import sys
import time
from pathlib import Path

MAX_BYTES = 2 * 1024 * 1024 * 1024  # 2 GB, limite da Files API
MODEL = "gemini-2.5-pro"
POLL_INTERVAL_S = 3
POLL_TIMEOUT_S = 600

PROMPT = """Você é um diretor de fotografia e roteirista profissional brasileiro, com olhar técnico apurado. Analise o vídeo e produza UM roteiro técnico detalhado em markdown, em português do Brasil, no formato exato abaixo. Não adicione texto fora desse formato. Não use JSON.

# <título sugerido para o vídeo>

**Resumo:** <2-3 frases sobre o conteúdo geral>

**Estilo geral:** <documentário / publicidade / vlog / cinema / institucional / etc.>

---

## Cena 1 — [HH:MM:SS – HH:MM:SS]

**Câmera:** <tipo inferido: DSLR full-frame, smartphone, câmera cinema, GoPro, drone, etc.> · **Lente:** <grande angular ~24mm / normal ~50mm / tele ~85mm+, quando inferível> · **Profundidade de campo:** <rasa / profunda> · **Estabilização:** <tripé / gimbal / handheld>

**Enquadramento:** <plano geral / médio / close / primeiríssimo plano / plongée / contra-plongée / plano-detalhe> · **Movimento:** <fixo / pan / tilt / travelling / dolly / zoom>

**Iluminação:** <natural ou artificial; dura/suave; alta-chave/baixa-chave; contraluz/key/fill; hora do dia se exterior>

**Paleta de cores:** <tons dominantes em palavras + 3 a 5 hex aproximados, ex: âmbar quente #C8843C, verde-musgo #4A6B3A, creme #EFE3CA> · **Temperatura:** <quente / fria / neutra> · **Contraste:** <baixo/médio/alto>

**Local:** <descrição física do ambiente: materiais, mobília, dimensões, texturas, profundidade>

**Pessoas:** <para cada figura: idade aproximada, biotipo, vestuário em detalhe, cabelo, expressão, postura. Use PESSOA 1, PESSOA 2 se nome desconhecido>

**Objetos em destaque:** <itens visualmente relevantes: forma, cor, material, estado>

**Ação e diálogo:**
> [ação visual ou rubrica]
**NARRADOR:** fala literal...
**PESSOA 1 (tom emocional):** fala literal...

---

## Cena 2 — [HH:MM:SS – HH:MM:SS]
... (mesmo formato, e assim por diante até cobrir todo o vídeo)

Regras:
- Timestamps REAIS do vídeo, não inventados.
- Cubra o vídeo inteiro do início ao fim, sem lacunas entre cenas.
- Quando algo não for inferível com segurança, escreva "indeterminado" em vez de chutar.
- Hex de cores são aproximações visuais, não medições exatas.
- Falas devem ser transcrição literal (não resumo).
- Não inclua nenhum texto antes do título nem depois da última cena.
"""


def fail(msg: str, code: int = 1) -> "None":
    print(f"ERRO: {msg}", file=sys.stderr)
    sys.exit(code)


def main() -> None:
    if len(sys.argv) < 2:
        fail("uso: process_video.py <caminho-do-video> [arquivo-saida.md]")

    video_path = Path(sys.argv[1]).expanduser().resolve()
    output_path = Path(sys.argv[2] if len(sys.argv) > 2 else "roteiro.md").expanduser().resolve()

    api_key = os.environ.get("GEMINI_API_KEY")
    if not api_key:
        fail("variável de ambiente GEMINI_API_KEY não definida. Pegue uma chave em https://aistudio.google.com/apikey e exporte: export GEMINI_API_KEY=...")

    if not video_path.is_file():
        fail(f"arquivo de vídeo não encontrado: {video_path}")

    size = video_path.stat().st_size
    if size == 0:
        fail(f"arquivo de vídeo está vazio: {video_path}")
    if size > MAX_BYTES:
        fail(f"arquivo excede 2 GB ({size / 1024 / 1024:.1f} MB). Reduza/corte o vídeo antes de enviar.")

    try:
        from google import genai
        from google.genai import types
    except ImportError:
        fail("pacote google-genai não está instalado. Rode: pip install google-genai")

    client = genai.Client(api_key=api_key)

    print(f"[1/3] Enviando vídeo ({size / 1024 / 1024:.1f} MB) para a Files API...", file=sys.stderr)
    try:
        uploaded = client.files.upload(file=str(video_path))
    except Exception as e:
        fail(f"falha ao enviar o vídeo: {e}")

    print(f"[2/3] Aguardando processamento do arquivo {uploaded.name}...", file=sys.stderr)
    waited = 0
    while uploaded.state.name == "PROCESSING":
        if waited >= POLL_TIMEOUT_S:
            fail(f"tempo esgotado aguardando processamento do vídeo (>{POLL_TIMEOUT_S}s).")
        time.sleep(POLL_INTERVAL_S)
        waited += POLL_INTERVAL_S
        uploaded = client.files.get(name=uploaded.name)

    if uploaded.state.name != "ACTIVE":
        fail(f"upload terminou em estado inesperado: {uploaded.state.name}")

    print(f"[3/3] Gerando roteiro com {MODEL}...", file=sys.stderr)
    try:
        response = client.models.generate_content(
            model=MODEL,
            contents=[uploaded, PROMPT],
            config=types.GenerateContentConfig(temperature=0.3),
        )
    except Exception as e:
        fail(f"falha ao gerar o roteiro: {e}")

    text = (response.text or "").strip()
    if not text:
        fail("a API retornou conteúdo vazio.")

    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(text + "\n", encoding="utf-8")

    print(f"OK: roteiro gravado em {output_path}", file=sys.stderr)

    try:
        client.files.delete(name=uploaded.name)
    except Exception:
        pass


if __name__ == "__main__":
    main()

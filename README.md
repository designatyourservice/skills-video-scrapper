# skills-video-scrapper

Skill do Claude Code que transforma um arquivo de vídeo local em um roteiro técnico detalhado em português do Brasil, usando a API Gemini do Google.

A saída é um único arquivo markdown (`roteiro.md`) com decupagem cena-a-cena, contendo timeframe, câmera inferida, enquadramento, iluminação, paleta de cores (com hex aproximados), descrição física de pessoas/locais/objetos e falas literais.

## Pré-requisitos

- Python 3.10+
- Conta no [Google AI Studio](https://aistudio.google.com/apikey) com uma `GEMINI_API_KEY`
- Claude Code instalado

## Instalação

```bash
git clone <este-repo>
cd skills-video-scrapper
bash install.sh
```

`install.sh` cria um symlink em `~/.claude/skills/video-to-roteiro` apontando para a pasta versionada da skill, então atualizações via `git pull` propagam automaticamente.

Antes de usar, exporte sua chave:

```bash
export GEMINI_API_KEY="..."
```

## Uso

Dentro do Claude Code:

```
/video-to-roteiro caminho/para/video.mp4
```

ou com saída customizada:

```
/video-to-roteiro caminho/para/video.mp4 saida/roteiro_filme.md
```

Você também pode pedir em linguagem natural:

> Transcreva `entrevista.mp4` em roteiro técnico.

A skill será sugerida automaticamente.

## Limites

- Arquivo de vídeo ≤ 2 GB (limite da Files API do Gemini).
- Vídeos longos consomem mais cota — comece com clipes curtos.
- Modelo padrão: `gemini-2.5-pro`.

## Exemplo de saída (trecho)

```markdown
# Café da manhã na varanda

**Resumo:** Vlog matinal em uma casa de campo, com uma jovem preparando café e
conversando com a câmera enquanto observa o jardim.

**Estilo geral:** vlog / lifestyle

---

## Cena 1 — [00:00:00 – 00:00:08]

**Câmera:** smartphone moderno · **Lente:** grande angular ~24mm ·
**Profundidade de campo:** profunda · **Estabilização:** handheld

**Enquadramento:** plano geral · **Movimento:** pan lento da esquerda para a direita

**Iluminação:** natural, suave, hora dourada do amanhecer, contraluz parcial

**Paleta de cores:** dourados quentes e verdes saturados — âmbar #D9A05B,
verde-folha #5C7A3A, creme #F1E4C8 · **Temperatura:** quente · **Contraste:** médio

**Local:** varanda de madeira escura com vista para um jardim com árvores frutíferas...
```

## Estrutura do repositório

```
skills-video-scrapper/
├── README.md
├── install.sh
└── skills/
    └── video-to-roteiro/
        ├── SKILL.md
        ├── requirements.txt
        └── scripts/
            └── process_video.py
```

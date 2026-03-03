# Word Invaders

Jogo 2D em Python (Pygame) onde palavras em PT-BR e EN descem em direção ao solo. O jogador deve digitar a **primeira letra restante** de cada palavra para disparar automaticamente e remover letras.

## Requisitos

- Python 3.10+
- Dependências em `requirements.txt`

## Instalação

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

## Como executar

```bash
python main.py
```

## Controles

- Digite letras do teclado para atacar palavras
- `R`: reiniciar após Game Over
- `F11`: alternar entre janela e tela cheia
- Fechar janela: encerra o jogo

## Mecânica principal

- Palavras surgem no topo da tela e descem verticalmente
- O alvo da digitação é a primeira letra restante da palavra
- Ao acertar, um laser/projétil é desenhado do canhão até a palavra
- Ao errar, palavras ativas aceleram (penalidade)
- Se palavra atingir a base, perde vida
- Sem vidas: Game Over

## Dificuldade

- Nível aumenta por pontuação:
	- Nível 1: `score <= 20`
	- Nível 2: `score > 20`
	- Nível 3: `score > 50`
	- Nível 4: `score > 90`
- Progressão por nível (implementada em `game.py`):
	- Nível 1: até 1 palavra simultânea, spawn ~120 frames, tamanho 3-5
	- Nível 2: até 2 palavras simultâneas, spawn ~95 frames, tamanho 4-6
	- Nível 3: até 3 palavras simultâneas, spawn ~75 frames, tamanho 5-8
	- Nível 4+: até 4 palavras simultâneas, spawn ~60 frames, tamanho 6+
- A velocidade de queda base de novas palavras também cresce com o nível (`1 + level * 0.5`).
- Em erro de digitação, palavras ativas aceleram com multiplicador de velocidade (`x1.2`).
- As cores das palavras alternam no spawn entre laranja e azul.

## Estrutura do projeto

- `main.py`: ponto de entrada
- `game.py`: loop principal, estados do jogo, HUD, níveis e eventos
- `word.py`: classe de palavra (texto, estado, posição e renderização)
- `projectile.py`: efeito visual de disparo
- `loader_csv.py`: leitura e validação do CSV de palavras
- `base_100_palavras.csv`: base principal de palavras
- `assets/`: sprites, sons e fontes

## Formato do CSV

Cabeçalho esperado:

```csv
pt-br,len-pt-br,en,len-en
```

Regras aplicadas pelo carregador:

- `len-pt-br` deve bater com o tamanho de `pt-br`
- `len-en` deve bater com o tamanho de `en`
- Arquivo inexistente gera erro


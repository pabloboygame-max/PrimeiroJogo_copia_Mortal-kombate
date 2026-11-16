

# 1. IMPORTACAO DAS BIBLIOTECAS
import pygame
import sys
import math
import random
from array import array
from pathlib import Path
from menu_jogo import Jogo as MenuJogo, PERSONAGENS as PERSONAGENS_MENU

# 2. INICIALIZACAO DO PYGAME E CRIACAO DA JANELA
pygame.init()

LARGURA = 1000
ALTURA = 600
tela = pygame.display.set_mode((LARGURA, ALTURA))
pygame.display.set_caption("Arena Mortal - Prototipo de Luta")
relogio = pygame.time.Clock()


def criar_som_impacto(frequencia, duracao, volume):
    configuracao_audio = pygame.mixer.get_init()
    if configuracao_audio is None:
        return None

    taxa_amostragem = configuracao_audio[0]
    quantidade_amostras = int(taxa_amostragem * duracao)
    amostras = array("h")
    for indice in range(quantidade_amostras):
        envelope = 1 - indice / quantidade_amostras
        onda = 1 if math.sin(2 * math.pi * frequencia * indice / taxa_amostragem) >= 0 else -1
        amostras.append(int(32767 * volume * envelope * onda))
    return pygame.mixer.Sound(buffer=amostras.tobytes())


som_golpe = criar_som_impacto(115, 0.12, 0.28)
som_bloqueio = criar_som_impacto(430, 0.08, 0.18)

# 3. DEFINICAO DE CORES, FONTES E CONFIGURACOES
PRETO = (12, 10, 18)
BRANCO = (245, 245, 245)
VERMELHO = (190, 35, 45)
AZUL = (40, 110, 220)
AMARELO = (245, 190, 55)
CHAO = 445

fonte_titulo = pygame.font.SysFont("arial", 54, bold=True)
fonte_media = pygame.font.SysFont("arial", 30, bold=True)
fonte_normal = pygame.font.SysFont("arial", 22)
fonte_pequena = pygame.font.SysFont("arial", 16)
fonte_controles = pygame.font.SysFont("arial", 14)

# 4. CARREGAMENTO DOS SPRITES DO SCORPION
# Usa o caminho do projeto em vez do diretório atual do terminal.
BASE_DIR = Path(__file__).resolve().parent
pasta_sprites = BASE_DIR / "sprites" / "quadros_separados"
ALTURA_SPRITE = 145
LARGURA_COLISAO = 80


def preparar_sprite(imagem):
    """Recorta transparencia e redimensiona sem deformar o personagem."""
    if imagem is None:
        raise ValueError("Sprite nulo.")

    area_visivel = imagem.get_bounding_rect()
    if area_visivel.width <= 1 or area_visivel.height <= 1:
        raise ValueError("Sprite sem pixels visiveis.")

    imagem = imagem.subsurface(area_visivel).copy()
    altura = max(1, imagem.get_height())
    largura = max(1, round(imagem.get_width() * ALTURA_SPRITE / altura))
    return pygame.transform.smoothscale(imagem, (largura, ALTURA_SPRITE))


imagem_scorpion_principal = None

def carregar_quadro(numero):
    """Carrega um quadro do Scorpion. Se nao existir, retorna None."""
    caminho = pasta_sprites / f"quadro_{numero:03}.png"
    if not caminho.exists():
        return None

    try:
        imagem = pygame.image.load(str(caminho)).convert_alpha()
        return preparar_sprite(imagem)
    except (pygame.error, ValueError):
        print(f"Aviso: quadro do Scorpion invalido ou sem pixels visiveis: {caminho}")
        return None

def carregar_animacao(inicio, fim):
    """Carrega uma sequencia de quadros numerados."""
    quadros = []
    for numero in range(inicio, fim + 1):
        imagem = carregar_quadro(numero)
        if imagem is not None:
            quadros.append(imagem)
    return quadros

# 5. CARREGAMENTO DAS ANIMACOES
# Numeracao informada: parado 003-009, andando 010-018 e socos 039-058.
animacao_parado = carregar_animacao(3, 9)
animacao_andando = carregar_animacao(10, 18)
animacao_soco = carregar_animacao(39, 58)
imagem_scorpion_principal = animacao_parado[0] if animacao_parado else None

if not animacao_parado:
    print("Aviso: animacao do Scorpion nao encontrada; sera usado o lutador provisorio.")

pasta_sprites_subzero = BASE_DIR / "sprites" / "subzero_animacao"


def carregar_animacao_subzero(nome, quantidade):
    quadros = []
    for numero in range(quantidade):
        caminho = pasta_sprites_subzero / f"{nome}_{numero:02}.png"
        if not caminho.exists():
            raise FileNotFoundError(f"Quadro do Sub-Zero nao encontrado: {caminho}")
        imagem = pygame.image.load(str(caminho)).convert_alpha()
        try:
            quadros.append(preparar_sprite(imagem))
        except ValueError as erro:
            raise ValueError(f"Quadro do Sub-Zero sem pixels visiveis: {caminho}") from erro
    return quadros


animacao_subzero_parado = carregar_animacao_subzero("parado", 12)
animacao_subzero_andando = carregar_animacao_subzero("andando", 9)
animacao_subzero_soco = carregar_animacao_subzero("soco", 10)
animacao_subzero_pulo = carregar_animacao_subzero("pulo", 5)
animacao_subzero_dano = carregar_animacao_subzero("dano", 4)
animacao_subzero_defesa = carregar_animacao_subzero("defesa", 5)
animacao_subzero_especial = carregar_animacao_subzero("especial", 12)

pasta_sprites_liu = BASE_DIR / "sprites" / "liu_kang_animacao"


def carregar_animacao_liu(nome, quantidade):
    quadros = []
    for numero in range(quantidade):
        caminho = pasta_sprites_liu / f"{nome}_{numero:02}.png"
        if not caminho.exists():
            raise FileNotFoundError(f"Quadro do Liu Kang nao encontrado: {caminho}")
        imagem = pygame.image.load(str(caminho)).convert_alpha()
        try:
            quadros.append(preparar_sprite(imagem))
        except ValueError as erro:
            raise ValueError(f"Quadro do Liu Kang sem pixels visiveis: {caminho}") from erro
    return quadros


animacao_liu_parado = carregar_animacao_liu("parado", 8)
animacao_liu_andando = carregar_animacao_liu("andando", 9)
animacao_liu_soco = carregar_animacao_liu("soco", 9)
animacao_liu_chute = carregar_animacao_liu("chute", 7)

pasta_sprites_raiden = BASE_DIR / "sprites" / "raiden_animacao"


def carregar_animacao_raiden(nome, quantidade):
    quadros = []
    for numero in range(quantidade):
        caminho = pasta_sprites_raiden / f"{nome}_{numero:02}.png"
        if not caminho.exists():
            raise FileNotFoundError(f"Quadro do Raiden nao encontrado: {caminho}")
        imagem = pygame.image.load(str(caminho)).convert_alpha()
        try:
            quadros.append(preparar_sprite(imagem))
        except ValueError as erro:
            raise ValueError(f"Quadro do Raiden sem pixels visiveis: {caminho}") from erro
    return quadros


animacao_raiden_parado = carregar_animacao_raiden("parado", 10)
animacao_raiden_andando = carregar_animacao_raiden("andando", 9)
animacao_raiden_soco = carregar_animacao_raiden("soco", 5)
animacao_raiden_chute = carregar_animacao_raiden("chute", 7)
# Os quadros de raio do atlas cortam partes do lutador; os efeitos eletricos
# sao desenhados separadamente para manter a animacao do personagem consistente.
animacao_raiden_especial = animacao_raiden_soco + animacao_raiden_chute
animacao_ataque_raiden = animacao_raiden_soco + animacao_raiden_chute

# 6. CRIACAO DOS PERSONAGENS E VARIAVEIS DA PARTIDA
jogador1 = pygame.Rect(190, CHAO - ALTURA_SPRITE, LARGURA_COLISAO, ALTURA_SPRITE)
jogador2 = pygame.Rect(735, CHAO - ALTURA_SPRITE, LARGURA_COLISAO, ALTURA_SPRITE)
velocidade_vertical_jogador1 = 0.0
velocidade_vertical_jogador2 = 0.0
FORCA_PULO = -15
GRAVIDADE = 0.8
VELOCIDADE_JOGADOR1 = 5
VELOCIDADE_JOGADOR2 = 6

vida_jogador1 = 100
vida_jogador2 = 100

direcao_jogador1 = 1
direcao_jogador2 = -1
NOME_JOGADOR1 = "SCORPION"
NOME_JOGADOR2 = "SUB-ZERO"
modo_jogo = "dois"
cpu_tempo_decisao = 0
cpu_tempo_defesa = 0

indice_parado = 0
indice_andando = 0
indice_soco1 = 0
indice_soco2 = 0
indice_subzero_parado = 0
indice_subzero_andando = 0
indice_subzero_pulo = 0
indice_subzero_defesa = 0
indice_subzero_especial = 0
contador_subzero_especial = 0
animando_especial_subzero = False
indice_liu_parado = 0
indice_liu_andando = 0
indice_raiden_parado = 0
indice_raiden_andando = 0
indice_raiden_especial = 0
contador_raiden_especial = 0
animando_especial_raiden = False
contador_animacao = 0

atacando1 = False
atacando2 = False
contador_soco1 = 0
contador_soco2 = 0
acertou1 = False
acertou2 = False
invulneravel1 = 0
invulneravel2 = 0
cooldown_ataque1 = 0
cooldown_ataque2 = 0
bloqueando1 = False
bloqueando2 = False
atordoamento = {1: 0, 2: 0}
brilho_impacto = {1: 0, 2: 0}
congelamento = {1: 0, 2: 0}
particulas_impacto = []

TEMPO_Soco = 18
DURACAO_LUTA = 99
tempo_restante = DURACAO_LUTA * 60

# 6.1. PODERES ESPECIAIS (variaveis conforme o lutador escolhido)
# Cada jogador pode usar os dois poderes. O cooldown evita ataques infinitos.
projetis = []
recarga_lanca = {1: 0, 2: 0}
recarga_fogo = {1: 0, 2: 0}
TEMPO_RECARGA_LANCA = 150  # 2,5 segundos a 60 FPS
TEMPO_RECARGA_FOGO = 90   # 1,5 segundo a 60 FPS

# 7. FUNCOES AUXILIARES
def desenhar_texto(texto, fonte, cor, x, y, centralizado=True):
    """Desenha texto na tela."""
    imagem = fonte.render(texto, True, cor)
    retangulo = imagem.get_rect()
    if centralizado:
        retangulo.center = (x, y)
    else:
        retangulo.topleft = (x, y)
    tela.blit(imagem, retangulo)

CENARIO_LARGURA = 1280
CENARIO_ALTURA = 720
ESCALA_CENARIO_X = LARGURA / CENARIO_LARGURA
ESCALA_CENARIO_Y = ALTURA / CENARIO_ALTURA
ESCALA_CENARIO = min(ESCALA_CENARIO_X, ESCALA_CENARIO_Y)

CENARIO_PRETO = (8, 7, 15)
CENARIO_ROXO = (25, 13, 35)
CENARIO_VERMELHO = (130, 28, 25)
CENARIO_DOURADO = (190, 126, 48)


def ponto_cenario(x, y):
    return round(x * ESCALA_CENARIO_X), round(y * ESCALA_CENARIO_Y)


def retangulo_cenario(x, y, largura, altura):
    return pygame.Rect(
        round(x * ESCALA_CENARIO_X),
        round(y * ESCALA_CENARIO_Y),
        max(1, round(largura * ESCALA_CENARIO_X)),
        max(1, round(altura * ESCALA_CENARIO_Y)),
    )


def desenhar_gradiente(superficie, cima, baixo):
    """Cria o ceu em degradê do cenário."""
    for y in range(ALTURA):
        proporcao = y / ALTURA
        cor = tuple(
            int(cima[indice] * (1 - proporcao) + baixo[indice] * proporcao)
            for indice in range(3)
        )
        pygame.draw.line(superficie, cor, (0, y), (LARGURA, y))


def desenhar_montanhas(superficie):
    pygame.draw.polygon(superficie, (25, 17, 31), [
        ponto_cenario(x, y) for x, y in (
            (0, 390), (130, 250), (250, 370), (390, 220),
            (560, 390), (730, 245), (900, 370), (1060, 220),
            (1280, 390), (1280, 520), (0, 520)
        )
    ])
    pygame.draw.polygon(superficie, (15, 13, 23), [
        ponto_cenario(x, y) for x, y in (
            (0, 440), (190, 330), (350, 440), (520, 300),
            (710, 445), (900, 320), (1100, 440), (1280, 340),
            (1280, 550), (0, 550)
        )
    ])


def desenhar_lua(superficie):
    halo = pygame.Surface((360, 360), pygame.SRCALPHA)
    for raio in range(170, 20, -8):
        alpha = max(2, 22 - raio // 10)
        pygame.draw.circle(halo, (190, 65, 65, alpha), (180, 180), raio)
    superficie.blit(halo, ponto_cenario(820, 35))

    pygame.draw.circle(superficie, (220, 205, 185), ponto_cenario(1000, 210), round(88 * ESCALA_CENARIO))
    pygame.draw.circle(superficie, (190, 175, 165), ponto_cenario(970, 180), round(13 * ESCALA_CENARIO))
    pygame.draw.circle(superficie, (195, 180, 170), ponto_cenario(1030, 230), round(19 * ESCALA_CENARIO))
    pygame.draw.circle(superficie, (200, 185, 175), ponto_cenario(985, 250), round(9 * ESCALA_CENARIO))


def desenhar_templo(superficie):
    pygame.draw.rect(superficie, (18, 15, 23), retangulo_cenario(365, 245, 550, 280))
    pygame.draw.polygon(superficie, (35, 25, 30), [
        ponto_cenario(x, y) for x, y in ((330, 260), (640, 125), (950, 260))
    ])
    pygame.draw.polygon(superficie, (12, 11, 18), [
        ponto_cenario(x, y) for x, y in ((390, 250), (640, 155), (890, 250))
    ])
    pygame.draw.rect(superficie, (7, 7, 12), retangulo_cenario(520, 290, 240, 235))
    pygame.draw.arc(superficie, (90, 54, 43), retangulo_cenario(520, 245, 240, 100), math.pi, 2 * math.pi, 7)
    pygame.draw.rect(superficie, (75, 42, 35), retangulo_cenario(510, 285, 18, 245))
    pygame.draw.rect(superficie, (75, 42, 35), retangulo_cenario(752, 285, 18, 245))

    for x in (390, 470, 790, 870):
        pygame.draw.rect(superficie, (39, 32, 37), retangulo_cenario(x, 260, 34, 280))
        pygame.draw.rect(superficie, (75, 56, 49), retangulo_cenario(x - 7, 255, 48, 13))
        pygame.draw.rect(superficie, (75, 56, 49), retangulo_cenario(x - 7, 525, 48, 16))
        pygame.draw.line(superficie, (95, 68, 55), ponto_cenario(x + 8, 280), ponto_cenario(x + 8, 520), 2)


def desenhar_arcos_e_pilares(superficie):
    for x in (55, 1150):
        pygame.draw.rect(superficie, (22, 19, 25), retangulo_cenario(x, 210, 75, 390))
        pygame.draw.rect(superficie, (70, 49, 43), retangulo_cenario(x - 10, 205, 95, 20))
        pygame.draw.rect(superficie, (70, 49, 43), retangulo_cenario(x - 10, 580, 95, 22))
        pygame.draw.line(superficie, (95, 68, 55), ponto_cenario(x + 18, 230), ponto_cenario(x + 18, 575), 3)
        pygame.draw.line(superficie, (10, 9, 14), ponto_cenario(x + 53, 230), ponto_cenario(x + 53, 575), 4)


def desenhar_tocha(x, y, tempo):
    ponto = ponto_cenario(x, y)
    pygame.draw.line(
        tela, (85, 58, 35), ponto_cenario(x, y + 20), ponto_cenario(x, y + 75), 6
    )
    pygame.draw.circle(tela, (45, 30, 23), ponto, round(13 * ESCALA_CENARIO))

    altura = 25 + math.sin(tempo * 12 + x) * 5
    largura = 12 + math.sin(tempo * 17 + x) * 3
    pontos = [
        (x, y + 10), (x - largura, y - 17),
        (x - 10, y - 35 - altura * 0.25), (x, y - 60),
        (x + 13, y - 30), (x + largura, y - 10),
    ]
    pygame.draw.polygon(tela, (255, 105, 20), [ponto_cenario(px, py) for px, py in pontos])
    pygame.draw.ellipse(tela, (255, 210, 70), retangulo_cenario(x - 8, y - 27, 16, 34))


def desenhar_chao(superficie):
    pygame.draw.rect(superficie, (19, 16, 21), retangulo_cenario(0, 535, 1280, 185))
    pygame.draw.line(superficie, (115, 65, 43), ponto_cenario(0, 535), ponto_cenario(1280, 535), 4)
    for y in range(555, CENARIO_ALTURA, 32):
        pygame.draw.line(superficie, (48, 38, 39), ponto_cenario(0, y), ponto_cenario(1280, y), 2)
    for x in range(-300, CENARIO_LARGURA + 300, 120):
        pygame.draw.line(superficie, (39, 32, 36), ponto_cenario(640, 535), ponto_cenario(x, 720), 2)
    pygame.draw.line(superficie, (105, 47, 38), ponto_cenario(0, 690), ponto_cenario(1280, 690), 2)


def criar_cenario():
    superficie = pygame.Surface((LARGURA, ALTURA))
    desenhar_gradiente(superficie, CENARIO_PRETO, CENARIO_ROXO)
    desenhar_montanhas(superficie)
    desenhar_lua(superficie)
    desenhar_templo(superficie)
    desenhar_arcos_e_pilares(superficie)
    desenhar_chao(superficie)
    return superficie


cenario_fundo = criar_cenario()
neblina = pygame.Surface((LARGURA, ALTURA), pygame.SRCALPHA)
pygame.draw.ellipse(neblina, (120, 75, 75, 18), retangulo_cenario(180, 360, 920, 180))
brasas = [
    [random.randint(0, CENARIO_LARGURA), random.randint(150, CENARIO_ALTURA),
     random.uniform(0.4, 1.5), random.randint(2, 5)]
    for _ in range(55)
]


def atualizar_brasas():
    for brasa in brasas:
        brasa[1] -= brasa[2]
        brasa[0] += math.sin(brasa[1] * 0.03) * 0.5
        if brasa[1] < 170:
            brasa[0] = random.randint(0, CENARIO_LARGURA)
            brasa[1] = random.randint(550, CENARIO_ALTURA + 30)


def desenhar_cenario():
    """Desenha o templo sombrio, as tochas e as brasas animadas."""
    tela.blit(cenario_fundo, (0, 0))
    tela.blit(neblina, (0, 0))

    tempo = pygame.time.get_ticks() / 1000
    desenhar_tocha(330, 390, tempo)
    desenhar_tocha(950, 390, tempo + 1)

    atualizar_brasas()
    for x, y, _, tamanho in brasas:
        pygame.draw.circle(
            tela, (255, random.randint(95, 175), 35),
            ponto_cenario(x, y), max(1, round(tamanho * ESCALA_CENARIO))
        )

def desenhar_lutador_provisorio(retangulo, cor, direcao):
    """Desenha um personagem simples quando nao ha sprites disponiveis."""
    x = retangulo.centerx
    escala = retangulo.height / ALTURA_SPRITE
    topo = retangulo.top
    pygame.draw.ellipse(
        tela, (10, 10, 10),
        (retangulo.x - 8 * escala, retangulo.bottom - 12 * escala,
         95 * escala, 20 * escala)
    )
    pygame.draw.circle(tela, cor, (x, round(topo + 22 * escala)), round(19 * escala))
    pygame.draw.rect(
        tela, cor,
        (x - 19 * escala, topo + 42 * escala, 38 * escala, 48 * escala),
        border_radius=round(8 * escala)
    )
    pygame.draw.line(
        tela, cor, (x - 12 * escala, topo + 52 * escala),
        (x - 30 * escala * direcao, topo + 85 * escala), round(10 * escala)
    )
    pygame.draw.line(
        tela, cor, (x + 12 * escala, topo + 52 * escala),
        (x + 30 * escala * direcao, topo + 82 * escala), round(10 * escala)
    )
    pygame.draw.line(
        tela, cor, (x - 8 * escala, topo + 87 * escala),
        (x - 15 * escala, topo + 120 * escala), round(12 * escala)
    )
    pygame.draw.line(
        tela, cor, (x + 8 * escala, topo + 87 * escala),
        (x + 15 * escala, topo + 120 * escala), round(12 * escala)
    )

def desenhar_personagem(retangulo, imagem, direcao, cor):
    """Desenha o sprite principal ou o lutador provisório."""
    if imagem is None:
        if imagem_scorpion_principal is not None:
            sprite = imagem_scorpion_principal
            if direcao == -1:
                sprite = pygame.transform.flip(sprite, True, False)
            tela.blit(sprite, sprite.get_rect(midbottom=(retangulo.centerx, retangulo.bottom)))
            return
        desenhar_lutador_provisorio(retangulo, cor, direcao)
        return

    sprite = imagem
    if direcao == -1:
        sprite = pygame.transform.flip(sprite, True, False)
    tela.blit(sprite, sprite.get_rect(midbottom=(retangulo.centerx, retangulo.bottom)))


def desenhar_subzero(retangulo, imagem, direcao):
    desenhar_personagem(retangulo, imagem, direcao, (40, 110, 220))


def aplicar_brilho_sprite(imagem, jogador):
    if brilho_impacto[jogador] <= 0:
        return imagem
    sprite = imagem.copy()
    alpha = min(170, brilho_impacto[jogador] * 17)
    sobreposicao = pygame.mask.from_surface(sprite).to_surface(
        setcolor=(255, 255, 255, alpha),
        unsetcolor=(0, 0, 0, 0),
    )
    sprite.blit(sobreposicao, (0, 0))
    return sprite


def escolher_imagem_jogador(numero, andando):
    if personagem_raiden(numero):
        if animando_especial_raiden:
            return animacao_raiden_especial[indice_raiden_especial]
        if (atacando1 if numero == 1 else atacando2):
            indice = indice_soco1 if numero == 1 else indice_soco2
            return animacao_ataque_raiden[min(indice, len(animacao_ataque_raiden) - 1)]
        if andando and atordoamento[numero] == 0:
            return animacao_raiden_andando[indice_raiden_andando]
        return animacao_raiden_parado[indice_raiden_parado]

    if personagem_liu_kang(numero):
        chute = next(
            (
                poder for poder in projetis
                if poder["tipo"] == "chute_liu" and poder["dono"] == numero
            ),
            None,
        )
        if chute is not None:
            indice = min(chute["tempo"] // 3, len(animacao_liu_chute) - 1)
            return animacao_liu_chute[indice]
        if (atacando1 if numero == 1 else atacando2):
            indice = indice_soco1 if numero == 1 else indice_soco2
            return animacao_liu_soco[min(indice, len(animacao_liu_soco) - 1)]
        if andando and atordoamento[numero] == 0:
            return animacao_liu_andando[indice_liu_andando]
        return animacao_liu_parado[indice_liu_parado]

    if personagem_subzero(numero):
        if brilho_impacto[numero] > 0:
            indice = min((10 - brilho_impacto[numero]) // 3, len(animacao_subzero_dano) - 1)
            return animacao_subzero_dano[indice]
        if animando_especial_subzero:
            return animacao_subzero_especial[indice_subzero_especial]
        if (atacando1 if numero == 1 else atacando2):
            quadros = animacao_subzero_soco
            indice = indice_soco1 if numero == 1 else indice_soco2
            return quadros[min(indice, len(quadros) - 1)]
        if (bloqueando1 if numero == 1 else bloqueando2):
            return animacao_subzero_defesa[indice_subzero_defesa]
        lutador = jogador1 if numero == 1 else jogador2
        if lutador.bottom < CHAO:
            return animacao_subzero_pulo[indice_subzero_pulo]
        if andando and atordoamento[numero] == 0:
            return animacao_subzero_andando[indice_subzero_andando]
        return animacao_subzero_parado[indice_subzero_parado]

    if (atacando1 if numero == 1 else atacando2) and animacao_soco:
        indice = indice_soco1 if numero == 1 else indice_soco2
        return animacao_soco[min(indice, len(animacao_soco) - 1)]
    if andando and animacao_andando:
        return animacao_andando[indice_andando]
    if animacao_parado:
        return animacao_parado[indice_parado]
    return imagem_scorpion_principal


def desenhar_barra_vida(x, y, vida, cor, inverter=False):
    """Desenha a barra de vida de cada jogador."""
    pygame.draw.rect(tela, (55, 20, 25), (x, y, 360, 28), border_radius=5)
    largura = max(0, int(356 * vida / 100))
    if inverter:
        pygame.draw.rect(tela, cor, (x + 358 - largura, y + 2, largura, 24), border_radius=4)
    else:
        pygame.draw.rect(tela, cor, (x + 2, y + 2, largura, 24), border_radius=4)
    pygame.draw.rect(tela, BRANCO, (x, y, 360, 28), 2, border_radius=5)


def aplicar_dano(alvo, dano, atacante, cor_impacto):
    global vida_jogador1, vida_jogador2, invulneravel1, invulneravel2
    global atacando1, atacando2, contador_soco1, contador_soco2

    invulneravel = invulneravel1 if alvo == 1 else invulneravel2
    if invulneravel > 0:
        return None

    defensor = jogador1 if alvo == 1 else jogador2
    agressor = jogador1 if atacante == 1 else jogador2
    direcao_defensor = direcao_jogador1 if alvo == 1 else direcao_jogador2
    bloqueando = bloqueando1 if alvo == 1 else bloqueando2
    protegeu = bloqueando and (agressor.centerx - defensor.centerx) * direcao_defensor > 0
    dano_final = max(1, round(dano * (0.25 if protegeu else 1)))

    if alvo == 1:
        vida_jogador1 = max(0, vida_jogador1 - dano_final)
        invulneravel1 = 12 if protegeu else 30
    else:
        vida_jogador2 = max(0, vida_jogador2 - dano_final)
        invulneravel2 = 12 if protegeu else 30

    atordoamento[alvo] = 3 if protegeu else 9
    brilho_impacto[alvo] = 10
    if alvo == 1:
        atacando1 = False
        contador_soco1 = 0
    else:
        atacando2 = False
        contador_soco2 = 0

    empurrao = 2 if protegeu else 7
    defensor.x += empurrao if agressor.centerx < defensor.centerx else -empurrao
    defensor.x = max(0, min(LARGURA - defensor.width, defensor.x))

    for _ in range(10 if not protegeu else 6):
        angulo = random.uniform(0, 2 * math.pi)
        velocidade = random.uniform(1.5, 4.5)
        particulas_impacto.append([
            float(defensor.centerx), float(defensor.centery),
            math.cos(angulo) * velocidade, math.sin(angulo) * velocidade,
            random.randint(12, 22), cor_impacto
        ])

    som = som_bloqueio if protegeu else som_golpe
    if som is not None:
        som.play()
    return "bloqueado" if protegeu else "acertou"


def atualizar_particulas_impacto():
    for particula in particulas_impacto[:]:
        particula[0] += particula[2]
        particula[1] += particula[3]
        particula[3] += 0.12
        particula[4] -= 1
        if particula[4] <= 0:
            particulas_impacto.remove(particula)


def desenhar_particulas_impacto():
    for x, y, _, _, vida, cor in particulas_impacto:
        pygame.draw.circle(
            tela, cor, (round(x), round(y)), max(1, min(5, vida // 4))
        )


def criar_area_soco(lutador, direcao):
    x = lutador.right if direcao > 0 else lutador.left - 82
    return pygame.Rect(x, lutador.top + 25, 82, 70)


def personagem_subzero(jogador):
    nome = NOME_JOGADOR1 if jogador == 1 else NOME_JOGADOR2
    return nome == "SUB-ZERO"


def personagem_liu_kang(jogador):
    nome = NOME_JOGADOR1 if jogador == 1 else NOME_JOGADOR2
    return nome == "LIU KANG"


def personagem_raiden(jogador):
    nome = NOME_JOGADOR1 if jogador == 1 else NOME_JOGADOR2
    return nome == "RAIDEN"


def iniciar_animacao_especial_raiden():
    global animando_especial_raiden, contador_raiden_especial
    global indice_raiden_especial
    animando_especial_raiden = True
    contador_raiden_especial = 0
    indice_raiden_especial = 0


def chute_liu_ativo(jogador):
    return any(
        poder["tipo"] == "chute_liu" and poder["dono"] == jogador
        for poder in projetis
    )


def iniciar_ataque(jogador):
    """Inicia um soco para o jogador escolhido somente quando o cooldown terminar."""
    global atacando1, atacando2, contador_soco1, contador_soco2
    global indice_soco1, indice_soco2, acertou1, acertou2
    global cooldown_ataque1, cooldown_ataque2

    if jogador == 1 and not bloqueando1 and atordoamento[1] == 0 and not atacando1 and not chute_liu_ativo(1) and cooldown_ataque1 <= 0:
        atacando1 = True
        contador_soco1 = 0
        indice_soco1 = 0
        acertou1 = False
        cooldown_ataque1 = TEMPO_Soco
    elif jogador == 2 and not bloqueando2 and atordoamento[2] == 0 and not atacando2 and not chute_liu_ativo(2) and cooldown_ataque2 <= 0:
        atacando2 = True
        contador_soco2 = 0
        indice_soco2 = 0
        acertou2 = False
        cooldown_ataque2 = TEMPO_Soco

def usar_lanca(jogador):
    """Usa a corrente, o chute de Liu Kang ou o teleporte de Raiden."""
    global animando_especial_subzero, contador_subzero_especial, indice_subzero_especial
    global direcao_jogador1, direcao_jogador2
    if recarga_lanca[jogador] > 0:
        return
    origem = jogador1 if jogador == 1 else jogador2
    alvo = jogador2 if jogador == 1 else jogador1
    direcao = direcao_jogador1 if jogador == 1 else direcao_jogador2
    if personagem_raiden(jogador):
        x_direita = alvo.right + 8
        x_esquerda = alvo.left - origem.width - 8
        if direcao > 0 and x_direita + origem.width <= LARGURA:
            origem.x = x_direita
        elif x_esquerda >= 0:
            origem.x = x_esquerda
        else:
            origem.x = max(0, min(LARGURA - origem.width, x_direita))
        direcao = 1 if alvo.centerx > origem.centerx else -1
        if jogador == 1:
            direcao_jogador1 = direcao
        else:
            direcao_jogador2 = direcao
        projetis.append({
            "tipo": "teleporte_raiden", "dono": jogador,
            "x": float(alvo.centerx), "y": float(alvo.centery),
            "direcao": direcao, "tempo": 0, "acertou": True
        })
        aplicar_dano(2 if jogador == 1 else 1, 17, jogador, (110, 205, 255))
        recarga_lanca[jogador] = TEMPO_RECARGA_LANCA
        iniciar_animacao_especial_raiden()
        return

    if personagem_liu_kang(jogador):
        projetis.append({
            "tipo": "chute_liu", "dono": jogador,
            "x": float(origem.centerx + direcao * 28),
            "y": float(origem.centery), "direcao": direcao,
            "tempo": 0, "acertou": False
        })
        recarga_lanca[jogador] = TEMPO_RECARGA_LANCA
        return

    tipo = "lanca_gelo" if personagem_subzero(jogador) else "lanca"
    projetis.append({
        "tipo": tipo, "dono": jogador,
        "x": float(origem.centerx + direcao * 28 if personagem_subzero(jogador) else origem.centerx),
        "y": float(origem.y + 48), "direcao": direcao,
        "fase": "ida", "tempo": 0, "acertou": False
    })
    recarga_lanca[jogador] = TEMPO_RECARGA_LANCA
    if personagem_subzero(jogador):
        animando_especial_subzero = True
        contador_subzero_especial = 0
        indice_subzero_especial = 0

def usar_fogo(jogador):
    """Dispara fogo, gelo, a Bola do Dragao ou um raio de Raiden."""
    global animando_especial_subzero, contador_subzero_especial, indice_subzero_especial
    if recarga_fogo[jogador] > 0:
        return
    origem = jogador1 if jogador == 1 else jogador2
    direcao = direcao_jogador1 if jogador == 1 else direcao_jogador2
    if personagem_raiden(jogador):
        tipo = "raio_raiden"
    elif personagem_liu_kang(jogador):
        tipo = "fogo_liu"
    elif personagem_subzero(jogador):
        tipo = "gelo"
    else:
        tipo = "fogo"
    projetis.append({
        "tipo": tipo, "dono": jogador,
        "x": float(origem.centerx + direcao * 42),
        "y": float(origem.y + 58), "direcao": direcao,
        "tempo": 0, "acertou": False
    })
    recarga_fogo[jogador] = TEMPO_RECARGA_FOGO
    if personagem_subzero(jogador):
        animando_especial_subzero = True
        contador_subzero_especial = 0
        indice_subzero_especial = 0
    elif personagem_raiden(jogador):
        iniciar_animacao_especial_raiden()

def atualizar_poderes():
    """Atualiza movimento, colisao, dano e puxao dos poderes."""
    for jogador in (1, 2):
        recarga_lanca[jogador] = max(0, recarga_lanca[jogador] - 1)
        recarga_fogo[jogador] = max(0, recarga_fogo[jogador] - 1)

    for poder in projetis[:]:
        dono = poder["dono"]
        alvo = jogador2 if dono == 1 else jogador1
        poder["tempo"] += 1

        if poder["tipo"] in ("fogo", "fogo_liu", "gelo", "raio_raiden"):
            poder["x"] += poder["direcao"] * (
                14 if poder["tipo"] == "raio_raiden" else 10
            )
            caixa_fogo = pygame.Rect(int(poder["x"] - 18), int(poder["y"] - 16), 36, 32)
            if caixa_fogo.colliderect(alvo) and not poder["acertou"]:
                cor = (
                    (100, 220, 255)
                    if poder["tipo"] in ("gelo", "raio_raiden")
                    else (255, 170, 45)
                )
                if poder["tipo"] == "gelo":
                    dano = 11
                elif poder["tipo"] == "raio_raiden":
                    dano = 16
                else:
                    dano = 14
                impacto = aplicar_dano(2 if dono == 1 else 1, dano, dono, cor)
                if poder["tipo"] == "gelo" and impacto == "acertou":
                    congelamento[2 if dono == 1 else 1] = 90
                elif poder["tipo"] == "raio_raiden" and impacto == "acertou":
                    atordoamento[2 if dono == 1 else 1] = 24
                poder["acertou"] = True
                projetis.remove(poder)
            elif poder["tempo"] > 100 or not (-40 <= poder["x"] <= LARGURA + 40):
                projetis.remove(poder)

        elif poder["tipo"] == "teleporte_raiden":
            if poder["tempo"] >= 12:
                projetis.remove(poder)

        elif poder["tipo"] == "chute_liu":
            lutador = jogador1 if dono == 1 else jogador2
            lutador.x += poder["direcao"] * 11
            lutador.x = max(0, min(LARGURA - lutador.width, lutador.x))
            poder["x"] = float(lutador.centerx + poder["direcao"] * 28)
            poder["y"] = float(lutador.centery)
            area_chute = pygame.Rect(
                int(poder["x"] - (52 if poder["direcao"] < 0 else 0)),
                int(poder["y"] - 30),
                52,
                60,
            )
            if area_chute.colliderect(alvo) and not poder["acertou"]:
                aplicar_dano(2 if dono == 1 else 1, 18, dono, (255, 130, 45))
                poder["acertou"] = True
                projetis.remove(poder)
            elif poder["tempo"] >= 22 or lutador.left == 0 or lutador.right == LARGURA:
                projetis.remove(poder)

        elif poder["tipo"] == "lanca_gelo":
            poder["x"] += poder["direcao"] * 15
            ponta_gelo = pygame.Rect(int(poder["x"] - 13), int(poder["y"] - 12), 26, 24)
            if ponta_gelo.colliderect(alvo):
                alvo_numero = 2 if dono == 1 else 1
                impacto = aplicar_dano(alvo_numero, 12, dono, (110, 220, 255))
                if impacto == "acertou":
                    congelamento[alvo_numero] = 60
                projetis.remove(poder)
            elif poder["tempo"] > 45 or not (-40 <= poder["x"] <= LARGURA + 40):
                projetis.remove(poder)

        elif poder["tipo"] == "lanca":
            if poder["fase"] == "ida":
                poder["x"] += poder["direcao"] * 15
                alcance = abs(poder["x"] - (jogador1.centerx if dono == 1 else jogador2.centerx))
                ponta = pygame.Rect(int(poder["x"] - 13), int(poder["y"] - 12), 26, 24)
                if ponta.colliderect(alvo) and not poder["acertou"]:
                    resultado_impacto = aplicar_dano(
                        2 if dono == 1 else 1, 8, dono, (220, 220, 235)
                    )
                    poder["acertou"] = True
                    if resultado_impacto == "acertou":
                        poder["fase"] = "puxar"
                    else:
                        projetis.remove(poder)
                elif alcance > 520:
                    projetis.remove(poder)
            else:
                # Puxa o adversario em direcao ao dono durante alguns frames.
                dono_rect = jogador1 if dono == 1 else jogador2
                diferenca = dono_rect.centerx - alvo.centerx
                if abs(diferenca) > 88:
                    alvo.x += 7 if diferenca > 0 else -7
                    alvo.x = max(0, min(LARGURA - alvo.width, alvo.x))
                if poder["tempo"] > 48 or abs(diferenca) <= 88:
                    projetis.remove(poder)

def desenhar_poderes():
    """Desenha correntes, projeteis elementais e o rastro do chute de Liu Kang."""
    for poder in projetis:
        if poder["tipo"] == "raio_raiden":
            x, y = int(poder["x"]), int(poder["y"])
            direcao = poder["direcao"]
            pontos = [
                (x - direcao * 46, y),
                (x - direcao * 33, y - 9),
                (x - direcao * 25, y + 5),
                (x - direcao * 15, y - 7),
                (x - direcao * 6, y + 7),
                (x, y),
            ]
            pygame.draw.lines(tela, (90, 150, 255), False, pontos, 12)
            pygame.draw.lines(tela, (180, 235, 255), False, pontos, 7)
            pygame.draw.lines(tela, (255, 255, 225), False, pontos, 3)
            pygame.draw.circle(tela, (180, 235, 255), (x, y), 10)
        elif poder["tipo"] == "teleporte_raiden":
            x, y = int(poder["x"]), int(poder["y"])
            pulso = poder["tempo"] % 4
            pygame.draw.circle(tela, (65, 130, 255), (x, y), 48 - pulso, 5)
            pygame.draw.circle(tela, (185, 235, 255), (x, y), 34 - pulso, 3)
            for deslocamento in (-24, 0, 24):
                pygame.draw.line(
                    tela, (150, 220, 255),
                    (x + deslocamento - 8, y - 36),
                    (x + deslocamento + 8, y - 17), 3
                )
        elif poder["tipo"] in ("fogo", "fogo_liu", "gelo"):
            x, y = int(poder["x"]), int(poder["y"])
            pulso = poder["tempo"] % 4
            if poder["tipo"] == "gelo":
                pygame.draw.circle(tela, (60, 155, 255), (x, y), 18 + pulso)
                pygame.draw.circle(tela, (145, 225, 255), (x, y), 12 + pulso // 2)
                pygame.draw.polygon(tela, (235, 250, 255), [
                    (x, y - 10), (x + 7, y), (x, y + 10), (x - 7, y)
                ])
            elif poder["tipo"] == "fogo_liu":
                pygame.draw.circle(tela, (180, 35, 18), (x, y), 22 + pulso)
                pygame.draw.circle(tela, (255, 95, 18), (x, y), 16 + pulso // 2)
                pygame.draw.polygon(tela, (255, 210, 65), [
                    (x - 18, y), (x - 5, y - 10), (x + 17, y),
                    (x - 5, y + 10)
                ])
                pygame.draw.circle(tela, (255, 250, 190), (x, y), 5)
            else:
                pygame.draw.circle(tela, (255, 70, 15), (x, y), 18 + pulso)
                pygame.draw.circle(tela, (255, 190, 35), (x, y), 12 + pulso // 2)
                pygame.draw.circle(tela, (255, 245, 170), (x, y), 6)
                pygame.draw.circle(tela, (255, 110, 20), (x - poder["direcao"] * 13, y + 5), 8)
        elif poder["tipo"] == "lanca_gelo":
            x, y = int(poder["x"]), int(poder["y"])
            direcao = poder["direcao"]
            dono_rect = jogador2 if poder["dono"] == 2 else jogador1
            inicio = (dono_rect.centerx + direcao * 28, dono_rect.y + 48)
            fim = (x, y)
            pygame.draw.line(tela, (85, 200, 255), inicio, fim, 7)
            pygame.draw.line(tela, (220, 250, 255), inicio, fim, 3)
            pygame.draw.polygon(tela, (180, 240, 255), [
                (x + direcao * 19, y),
                (x - direcao * 13, y - 10),
                (x - direcao * 13, y + 10)
            ])
        elif poder["tipo"] == "chute_liu":
            x, y = int(poder["x"]), int(poder["y"])
            direcao = poder["direcao"]
            pygame.draw.line(
                tela, (170, 35, 18),
                (x - direcao * 34, y + 12), (x + direcao * 10, y + 12), 14
            )
            for distancia, cor, raio in (
                (29, (255, 75, 15), 9),
                (15, (255, 155, 30), 7),
                (2, (255, 225, 85), 5),
            ):
                pygame.draw.circle(
                    tela, cor, (x - direcao * distancia, y + 12), raio
                )
        else:
            dono_rect = jogador1 if poder["dono"] == 1 else jogador2
            inicio = (dono_rect.centerx + poder["direcao"] * 28, dono_rect.y + 48)
            fim = (int(poder["x"]), int(poder["y"]))
            pygame.draw.line(tela, (35, 35, 42), inicio, fim, 8)
            pygame.draw.line(tela, (190, 190, 200), inicio, fim, 4)
            # Pequenos elos dourados dão movimento visual à corrente.
            for t in range(1, 10):
                px = inicio[0] + (fim[0] - inicio[0]) * t / 10
                py = inicio[1] + (fim[1] - inicio[1]) * t / 10
                pygame.draw.circle(tela, (235, 175, 65), (int(px), int(py)), 3)
            pygame.draw.polygon(tela, (210, 210, 220), [
                (fim[0] + poder["direcao"] * 15, fim[1]),
                (fim[0] - poder["direcao"] * 8, fim[1] - 9),
                (fim[0] - poder["direcao"] * 8, fim[1] + 9)
            ])


def reiniciar_partida():
    global vida_jogador1, vida_jogador2
    global velocidade_vertical_jogador1, velocidade_vertical_jogador2
    global direcao_jogador1, direcao_jogador2
    global cpu_tempo_decisao, cpu_tempo_defesa
    global indice_parado, indice_andando, indice_soco1, indice_soco2, contador_animacao
    global indice_subzero_parado, indice_subzero_andando, indice_subzero_pulo
    global indice_subzero_defesa, indice_subzero_especial, contador_subzero_especial
    global indice_liu_parado, indice_liu_andando
    global indice_raiden_parado, indice_raiden_andando, indice_raiden_especial
    global contador_raiden_especial, animando_especial_raiden
    global animando_especial_subzero
    global atacando1, atacando2, contador_soco1, contador_soco2, acertou1, acertou2
    global invulneravel1, invulneravel2, cooldown_ataque1, cooldown_ataque2
    global bloqueando1, bloqueando2, tempo_restante, vencedor

    jogador1.update(
        190, CHAO - ALTURA_SPRITE, LARGURA_COLISAO, ALTURA_SPRITE
    )
    jogador2.update(
        735, CHAO - ALTURA_SPRITE, LARGURA_COLISAO, ALTURA_SPRITE
    )
    velocidade_vertical_jogador1 = 0
    velocidade_vertical_jogador2 = 0
    vida_jogador1 = 100
    vida_jogador2 = 100
    direcao_jogador1 = 1
    direcao_jogador2 = -1
    indice_parado = indice_andando = indice_soco1 = indice_soco2 = 0
    indice_subzero_parado = indice_subzero_andando = 0
    indice_subzero_pulo = indice_subzero_defesa = indice_subzero_especial = 0
    indice_liu_parado = indice_liu_andando = 0
    indice_raiden_parado = indice_raiden_andando = indice_raiden_especial = 0
    contador_raiden_especial = 0
    animando_especial_raiden = False
    contador_subzero_especial = 0
    animando_especial_subzero = False
    contador_animacao = 0
    atacando1 = atacando2 = False
    contador_soco1 = contador_soco2 = 0
    acertou1 = acertou2 = False
    invulneravel1 = invulneravel2 = 0
    cooldown_ataque1 = cooldown_ataque2 = 0
    bloqueando1 = bloqueando2 = False
    atordoamento[1] = atordoamento[2] = 0
    brilho_impacto[1] = brilho_impacto[2] = 0
    congelamento[1] = congelamento[2] = 0
    recarga_lanca[1] = recarga_lanca[2] = 0
    recarga_fogo[1] = recarga_fogo[2] = 0
    projetis.clear()
    particulas_impacto.clear()
    tempo_restante = DURACAO_LUTA * 60
    vencedor = ""
    cpu_tempo_decisao = 0
    cpu_tempo_defesa = 0


# 8. MENU INICIAL E ESTADOS DO JOGO
estado_jogo = "menu"
rodando = True
vencedor = ""
tela_pausa = None
menu_jogo = MenuJogo(tela)
volume_aplicado = None


def aplicar_volume_menu():
    global volume_aplicado
    volume = menu_jogo.config["volume"] / 10
    if volume == volume_aplicado:
        return
    if pygame.mixer.get_init():
        pygame.mixer.music.set_volume(volume)
        for som in (som_golpe, som_bloqueio):
            if som is not None:
                som.set_volume(volume)
    volume_aplicado = volume

# 9. LOOP PRINCIPAL DO JOGO
while rodando:

    # 9.1. CAPTURA DOS EVENTOS DO TECLADO E DA JANELA
    for evento in pygame.event.get():
        if evento.type == pygame.QUIT:
            rodando = False

        if evento.type == pygame.KEYDOWN and evento.key == pygame.K_F11:
            menu_jogo.alternar_tela_cheia()

        if estado_jogo == "menu":
            menu_jogo.processar_evento(evento)
            if menu_jogo.pronto:
                NOME_JOGADOR1 = PERSONAGENS_MENU[menu_jogo.p1][0].upper()
                NOME_JOGADOR2 = PERSONAGENS_MENU[menu_jogo.p2][0].upper()
                modo_jogo = menu_jogo.modo
                menu_jogo.pronto = False
                reiniciar_partida()
                estado_jogo = "luta"
            continue

        if evento.type == pygame.KEYDOWN:
            if estado_jogo == "resultado":
                if evento.key == pygame.K_RETURN:
                    reiniciar_partida()
                    estado_jogo = "luta"
                elif evento.key == pygame.K_ESCAPE:
                    menu_jogo.voltar_ao_menu()
                    estado_jogo = "menu"

            elif estado_jogo == "luta":
                if evento.key == pygame.K_ESCAPE:
                    tela_pausa = tela.copy()
                    estado_jogo = "pausado"
                elif evento.key == pygame.K_w and jogador1.bottom >= CHAO and atordoamento[1] == 0:
                    velocidade_vertical_jogador1 = FORCA_PULO
                elif evento.key == pygame.K_UP and modo_jogo == "dois" and jogador2.bottom >= CHAO and atordoamento[2] == 0:
                    velocidade_vertical_jogador2 = FORCA_PULO

                # J/P: soco; U/NUM1: corrente; I/NUM2: fogo ou gelo.
                if evento.key == pygame.K_j:
                    iniciar_ataque(1)
                if evento.key == pygame.K_p and modo_jogo == "dois":
                    iniciar_ataque(2)
                if evento.key == pygame.K_u:
                    usar_lanca(1)
                if evento.key == pygame.K_i:
                    usar_fogo(1)
                if evento.key == pygame.K_KP1 and modo_jogo == "dois":
                    usar_lanca(2)
                if evento.key == pygame.K_KP2 and modo_jogo == "dois":
                    usar_fogo(2)

            elif estado_jogo == "pausado" and evento.key == pygame.K_ESCAPE:
                estado_jogo = "luta"
                tela_pausa = None

    tela = pygame.display.get_surface()
    menu_jogo.tela = tela
    aplicar_volume_menu()

    # 9.2. DESENHO DO MENU INICIAL
    if estado_jogo == "menu":
        menu_jogo.t += 1 / 60
        menu_jogo.desenhar()

    # 9.3. ATUALIZACAO E DESENHO DA LUTA
    elif estado_jogo == "luta":
        teclas = pygame.key.get_pressed()
        bloqueando1 = teclas[pygame.K_s] and jogador1.bottom >= CHAO
        if modo_jogo == "solo":
            cpu_tempo_decisao = max(0, cpu_tempo_decisao - 1)
            cpu_tempo_defesa = max(0, cpu_tempo_defesa - 1)
            bloqueando2 = cpu_tempo_defesa > 0 and jogador2.bottom >= CHAO
            distancia_cpu = abs(jogador1.centerx - jogador2.centerx)
            direcao_jogador2 = -1 if jogador2.centerx > jogador1.centerx else 1
            if cpu_tempo_decisao == 0 and atordoamento[2] == 0 and congelamento[2] == 0:
                intervalo_cpu = (26, 20, 14)[menu_jogo.config["dificuldade"]]
                cpu_tempo_decisao = random.randint(intervalo_cpu - 4, intervalo_cpu + 4)
                if atacando1 and distancia_cpu < 145 and random.random() < 0.35:
                    cpu_tempo_defesa = random.randint(12, 24)
                elif distancia_cpu <= 115:
                    iniciar_ataque(2)
                elif distancia_cpu <= 410 and recarga_lanca[2] == 0 and random.random() < 0.35:
                    usar_lanca(2)
                elif recarga_fogo[2] == 0 and random.random() < 0.3:
                    usar_fogo(2)
        else:
            bloqueando2 = teclas[pygame.K_DOWN] and jogador2.bottom >= CHAO

        if tempo_restante > 0:
            tempo_restante -= 1

        # Movimentacao do jogador 1.
        if atordoamento[1] > 0:
            atordoamento[1] -= 1
        elif not atacando1 and not bloqueando1 and not chute_liu_ativo(1):
            velocidade_atual = int(VELOCIDADE_JOGADOR1 * (0.55 if congelamento[1] > 0 else 1))
            if teclas[pygame.K_a]:
                jogador1.x -= velocidade_atual
                direcao_jogador1 = -1
            if teclas[pygame.K_d]:
                jogador1.x += velocidade_atual
                direcao_jogador1 = 1

        # Movimentacao do jogador 2.
        if atordoamento[2] > 0:
            atordoamento[2] -= 1
        elif not atacando2 and not bloqueando2 and not chute_liu_ativo(2):
            if modo_jogo == "solo":
                if distancia_cpu > 105 and congelamento[2] == 0:
                    jogador2.x += direcao_jogador2 * VELOCIDADE_JOGADOR2
            else:
                velocidade_atual = int(VELOCIDADE_JOGADOR2 * (0.55 if congelamento[2] > 0 else 1))
                if teclas[pygame.K_LEFT]:
                    jogador2.x -= velocidade_atual
                    direcao_jogador2 = -1
                if teclas[pygame.K_RIGHT]:
                    jogador2.x += velocidade_atual
                    direcao_jogador2 = 1

        congelamento[1] = max(0, congelamento[1] - 1)
        congelamento[2] = max(0, congelamento[2] - 1)

        # Aplica gravidade e mantem os lutadores apoiados no chao.
        if jogador1.bottom < CHAO or velocidade_vertical_jogador1 < 0:
            velocidade_vertical_jogador1 += GRAVIDADE
            jogador1.y += round(velocidade_vertical_jogador1)
            if jogador1.bottom >= CHAO:
                jogador1.bottom = CHAO
                velocidade_vertical_jogador1 = 0
        if jogador2.bottom < CHAO or velocidade_vertical_jogador2 < 0:
            velocidade_vertical_jogador2 += GRAVIDADE
            jogador2.y += round(velocidade_vertical_jogador2)
            if jogador2.bottom >= CHAO:
                jogador2.bottom = CHAO
                velocidade_vertical_jogador2 = 0

        # Mantem os personagens dentro da arena.
        jogador1.left = max(0, jogador1.left)
        jogador1.right = min(LARGURA, jogador1.right)
        jogador2.left = max(0, jogador2.left)
        jogador2.right = min(LARGURA, jogador2.right)

        # Atualiza a animacao e o acerto do soco do jogador 1.
        if atacando1:
            contador_soco1 += 1
            quadros_soco1 = (
                animacao_subzero_soco if personagem_subzero(1)
                else animacao_ataque_raiden if personagem_raiden(1)
                else animacao_soco
            )
            velocidade_animacao_soco1 = 5 if personagem_subzero(1) else 4
            if quadros_soco1:
                indice_soco1 = min(contador_soco1 // velocidade_animacao_soco1, len(quadros_soco1) - 1)
            if contador_soco1 >= max(20, len(quadros_soco1) * velocidade_animacao_soco1):
                atacando1 = False
                contador_soco1 = 0
                indice_soco1 = 0

            if not acertou1 and 8 <= contador_soco1 <= 24:
                ataque1 = criar_area_soco(jogador1, direcao_jogador1)
                if ataque1.colliderect(jogador2):
                    cor_golpe = (130, 205, 255) if personagem_subzero(1) else (255, 195, 85)
                    acertou1 = aplicar_dano(2, 10, 1, cor_golpe) is not None

        # Atualiza a animacao e o acerto do soco do jogador 2.
        if atacando2:
            contador_soco2 += 1
            quadros_soco2 = (
                animacao_subzero_soco if personagem_subzero(2)
                else animacao_ataque_raiden if personagem_raiden(2)
                else animacao_soco
            )
            velocidade_animacao_soco2 = 5 if personagem_subzero(2) else 4
            if quadros_soco2:
                indice_soco2 = min(contador_soco2 // velocidade_animacao_soco2, len(quadros_soco2) - 1)
            if contador_soco2 >= max(20, len(quadros_soco2) * velocidade_animacao_soco2):
                atacando2 = False
                contador_soco2 = 0
                indice_soco2 = 0

            if not acertou2 and 8 <= contador_soco2 <= 24:
                ataque2 = criar_area_soco(jogador2, direcao_jogador2)
                if ataque2.colliderect(jogador1):
                    cor_golpe = (130, 205, 255) if personagem_subzero(2) else (255, 195, 85)
                    acertou2 = aplicar_dano(1, 10, 2, cor_golpe) is not None

        # Atualiza os poderes especiais e suas colisoes.
        atualizar_poderes()
        atualizar_particulas_impacto()

        # Diminui o tempo de protecao depois de receber um golpe.
        if invulneravel1 > 0:
            invulneravel1 -= 1
        if invulneravel2 > 0:
            invulneravel2 -= 1
        brilho_impacto[1] = max(0, brilho_impacto[1] - 1)
        brilho_impacto[2] = max(0, brilho_impacto[2] - 1)
        if cooldown_ataque1 > 0:
            cooldown_ataque1 -= 1
        if cooldown_ataque2 > 0:
            cooldown_ataque2 -= 1

        # Atualiza a velocidade das animacoes de parado e caminhada.
        contador_animacao += 1
        if contador_animacao >= 8:
            contador_animacao = 0
            if animacao_parado:
                indice_parado = (indice_parado + 1) % len(animacao_parado)
            if animacao_andando:
                indice_andando = (indice_andando + 1) % len(animacao_andando)
            indice_subzero_parado = (indice_subzero_parado + 1) % len(animacao_subzero_parado)
            indice_subzero_andando = (indice_subzero_andando + 1) % len(animacao_subzero_andando)
            indice_subzero_defesa = (indice_subzero_defesa + 1) % len(animacao_subzero_defesa)
            indice_liu_parado = (indice_liu_parado + 1) % len(animacao_liu_parado)
            indice_liu_andando = (indice_liu_andando + 1) % len(animacao_liu_andando)
            indice_raiden_parado = (indice_raiden_parado + 1) % len(animacao_raiden_parado)
            indice_raiden_andando = (indice_raiden_andando + 1) % len(animacao_raiden_andando)

        if animando_especial_subzero:
            contador_subzero_especial += 1
            indice_subzero_especial = min(
                contador_subzero_especial // 3, len(animacao_subzero_especial) - 1
            )
            if contador_subzero_especial >= len(animacao_subzero_especial) * 3:
                animando_especial_subzero = False
                contador_subzero_especial = 0

        if animando_especial_raiden:
            contador_raiden_especial += 1
            indice_raiden_especial = min(
                contador_raiden_especial // 3, len(animacao_raiden_especial) - 1
            )
            if contador_raiden_especial >= len(animacao_raiden_especial) * 3:
                animando_especial_raiden = False
                contador_raiden_especial = 0

        if personagem_subzero(1) and jogador1.bottom < CHAO:
            progresso_pulo1 = 1 - min(
                1, abs(velocidade_vertical_jogador1) / abs(FORCA_PULO)
            )
            indice_subzero_pulo = round(progresso_pulo1 * (len(animacao_subzero_pulo) - 1))
        if personagem_subzero(2) and jogador2.bottom < CHAO:
            progresso_pulo = 1 - min(
                1, abs(velocidade_vertical_jogador2) / abs(FORCA_PULO)
            )
            indice_subzero_pulo = round(progresso_pulo * (len(animacao_subzero_pulo) - 1))

        # Desenha o cenario e as barras de vida.
        desenhar_cenario()
        desenhar_texto(NOME_JOGADOR1, fonte_normal, AMARELO, 180, 35)
        desenhar_texto(NOME_JOGADOR2, fonte_normal, (120, 180, 255), 820, 35)
        desenhar_texto(f"{tempo_restante // 60:02}", fonte_media, BRANCO, 500, 35)
        desenhar_barra_vida(35, 55, vida_jogador1, (205, 45, 45))
        desenhar_barra_vida(605, 55, vida_jogador2, (45, 115, 225), True)

        andando1 = teclas[pygame.K_a] or teclas[pygame.K_d]
        andando2 = (
            teclas[pygame.K_LEFT] or teclas[pygame.K_RIGHT]
            or (modo_jogo == "solo" and distancia_cpu > 105)
        )

        imagem1 = escolher_imagem_jogador(1, andando1)
        imagem2 = escolher_imagem_jogador(2, andando2)
        imagem1 = aplicar_brilho_sprite(imagem1, 1)
        imagem2 = aplicar_brilho_sprite(imagem2, 2)
        if personagem_subzero(1):
            desenhar_subzero(jogador1, imagem1, direcao_jogador1)
        else:
            desenhar_personagem(jogador1, imagem1, direcao_jogador1, (205, 115, 35))
        if personagem_subzero(2):
            desenhar_subzero(jogador2, imagem2, direcao_jogador2)
        else:
            desenhar_personagem(jogador2, imagem2, direcao_jogador2, (205, 115, 35))

        if bloqueando1:
            pygame.draw.arc(tela, (255, 210, 105),
                            (jogador1.x - 12, jogador1.y + 16, 100, 92), 0.3, 2.8, 5)
            desenhar_texto("DEFESA", fonte_pequena, (255, 220, 145), jogador1.centerx, jogador1.y - 12)
        if bloqueando2:
            pygame.draw.arc(tela, (130, 215, 255),
                            (jogador2.x - 12, jogador2.y + 16, 100, 92), 0.3, 2.8, 5)
            desenhar_texto("DEFESA", fonte_pequena, (155, 225, 255), jogador2.centerx, jogador2.y - 12)
        if congelamento[1] > 0:
            pygame.draw.circle(tela, (100, 205, 255), (jogador1.centerx, jogador1.y - 7), 5)
        if congelamento[2] > 0:
            pygame.draw.circle(tela, (100, 205, 255), (jogador2.centerx, jogador2.y - 7), 5)

        # Efeitos visuais da lanca e do fogo.
        desenhar_poderes()
        desenhar_particulas_impacto()

        # Mostra os controles durante a partida.
        desenhar_texto("A/D mover W pulo S defesa J soco U lanca I poder",
                       fonte_controles, BRANCO, 18, 565, centralizado=False)
        if modo_jogo == "dois":
            desenhar_texto("SETAS mover CIMA pulo BAIXO defesa P soco KP1 lanca KP2 poder",
                           fonte_controles, BRANCO, 520, 565, centralizado=False)
        else:
            desenhar_texto("Oponente CPU controlado pelo computador",
                           fonte_controles, BRANCO, 520, 565, centralizado=False)
        nome_lanca1 = (
            "Teleporte" if personagem_raiden(1)
            else "Chute voador" if personagem_liu_kang(1)
            else "Lanca gelo" if personagem_subzero(1)
            else "Corrente"
        )
        nome_poder1 = (
            "Raio" if personagem_raiden(1)
            else "Bola Dragao" if personagem_liu_kang(1)
            else "Bola gelo" if personagem_subzero(1)
            else "Fogo"
        )
        nome_lanca2 = (
            "Teleporte" if personagem_raiden(2)
            else "Chute voador" if personagem_liu_kang(2)
            else "Lanca gelo" if personagem_subzero(2)
            else "Corrente"
        )
        nome_poder2 = (
            "Raio" if personagem_raiden(2)
            else "Bola Dragao" if personagem_liu_kang(2)
            else "Bola gelo" if personagem_subzero(2)
            else "Fogo"
        )
        status1 = f"{nome_lanca1}: {'OK' if recarga_lanca[1] == 0 else '...'}  {nome_poder1}: {'OK' if recarga_fogo[1] == 0 else '...'}"
        status2 = f"{nome_lanca2}: {'OK' if recarga_lanca[2] == 0 else '...'}  {nome_poder2}: {'OK' if recarga_fogo[2] == 0 else '...'}"
        desenhar_texto(status1, fonte_pequena, AMARELO, 180, 92)
        desenhar_texto(status2, fonte_pequena, AMARELO, 820, 92)
        desenhar_texto("ESC pausa", fonte_pequena, BRANCO, 500, 585)

        # Verifica se algum jogador ficou sem vida.
        if vida_jogador1 <= 0:
            vencedor = NOME_JOGADOR2
            estado_jogo = "resultado"
        elif vida_jogador2 <= 0:
            vencedor = NOME_JOGADOR1
            estado_jogo = "resultado"
        elif tempo_restante <= 0:
            if vida_jogador1 == vida_jogador2:
                vencedor = "EMPATE"
            else:
                vencedor = NOME_JOGADOR1 if vida_jogador1 > vida_jogador2 else NOME_JOGADOR2
            estado_jogo = "resultado"

    elif estado_jogo == "pausado":
        if tela_pausa is not None:
            tela.blit(tela_pausa, (0, 0))
        sombreado = pygame.Surface((LARGURA, ALTURA), pygame.SRCALPHA)
        sombreado.fill((0, 0, 0, 155))
        tela.blit(sombreado, (0, 0))
        pygame.draw.rect(tela, (12, 10, 18), (300, 215, 400, 150), border_radius=18)
        pygame.draw.rect(tela, AMARELO, (300, 215, 400, 150), 3, border_radius=18)
        desenhar_texto("JOGO PAUSADO", fonte_titulo, AMARELO, 500, 270)
        desenhar_texto("ESC - CONTINUAR", fonte_normal, BRANCO, 500, 325)

    # 9.4. TELA DE VITORIA E DERROTA
    elif estado_jogo == "resultado":
        desenhar_cenario()
        pygame.draw.rect(tela, (12, 10, 18), (190, 165, 620, 250), border_radius=18)
        pygame.draw.rect(tela, AMARELO, (190, 165, 620, 250), 3, border_radius=18)
        desenhar_texto("FIM DE LUTA!", fonte_titulo, AMARELO, 500, 225)
        texto_resultado = vencedor if vencedor == "EMPATE" else f"{vencedor} VENCEU!"
        desenhar_texto(texto_resultado, fonte_media, BRANCO, 500, 290)
        desenhar_texto("ENTER - JOGAR NOVAMENTE", fonte_normal, BRANCO, 500, 345)
        desenhar_texto("ESC - VOLTAR AO MENU", fonte_normal, (190, 190, 200), 500, 385)

    # 10. ATUALIZACAO DA TELA E CONTROLE DA VELOCIDADE
    pygame.display.flip()
    relogio.tick(60)

# 11. FINALIZACAO DO JOGO
pygame.quit()
sys.exit()

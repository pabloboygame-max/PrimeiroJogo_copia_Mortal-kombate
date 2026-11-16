
import sys
from pathlib import Path

import pygame

pygame.init()

LARGURA = 1000
ALTURA = 600

PRETO = (12, 10, 18)
BRANCO = (245, 245, 245)
AMARELO = (245, 190, 55)
AZUL = (40, 110, 220)
VERMELHO = (190, 35, 45)

tela = pygame.display.set_mode((LARGURA, ALTURA))
pygame.display.set_caption("Arena Mortal - Prototipo")
relogio = pygame.time.Clock()

pasta_sprites = Path(__file__).resolve().parent / "sprites" / "quadros_separados"


def carregar_quadro(numero):
    caminho = pasta_sprites / f"quadro_{numero:03}.png"
    if not caminho.exists():
        return None
    imagem = pygame.image.load(str(caminho)).convert_alpha()
    return pygame.transform.scale(imagem, (140, 140))


def carregar_animacao(inicio, fim):
    quadros = []
    for numero in range(inicio, fim + 1):
        imagem = carregar_quadro(numero)
        if imagem is not None:
            quadros.append(imagem)
    return quadros


animacao_parado = carregar_animacao(3, 9)
animacao_andando = carregar_animacao(10, 18)
animacao_soco = carregar_animacao(39, 58)

if not animacao_parado:
    print("Aviso: sprites nao encontrados. O jogo usara lutadores provisórios.")

jogador1 = pygame.Rect(180, 430, 80, 120)
jogador2 = pygame.Rect(740, 430, 80, 120)

vida_jogador1 = 100
vida_jogador2 = 100
velocidade_jogador = 5

direcao_jogador1 = 1
direcao_jogador2 = -1

indice_parado = 0
indice_andando = 0
indice_soco1 = 0
indice_soco2 = 0
contador_animacao = 0

atacando1 = False
atacando2 = False
contador_soco1 = 0
contador_soco2 = 0
acertou1 = False
acertou2 = False
invulneravel1 = 0
invulneravel2 = 0


def desenhar_texto(texto, fonte, cor, x, y):
    imagem = fonte.render(texto, True, cor)
    rect = imagem.get_rect(center=(x, y))
    tela.blit(imagem, rect)


def desenhar_cenario():
    tela.fill((18, 18, 28))
    pygame.draw.rect(tela, (35, 30, 46), (0, 0, LARGURA, 330))
    pygame.draw.rect(tela, (80, 50, 45), (0, 330, LARGURA, ALTURA - 330))

    for x in range(0, LARGURA, 110):
        pygame.draw.rect(tela, (25, 22, 38), (x, 140, 80, 190))

    pygame.draw.rect(tela, (36, 32, 38), (0, 470, LARGURA, ALTURA - 470))
    pygame.draw.line(tela, (180, 120, 65), (0, 470), (LARGURA, 470), 5)


def desenhar_lutador_provisorio(retangulo, cor, direcao):
    x = retangulo.centerx
    y = retangulo.y
    pygame.draw.ellipse(tela, (10, 10, 10), (retangulo.x - 8, retangulo.bottom - 12, 95, 20))
    pygame.draw.circle(tela, cor, (x, y + 22), 19)
    pygame.draw.rect(tela, cor, (x - 19, y + 42, 38, 48), border_radius=8)
    pygame.draw.line(tela, cor, (x - 12, y + 52), (x - 30 * direcao, y + 85), 10)
    pygame.draw.line(tela, cor, (x + 12, y + 52), (x + 30 * direcao, y + 82), 10)
    pygame.draw.line(tela, cor, (x - 8, y + 87), (x - 15, y + 120), 12)
    pygame.draw.line(tela, cor, (x + 8, y + 87), (x + 15, y + 120), 12)


def desenhar_personagem(retangulo, imagem, direcao, cor):
    if imagem is None:
        desenhar_lutador_provisorio(retangulo, cor, direcao)
        return

    sprite = imagem
    if direcao == -1:
        sprite = pygame.transform.flip(sprite, True, False)
    tela.blit(sprite, (retangulo.centerx - 72, retangulo.bottom - 145))


def desenhar_barra_vida(x, y, valor, cor):
    pygame.draw.rect(tela, (55, 20, 25), (x, y, 360, 28), border_radius=5)
    largura = max(0, int(356 * valor / 100))
    pygame.draw.rect(tela, cor, (x + 2, y + 2, largura, 24), border_radius=4)
    pygame.draw.rect(tela, BRANCO, (x, y, 360, 28), 2, border_radius=5)


def iniciar_ataque(jogador):
    global atacando1, atacando2, contador_soco1, contador_soco2, indice_soco1, indice_soco2, acertou1, acertou2
    if jogador == 1 and not atacando1:
        atacando1 = True
        contador_soco1 = 0
        indice_soco1 = 0
        acertou1 = False
    elif jogador == 2 and not atacando2:
        atacando2 = True
        contador_soco2 = 0
        indice_soco2 = 0
        acertou2 = False


while True:
    for evento in pygame.event.get():
        if evento.type == pygame.QUIT:
            pygame.quit()
            sys.exit()

        if evento.type == pygame.KEYDOWN:
            if evento.key == pygame.K_j:
                iniciar_ataque(1)
            if evento.key == pygame.K_p:
                iniciar_ataque(2)

    teclas = pygame.key.get_pressed()

    if not atacando1:
        if teclas[pygame.K_a]:
            jogador1.x -= velocidade_jogador
            direcao_jogador1 = -1
        if teclas[pygame.K_d]:
            jogador1.x += velocidade_jogador
            direcao_jogador1 = 1

    if not atacando2:
        if teclas[pygame.K_LEFT]:
            jogador2.x -= velocidade_jogador
            direcao_jogador2 = -1
        if teclas[pygame.K_RIGHT]:
            jogador2.x += velocidade_jogador
            direcao_jogador2 = 1

    jogador1.left = max(0, jogador1.left)
    jogador1.right = min(LARGURA, jogador1.right)
    jogador2.left = max(0, jogador2.left)
    jogador2.right = min(LARGURA, jogador2.right)

    if atacando1:
        contador_soco1 += 1
        if animacao_soco:
            indice_soco1 = min(contador_soco1 // 4, len(animacao_soco) - 1)
        if contador_soco1 >= max(20, len(animacao_soco) * 4):
            atacando1 = False
            contador_soco1 = 0
            indice_soco1 = 0

        distancia = abs(jogador1.centerx - jogador2.centerx)
        alvo_na_frente = (jogador2.centerx - jogador1.centerx) * direcao_jogador1 > 0
        if not acertou1 and 8 <= contador_soco1 <= 24:
            if distancia < 145 and alvo_na_frente and invulneravel2 == 0:
                vida_jogador2 = max(0, vida_jogador2 - 10)
                invulneravel2 = 35
                acertou1 = True

    if atacando2:
        contador_soco2 += 1
        if animacao_soco:
            indice_soco2 = min(contador_soco2 // 4, len(animacao_soco) - 1)
        if contador_soco2 >= max(20, len(animacao_soco) * 4):
            atacando2 = False
            contador_soco2 = 0
            indice_soco2 = 0

        distancia = abs(jogador2.centerx - jogador1.centerx)
        alvo_na_frente = (jogador1.centerx - jogador2.centerx) * direcao_jogador2 > 0
        if not acertou2 and 8 <= contador_soco2 <= 24:
            if distancia < 145 and alvo_na_frente and invulneravel1 == 0:
                vida_jogador1 = max(0, vida_jogador1 - 10)
                invulneravel1 = 35
                acertou2 = True

    if invulneravel1 > 0:
        invulneravel1 -= 1
    if invulneravel2 > 0:
        invulneravel2 -= 1

    contador_animacao += 1
    if contador_animacao >= 8:
        contador_animacao = 0
        if animacao_parado:
            indice_parado = (indice_parado + 1) % len(animacao_parado)
        if animacao_andando:
            indice_andando = (indice_andando + 1) % len(animacao_andando)

    desenhar_cenario()

    fonte_botoes = pygame.font.SysFont("arial", 18)
    desenhar_texto("SCORPION", fonte_botoes, AMARELO, 180, 35)
    desenhar_texto("DESAFIANTE", fonte_botoes, AZUL, 820, 35)
    desenhar_barra_vida(35, 55, vida_jogador1, VERMELHO)
    desenhar_barra_vida(605, 55, vida_jogador2, AZUL)

    andando1 = teclas[pygame.K_a] or teclas[pygame.K_d]
    if atacando1 and animacao_soco:
        imagem1 = animacao_soco[min(indice_soco1, len(animacao_soco) - 1)]
    elif andando1 and animacao_andando:
        imagem1 = animacao_andando[indice_andando]
    elif animacao_parado:
        imagem1 = animacao_parado[indice_parado]
    else:
        imagem1 = None

    andando2 = teclas[pygame.K_LEFT] or teclas[pygame.K_RIGHT]
    if atacando2 and animacao_soco:
        imagem2 = animacao_soco[min(indice_soco2, len(animacao_soco) - 1)]
    elif andando2 and animacao_andando:
        imagem2 = animacao_andando[indice_andando]
    elif animacao_parado:
        imagem2 = animacao_parado[indice_parado]
    else:
        imagem2 = None

    desenhar_personagem(jogador1, imagem1, direcao_jogador1, (205, 115, 35))
    if imagem2 is not None:
        imagem2_azul = imagem2.copy()
        imagem2_azul.fill((80, 145, 255, 255), special_flags=pygame.BLEND_RGBA_MULT)
        if direcao_jogador2 == 1:
            imagem2_azul = pygame.transform.flip(imagem2_azul, True, False)
        tela.blit(imagem2_azul, (jogador2.centerx - 72, jogador2.bottom - 145))
    else:
        desenhar_lutador_provisorio(jogador2, AZUL, direcao_jogador2)

    desenhar_texto("A/D mover | J soco", pygame.font.SysFont("arial", 18), BRANCO, 175, 570)
    desenhar_texto("Setas mover | P soco", pygame.font.SysFont("arial", 18), BRANCO, 825, 570)

    if vida_jogador1 <= 0:
        desenhar_texto("JOGADOR 2 VENCEU!", pygame.font.SysFont("arial", 40, bold=True), AMARELO, LARGURA // 2, ALTURA // 2)
        pygame.display.flip()
        pygame.time.wait(1500)
        vida_jogador1 = 100
        vida_jogador2 = 100
        jogador1.x = 180
        jogador2.x = 740
        atacando1 = False
        atacando2 = False
    elif vida_jogador2 <= 0:
        desenhar_texto("JOGADOR 1 VENCEU!", pygame.font.SysFont("arial", 40, bold=True), AMARELO, LARGURA // 2, ALTURA // 2)
        pygame.display.flip()
        pygame.time.wait(1500)
        vida_jogador1 = 100
        vida_jogador2 = 100
        jogador1.x = 180
        jogador2.x = 740
        atacando1 = False
        atacando2 = False

    pygame.display.flip()
    relogio.tick(60)

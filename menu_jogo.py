import math
import random
import sys
from pathlib import Path

import pygame

# ------------------------------------------------------------
#  MENU ESTILO MORTAL KOMBAT  -  Pygame
#  Telas: MENU -> (OPÇÕES) -> SELEÇÃO DE PERSONAGEM -> LUTA
# ------------------------------------------------------------

W, H = 1000, 600
FPS = 60

BLACK = (0, 0, 0)
WHITE = (240, 240, 240)
RED = (200, 20, 20)
DARK_RED = (90, 0, 0)
GOLD = (230, 180, 40)
GRAY = (130, 130, 130)
BLUE = (60, 120, 255)
BASE_DIR = Path(__file__).resolve().parent

# Personagens: nome, cor principal, cor de destaque
# Se existir assets/personagens/<nome em minúsculo>.png, a imagem é usada no lugar do desenho.
PERSONAGENS = [
    ("Scorpion",   (230, 190, 20),  (30, 30, 30)),
    ("Sub-Zero",   (40, 110, 220),  (200, 230, 255)),
    ("Liu Kang",   (205, 70, 35),   (255, 190, 75)),
    ("Raiden",     (225, 220, 190), (110, 190, 255)),
]

MENU_ITENS = ["JOGAR SOLO", "JOGAR EM 2 JOGADORES", "OPÇÕES", "SAIR"]
DIFICULDADES = ["FÁCIL", "NORMAL", "DIFÍCIL"]


def tentar_imagem(nome):
    """Carrega assets/personagens/<nome>.png se existir."""
    nome_arquivo = nome.lower().replace(" ", "_").replace("-", "") + ".png"
    caminhos = [BASE_DIR / "assets" / "personagens" / nome_arquivo]
    sprites = BASE_DIR / "sprites"
    if nome == "Scorpion":
        caminhos.append(sprites / "quadros_separados" / "quadro_003.png")
    elif nome == "Sub-Zero":
        caminhos.append(sprites / "subzero_animacao" / "parado_00.png")
    elif nome == "Liu Kang":
        caminhos.append(sprites / "liu_kang_animacao" / "parado_00.png")
    elif nome == "Raiden":
        caminhos.append(sprites / "raiden_animacao" / "parado_00.png")

    for caminho in caminhos:
        if not caminho.exists():
            continue
        try:
            imagem = pygame.image.load(str(caminho)).convert_alpha()
            area_visivel = imagem.get_bounding_rect()
            if area_visivel.width == 0 or area_visivel.height == 0:
                raise ValueError(f"Sprite sem pixels visiveis: {caminho}")
            return imagem.subsurface(area_visivel).copy()
        except pygame.error:
            continue
    return None


class Jogo:
    def __init__(self, tela=None):
        pygame.init()
        if tela is None:
            pygame.display.set_caption("MORTAL KOMBAT - Protótipo")
            tela = pygame.display.set_mode((W, H), pygame.SCALED)
        self.tela = tela
        self.clock = pygame.time.Clock()

        self.f_titulo = pygame.font.SysFont("impact", 84)
        self.f_menu = pygame.font.SysFont("impact", 38)
        self.f_med = pygame.font.SysFont("impact", 28)
        self.f_peq = pygame.font.SysFont("arial", 18, bold=True)

        self.estado = "menu"      # menu | opcoes | selecao | luta
        self.modo = "solo"        # solo | dois
        self.menu_idx = 0
        self.opc_idx = 0
        self.config = {"volume": 7, "tela_cheia": False, "dificuldade": 1}

        self.p1 = 0
        self.p2 = 1
        self.p1_ok = False
        self.p2_ok = False
        self.oponente = None
        self.t = 0.0
        self.pronto = False

        self.imagens = {p[0]: tentar_imagem(p[0]) for p in PERSONAGENS}
        self.brasas = [self.nova_brasa(True) for _ in range(70)]

    # ------------------------------------------------------------
    #  Utilidades de desenho
    # ------------------------------------------------------------
    def nova_brasa(self, inicio=False):
        return [random.uniform(0, W), random.uniform(0, H) if inicio else H + 10,
                random.uniform(0.4, 1.8), random.uniform(1, 3)]

    def texto(self, txt, fonte, cor, centro=None, topo_esq=None, sombra=True):
        img = fonte.render(txt, True, cor)
        rect = img.get_rect()
        if centro:
            rect.center = centro
        if topo_esq:
            rect.topleft = topo_esq
        if sombra:
            s = fonte.render(txt, True, BLACK)
            self.tela.blit(s, (rect.x + 3, rect.y + 3))
        self.tela.blit(img, rect)
        return rect

    def fundo(self):
        # degradê vertical preto -> vermelho escuro
        for y in range(0, H, 4):
            k = y / H
            cor = (int(15 + 70 * k), int(0 + 5 * k), int(0 + 5 * k))
            pygame.draw.rect(self.tela, cor, (0, y, W, 4))
        # brasas subindo
        for b in self.brasas:
            b[1] -= b[2]
            b[0] += math.sin(self.t * 2 + b[1] * 0.02) * 0.4
            if b[1] < -10:
                b[0], b[1], b[2], b[3] = self.nova_brasa()
            pygame.draw.circle(self.tela, (255, int(100 + 100 * random.random()), 20), (int(b[0]), int(b[1])), int(b[3]))

    def titulo(self):
        pulso = 1 + 0.03 * math.sin(self.t * 3)
        img = self.f_titulo.render("MORTAL KOMBAT", True, RED)
        img = pygame.transform.rotozoom(img, 0, pulso)
        sombra = self.f_titulo.render("MORTAL KOMBAT", True, BLACK)
        sombra = pygame.transform.rotozoom(sombra, 0, pulso)
        r = img.get_rect(center=(W // 2, 120))
        self.tela.blit(sombra, (r.x + 5, r.y + 5))
        self.tela.blit(img, r)
        self.texto("PROTÓTIPO", self.f_peq, GOLD, centro=(W // 2, 175))

    # ------------------------------------------------------------
    #  MENU PRINCIPAL
    # ------------------------------------------------------------
    def rect_item_menu(self, i):
        return pygame.Rect(W // 2 - 250, 230 + i * 60, 500, 50)

    def desenhar_menu(self):
        self.fundo()
        self.titulo()
        for i, nome in enumerate(MENU_ITENS):
            r = self.rect_item_menu(i)
            sel = i == self.menu_idx
            if sel:
                pygame.draw.rect(self.tela, DARK_RED, r, border_radius=6)
                pygame.draw.rect(self.tela, RED, r, 3, border_radius=6)
            cor = GOLD if sel else WHITE
            self.texto(nome, self.f_menu, cor, centro=r.center)
        self.texto("Setas ou mouse para escolher  |  ENTER ou clique para confirmar",
                   self.f_peq, GRAY, centro=(W // 2, H - 25), sombra=False)

    def ativar_menu(self, i):
        if i == 0:
            self.modo = "solo"
            self.iniciar_selecao()
        elif i == 1:
            self.modo = "dois"
            self.iniciar_selecao()
        elif i == 2:
            self.estado = "opcoes"
            self.opc_idx = 0
        elif i == 3:
            pygame.quit()
            sys.exit()

    def eventos_menu(self, e):
        if e.type == pygame.KEYDOWN:
            if e.key == pygame.K_ESCAPE:
                pygame.quit()
                sys.exit()
            elif e.key in (pygame.K_UP, pygame.K_w):
                self.menu_idx = (self.menu_idx - 1) % len(MENU_ITENS)
            elif e.key in (pygame.K_DOWN, pygame.K_s):
                self.menu_idx = (self.menu_idx + 1) % len(MENU_ITENS)
            elif e.key in (pygame.K_RETURN, pygame.K_SPACE):
                self.ativar_menu(self.menu_idx)
        elif e.type == pygame.MOUSEMOTION:
            for i in range(len(MENU_ITENS)):
                if self.rect_item_menu(i).collidepoint(e.pos):
                    self.menu_idx = i
        elif e.type == pygame.MOUSEBUTTONDOWN and e.button == 1:
            for i in range(len(MENU_ITENS)):
                if self.rect_item_menu(i).collidepoint(e.pos):
                    self.ativar_menu(i)

    # ------------------------------------------------------------
    #  OPÇÕES
    # ------------------------------------------------------------
    def itens_opcoes(self):
        return [
            ("VOLUME", "< " + "|" * self.config["volume"] + "." * (10 - self.config["volume"]) + " >"),
            ("TELA CHEIA", "< " + ("LIGADA" if self.config["tela_cheia"] else "DESLIGADA") + " >"),
            ("DIFICULDADE", "< " + DIFICULDADES[self.config["dificuldade"]] + " >"),
            ("VOLTAR", ""),
        ]

    def rect_item_opc(self, i):
        return pygame.Rect(W // 2 - 330, 190 + i * 70, 660, 55)

    def desenhar_opcoes(self):
        self.fundo()
        self.texto("OPÇÕES", pygame.font.SysFont("impact", 60), RED, centro=(W // 2, 90))
        for i, (nome, valor) in enumerate(self.itens_opcoes()):
            r = self.rect_item_opc(i)
            sel = i == self.opc_idx
            if sel:
                pygame.draw.rect(self.tela, DARK_RED, r, border_radius=6)
                pygame.draw.rect(self.tela, RED, r, 3, border_radius=6)
            cor = GOLD if sel else WHITE
            if valor:
                self.texto(nome, self.f_med, cor, topo_esq=(r.x + 20, r.y + 10))
                rr = self.f_med.render(valor, True, cor)
                self.texto(valor, self.f_med, cor, topo_esq=(r.right - rr.get_width() - 20, r.y + 10))
            else:
                self.texto(nome, self.f_med, cor, centro=r.center)
        self.texto("Setas esquerda/direita alteram  |  ESC volta", self.f_peq, GRAY, centro=(W // 2, H - 25), sombra=False)

    def mudar_opcao(self, direcao):
        if self.opc_idx == 0:
            self.config["volume"] = max(0, min(10, self.config["volume"] + direcao))
            pygame.mixer.music.set_volume(self.config["volume"] / 10) if pygame.mixer.get_init() else None
        elif self.opc_idx == 1:
            self.alternar_tela_cheia()
        elif self.opc_idx == 2:
            self.config["dificuldade"] = (self.config["dificuldade"] + direcao) % len(DIFICULDADES)

    def alternar_tela_cheia(self):
        self.config["tela_cheia"] = not self.config["tela_cheia"]
        pygame.display.toggle_fullscreen()

    def eventos_opcoes(self, e):
        n = len(self.itens_opcoes())
        if e.type == pygame.KEYDOWN:
            if e.key == pygame.K_ESCAPE:
                self.estado = "menu"
            elif e.key in (pygame.K_UP, pygame.K_w):
                self.opc_idx = (self.opc_idx - 1) % n
            elif e.key in (pygame.K_DOWN, pygame.K_s):
                self.opc_idx = (self.opc_idx + 1) % n
            elif e.key in (pygame.K_LEFT, pygame.K_a):
                self.mudar_opcao(-1)
            elif e.key in (pygame.K_RIGHT, pygame.K_d):
                self.mudar_opcao(1)
            elif e.key in (pygame.K_RETURN, pygame.K_SPACE):
                if self.opc_idx == n - 1:
                    self.estado = "menu"
                else:
                    self.mudar_opcao(1)
        elif e.type == pygame.MOUSEMOTION:
            for i in range(n):
                if self.rect_item_opc(i).collidepoint(e.pos):
                    self.opc_idx = i
        elif e.type == pygame.MOUSEBUTTONDOWN and e.button == 1:
            for i in range(n):
                if self.rect_item_opc(i).collidepoint(e.pos):
                    self.opc_idx = i
                    if i == n - 1:
                        self.estado = "menu"
                    else:
                        self.mudar_opcao(1)

    # ------------------------------------------------------------
    #  SELEÇÃO DE PERSONAGEM
    # ------------------------------------------------------------
    COLS = 2
    CW, CH, GAP = 170, 150, 12

    def iniciar_selecao(self):
        self.estado = "selecao"
        self.p1, self.p2 = 0, 1
        self.p1_ok = self.p2_ok = False
        self.oponente = None

    def rect_celula(self, i):
        total_w = self.COLS * self.CW + (self.COLS - 1) * self.GAP
        x0 = (W - total_w) // 2
        y0 = 120
        c, l = i % self.COLS, i // self.COLS
        return pygame.Rect(x0 + c * (self.CW + self.GAP), y0 + l * (self.CH + self.GAP), self.CW, self.CH)

    def mover(self, idx, dx, dy):
        n = len(PERSONAGENS)
        linhas = math.ceil(n / self.COLS)
        c, l = idx % self.COLS, idx // self.COLS
        c = (c + dx) % self.COLS
        l = (l + dy) % linhas
        novo = l * self.COLS + c
        return novo if novo < n else idx

    def desenhar_retrato(self, rect, ch, escurecer=False):
        nome, cor, destaque = ch
        pygame.draw.rect(self.tela, tuple(int(c * 0.35) for c in cor), rect)
        img = self.imagens.get(nome)
        if img:
            esc = min(rect.w / img.get_width(), rect.h / img.get_height())
            img = pygame.transform.smoothscale(img, (int(img.get_width() * esc), int(img.get_height() * esc)))
            self.tela.blit(img, img.get_rect(midbottom=(rect.centerx, rect.bottom - 4)))
        else:
            # silhueta simples (placeholder)
            cx, base = rect.centerx, rect.bottom - 4
            pygame.draw.polygon(self.tela, cor, [(cx - 38, base), (cx - 26, base - 70), (cx + 26, base - 70), (cx + 38, base)])
            pygame.draw.rect(self.tela, destaque, (cx - 26, base - 50, 52, 8))
            pygame.draw.circle(self.tela, cor, (cx, base - 88), 20)
            pygame.draw.rect(self.tela, destaque, (cx - 20, base - 94, 40, 10))
        if escurecer:
            sombra = pygame.Surface(rect.size, pygame.SRCALPHA)
            sombra.fill((0, 0, 0, 120))
            self.tela.blit(sombra, rect.topleft)

    def desenhar_selecao(self):
        self.fundo()
        self.texto("ESCOLHA SEU LUTADOR", pygame.font.SysFont("impact", 52), RED, centro=(W // 2, 60))
        modo_txt = "MODO: SOLO" if self.modo == "solo" else "MODO: 2 JOGADORES"
        self.texto(modo_txt, self.f_peq, GOLD, centro=(W // 2, 98))

        for i, ch in enumerate(PERSONAGENS):
            r = self.rect_celula(i)
            self.desenhar_retrato(r, ch)
            pygame.draw.rect(self.tela, GRAY, r, 2)
            self.texto(ch[0].upper(), self.f_peq, WHITE, centro=(r.centerx, r.bottom - 14), sombra=True)

        # cursores
        pulso = 3 + int(1.5 * math.sin(self.t * 8))
        r1 = self.rect_celula(self.p1)
        pygame.draw.rect(self.tela, RED, r1.inflate(6, 6), pulso if not self.p1_ok else 7)
        self.texto("P1", self.f_peq, RED, topo_esq=(r1.x + 6, r1.y + 4))
        if self.modo == "dois":
            r2 = self.rect_celula(self.p2)
            off = r2.inflate(-8, -8) if self.p2 == self.p1 else r2.inflate(6, 6)
            pygame.draw.rect(self.tela, BLUE, off, pulso if not self.p2_ok else 7)
            self.texto("P2", self.f_peq, BLUE, topo_esq=(r2.right - 28, r2.y + 4))

        # painel inferior
        y = 478
        pygame.draw.line(self.tela, DARK_RED, (60, y - 14), (W - 60, y - 14), 2)
        st1 = "  [OK]" if self.p1_ok else ""
        self.texto("P1: " + PERSONAGENS[self.p1][0].upper() + st1, self.f_med, RED, topo_esq=(70, y))
        if self.modo == "dois":
            st2 = "  [OK]" if self.p2_ok else ""
            txt = "P2: " + PERSONAGENS[self.p2][0].upper() + st2
            w = self.f_med.size(txt)[0]
            self.texto(txt, self.f_med, BLUE, topo_esq=(W - 70 - w, y))
            ajuda = "P1: WASD + F  |  P2: Setas + ENTER  |  escolha lutadores diferentes"
        else:
            ajuda = "Setas/WASD ou mouse  |  ENTER/clique confirma  |  BACKSPACE cancela  |  ESC volta"
        self.texto(ajuda, self.f_peq, GRAY, centro=(W // 2, H - 14), sombra=False)

    def checar_prontos(self):
        if self.modo == "solo" and self.p1_ok:
            opcoes = [i for i in range(len(PERSONAGENS)) if i != self.p1]
            self.oponente = random.choice(opcoes)
            self.p2 = self.oponente
            self.iniciar_luta()
        elif self.modo == "dois" and self.p1_ok and self.p2_ok:
            if self.p1 == self.p2:
                self.p2_ok = False
            else:
                self.iniciar_luta()

    def eventos_selecao(self, e):
        if e.type == pygame.KEYDOWN:
            if e.key == pygame.K_ESCAPE:
                self.estado = "menu"
                return
            if self.modo == "solo":
                if not self.p1_ok:
                    d = {pygame.K_LEFT: (-1, 0), pygame.K_a: (-1, 0), pygame.K_RIGHT: (1, 0), pygame.K_d: (1, 0),
                         pygame.K_UP: (0, -1), pygame.K_w: (0, -1), pygame.K_DOWN: (0, 1), pygame.K_s: (0, 1)}
                    if e.key in d:
                        self.p1 = self.mover(self.p1, *d[e.key])
                    elif e.key in (pygame.K_RETURN, pygame.K_SPACE, pygame.K_f):
                        self.p1_ok = True
                if e.key == pygame.K_BACKSPACE:
                    self.p1_ok = False
            else:
                # Jogador 1: WASD + F
                d1 = {pygame.K_a: (-1, 0), pygame.K_d: (1, 0), pygame.K_w: (0, -1), pygame.K_s: (0, 1)}
                if not self.p1_ok and e.key in d1:
                    self.p1 = self.mover(self.p1, *d1[e.key])
                elif e.key == pygame.K_f:
                    self.p1_ok = not self.p1_ok
                # Jogador 2: setas + ENTER
                d2 = {pygame.K_LEFT: (-1, 0), pygame.K_RIGHT: (1, 0), pygame.K_UP: (0, -1), pygame.K_DOWN: (0, 1)}
                if not self.p2_ok and e.key in d2:
                    self.p2 = self.mover(self.p2, *d2[e.key])
                elif e.key in (pygame.K_RETURN, pygame.K_KP_ENTER):
                    self.p2_ok = not self.p2_ok
            self.checar_prontos()

        elif e.type == pygame.MOUSEMOTION:
            if self.modo == "solo":
                jogador_ativo = 1 if not self.p1_ok else None
            elif not self.p1_ok:
                jogador_ativo = 1
            elif not self.p2_ok:
                jogador_ativo = 2
            else:
                jogador_ativo = None

            if jogador_ativo is None:
                return
            for i in range(len(PERSONAGENS)):
                if self.rect_celula(i).collidepoint(e.pos):
                    if jogador_ativo == 1:
                        self.p1 = i
                    else:
                        self.p2 = i

        elif e.type == pygame.MOUSEBUTTONDOWN and e.button == 1:
            for i in range(len(PERSONAGENS)):
                if self.rect_celula(i).collidepoint(e.pos):
                    if self.modo == "solo":
                        self.p1 = i
                        self.p1_ok = True
                    elif not self.p1_ok:
                        self.p1 = i
                        self.p1_ok = True
                    elif not self.p2_ok:
                        self.p2 = i
                        self.p2_ok = True
                    else:
                        break
            self.checar_prontos()

    # ------------------------------------------------------------
    #  LUTA  (aqui você liga o seu jogo)
    # ------------------------------------------------------------
    def iniciar_luta(self):
        self.estado = "luta"
        self.pronto = True

    def voltar_ao_menu(self):
        self.estado = "menu"
        self.menu_idx = 0
        self.p1_ok = self.p2_ok = False
        self.pronto = False

    def processar_evento(self, evento):
        if self.estado == "menu":
            self.eventos_menu(evento)
        elif self.estado == "opcoes":
            self.eventos_opcoes(evento)
        elif self.estado == "selecao":
            self.eventos_selecao(evento)

    def desenhar(self):
        if self.estado == "menu":
            self.desenhar_menu()
        elif self.estado == "opcoes":
            self.desenhar_opcoes()
        elif self.estado == "selecao":
            self.desenhar_selecao()

    def desenhar_luta(self):
        self.fundo()
        self.texto("PREPARE-SE PARA LUTAR!", pygame.font.SysFont("impact", 56), RED, centro=(W // 2, 80))
        r1 = pygame.Rect(120, 150, 260, 270)
        r2 = pygame.Rect(W - 380, 150, 260, 270)
        self.desenhar_retrato(r1, PERSONAGENS[self.p1])
        self.desenhar_retrato(r2, PERSONAGENS[self.p2])
        pygame.draw.rect(self.tela, RED, r1, 4)
        pygame.draw.rect(self.tela, BLUE if self.modo == "dois" else GRAY, r2, 4)
        self.texto("VS", pygame.font.SysFont("impact", 90), GOLD, centro=(W // 2, 285))
        self.texto("P1 - " + PERSONAGENS[self.p1][0].upper(), self.f_med, RED, centro=(r1.centerx, 450))
        nome2 = ("P2 - " if self.modo == "dois" else "CPU - ") + PERSONAGENS[self.p2][0].upper()
        self.texto(nome2, self.f_med, BLUE if self.modo == "dois" else GRAY, centro=(r2.centerx, 450))
        self.texto("Aqui entra o seu jogo (jogo.py)  |  ESC volta ao menu", self.f_peq, GRAY,
                   centro=(W // 2, H - 20), sombra=False)

    def eventos_luta(self, e):
        if e.type == pygame.KEYDOWN and e.key == pygame.K_ESCAPE:
            self.estado = "menu"

    # ------------------------------------------------------------
    #  LOOP PRINCIPAL
    # ------------------------------------------------------------
    def rodar(self):
        while True:
            dt = self.clock.tick(FPS) / 1000
            self.t += dt
            for e in pygame.event.get():
                if e.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()
                if e.type == pygame.KEYDOWN and e.key == pygame.K_F11:
                    self.alternar_tela_cheia()
                if self.estado == "menu":
                    self.eventos_menu(e)
                elif self.estado == "opcoes":
                    self.eventos_opcoes(e)
                elif self.estado == "selecao":
                    self.eventos_selecao(e)
                elif self.estado == "luta":
                    self.eventos_luta(e)

            if self.pronto:
                return {
                    "modo": self.modo,
                    "jogador1": PERSONAGENS[self.p1][0].upper(),
                    "jogador2": PERSONAGENS[self.p2][0].upper(),
                }
            if self.estado == "menu":
                self.desenhar_menu()
            elif self.estado == "opcoes":
                self.desenhar_opcoes()
            elif self.estado == "selecao":
                self.desenhar_selecao()
            elif self.estado == "luta":
                self.desenhar_luta()
            pygame.display.flip()


if __name__ == "__main__":
    Jogo().rodar()
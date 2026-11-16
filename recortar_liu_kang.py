from pathlib import Path

from PIL import Image


BASE_DIR = Path(__file__).resolve().parent
IMAGEM_ORIGEM = BASE_DIR / "Arcade - Mortal Kombat - Kombatants - Liu Kang.png"
PASTA_DESTINO = BASE_DIR / "sprites" / "liu_kang_animacao"

# Cada quadro do atlas ocupa 230 x 220 pixels, com espacamento horizontal de 4.
ANIMACOES = {
    "parado": (32, 58, 8),
    "andando": (2138, 58, 9),
    "soco": (1202, 580, 9),
    "chute": (32, 1574, 7),
}
LARGURA_QUADRO = 230
ALTURA_QUADRO = 220
PASSO_HORIZONTAL = 234
COR_FUNDO = (165, 231, 255)


def remover_fundo(imagem):
    pixels = imagem.load()
    for y in range(imagem.height):
        for x in range(imagem.width):
            vermelho, verde, azul, _ = pixels[x, y]
            if (
                abs(vermelho - COR_FUNDO[0]) < 45
                and abs(verde - COR_FUNDO[1]) < 35
                and abs(azul - COR_FUNDO[2]) < 35
            ):
                pixels[x, y] = (0, 0, 0, 0)
    return imagem


def main():
    if not IMAGEM_ORIGEM.is_file():
        raise FileNotFoundError(f"Imagem do Liu Kang nao encontrada: {IMAGEM_ORIGEM}")

    atlas = Image.open(IMAGEM_ORIGEM).convert("RGBA")
    PASTA_DESTINO.mkdir(parents=True, exist_ok=True)

    total = 0
    for nome, (inicio_x, inicio_y, quantidade) in ANIMACOES.items():
        for indice in range(quantidade):
            esquerda = inicio_x + indice * PASSO_HORIZONTAL
            quadro = atlas.crop((
                esquerda + 4,
                inicio_y + 4,
                esquerda + LARGURA_QUADRO - 4,
                inicio_y + ALTURA_QUADRO - 4,
            ))
            quadro = remover_fundo(quadro)
            area_visivel = quadro.getchannel("A").getbbox()
            if area_visivel is None:
                raise ValueError(f"Quadro vazio no atlas: {nome}_{indice:02}")

            caminho = PASTA_DESTINO / f"{nome}_{indice:02}.png"
            quadro.save(caminho)
            total += 1

    print(f"Quadros do Liu Kang recortados: {total}")
    print(f"Pasta: {PASTA_DESTINO}")


if __name__ == "__main__":
    main()

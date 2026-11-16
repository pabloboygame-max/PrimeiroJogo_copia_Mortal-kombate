from pathlib import Path

from PIL import Image


BASE_DIR = Path(__file__).resolve().parent
IMAGEM_ORIGEM = BASE_DIR / "Arcade - Mortal Kombat - Kombatants - Raiden.png"
PASTA_DESTINO = BASE_DIR / "sprites" / "raiden_animacao"

# Coordenadas das faixas de sprites no atlas, em pixels.
ANIMACOES = {
    "parado": (32, 58, 10),
    "andando": (2606, 58, 9),
    "soco": (32, 1288, 5),
    "chute": (32, 2282, 7),
}
LARGURA_QUADRO = 230
ALTURA_QUADRO = 220
PASSO_HORIZONTAL = 234
COR_FUNDO_AZUL = (165, 231, 255)
COR_FUNDO_VERMELHA = (82, 1, 1)


def remover_fundo(imagem):
    pixels = imagem.load()
    for y in range(imagem.height):
        for x in range(imagem.width):
            vermelho, verde, azul, _ = pixels[x, y]
            fundo_azul = (
                abs(vermelho - COR_FUNDO_AZUL[0]) < 45
                and abs(verde - COR_FUNDO_AZUL[1]) < 35
                and abs(azul - COR_FUNDO_AZUL[2]) < 35
            )
            fundo_vermelho = (
                abs(vermelho - COR_FUNDO_VERMELHA[0]) < 20
                and verde < 20
                and azul < 20
            )
            if fundo_azul or fundo_vermelho:
                pixels[x, y] = (0, 0, 0, 0)
    return imagem


def main():
    if not IMAGEM_ORIGEM.is_file():
        raise FileNotFoundError(f"Imagem do Raiden nao encontrada: {IMAGEM_ORIGEM}")

    atlas = Image.open(IMAGEM_ORIGEM).convert("RGBA")
    PASTA_DESTINO.mkdir(parents=True, exist_ok=True)
    for indice in range(10):
        quadro_especial = PASTA_DESTINO / f"especial_{indice:02}.png"
        if quadro_especial.exists():
            quadro_especial.unlink()

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
            if quadro.getchannel("A").getbbox() is None:
                raise ValueError(f"Quadro vazio no atlas: {nome}_{indice:02}")

            quadro.save(PASTA_DESTINO / f"{nome}_{indice:02}.png")
            total += 1

    print(f"Quadros do Raiden recortados: {total}")
    print(f"Pasta: {PASTA_DESTINO}")


if __name__ == "__main__":
    main()

from PIL import Image
from pathlib import Path
import numpy as np

origem = Path("sprites/linhas")
destino = Path("sprites/quadros_separados")
destino.mkdir(parents=True, exist_ok=True)

total = 0

for arquivo in sorted(origem.glob("linha_*.png")):
    imagem = Image.open(arquivo).convert("RGBA")
    alpha = np.array(imagem.getchannel("A"))

    # Colunas que possuem pixels visíveis
    ocupadas = np.sum(alpha > 0, axis=0) > 0

    grupos = []
    inicio = None

    for x, ocupado in enumerate(ocupadas):
        if ocupado and inicio is None:
            inicio = x
        elif not ocupado and inicio is not None:
            if x - inicio >= 10:
                grupos.append((inicio, x))
            inicio = None

    if inicio is not None:
        grupos.append((inicio, imagem.width))

    for x1, x2 in grupos:
        quadro = imagem.crop((x1, 0, x2, imagem.height))
        caixa = quadro.getchannel("A").getbbox()

        if caixa:
            quadro = quadro.crop(caixa)
            total += 1
            quadro.save(destino / f"quadro_{total:03}.png")

print("Quadros separados:", total)
print("Pasta:", destino)
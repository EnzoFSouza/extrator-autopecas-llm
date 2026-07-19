import json

DIRETORIO_DADOS = "data/"
ARQUIVO = f"{DIRETORIO_DADOS}dados_brutos.txt"  # uma linha = um texto de anuncio

def extrair_textos_de_arquivo(caminho: str) -> list[str]:
    """
    Extrai textos de anuncio de um arquivo.
    Formato: "<texto>" puro, uma linha por anuncio.
    """
    textos = []
    with open(caminho, encoding="utf-8") as f:
        linhas = f.readlines()

    for linha in linhas:
        linha = linha.strip()
        if not linha:
            continue  # ignora linhas em branco
        textos.append(linha)

    return textos


def main():
    textos = extrair_textos_de_arquivo(ARQUIVO)
    print(f"{ARQUIVO}: {len(textos)} linhas lidas")

    # Deduplica mantendo a ordem de primeira aparicao
    # rede de seguranca barata contra duplicata acidental de copiar/colar
    vistos = set()
    textos_unicos = []
    for t in textos:
        if t not in vistos:
            vistos.add(t)
            textos_unicos.append(t)

    duplicatas = len(textos) - len(textos_unicos)
    print(f"Total unico: {len(textos_unicos)} (duplicatas removidas: {duplicatas})")

    with open(f"{DIRETORIO_DADOS}textos_limpos.json", "w", encoding="utf-8") as f:
        json.dump(textos_unicos, f, ensure_ascii=False, indent=2)

    print("\n--- Amostra (ultimos 5) ---")
    for t in textos_unicos[-5:]:
        print("-", t)

if __name__ == "__main__":
    main()
import json
import random
from collections import Counter

SEED = 42
PROPORCAO_TESTE = 0.2

DIRETORIO = "data/"
ARQUIVO_ENTRADA = f"{DIRETORIO}dataset_candidato.json"
ARQUIVO_TREINO = f"{DIRETORIO}treino.json"
ARQUIVO_TESTE = f"{DIRETORIO}teste.json"

def main():
    random.seed(SEED)

    with open(ARQUIVO_ENTRADA, encoding="utf-8") as f:
        dataset = json.load(f)

    # Remove qualquer metadado de revisao (ex: _revisar_multiplos_modelos)
    # que nao deve ir para treino/teste
    dataset_limpo = []
    for item in dataset:
        dataset_limpo.append({
            "texto": item["texto"],
            "extracao": item["extracao"],
        })

    indices = list(range(len(dataset_limpo)))
    random.shuffle(indices)

    n_teste = round(len(dataset_limpo) * PROPORCAO_TESTE)
    indices_teste = set(indices[:n_teste])

    treino = [dataset_limpo[i] for i in range(len(dataset_limpo)) if i not in indices_teste]
    teste = [dataset_limpo[i] for i in range(len(dataset_limpo)) if i in indices_teste]

    print(f"Total: {len(dataset_limpo)}")
    print(f"Treino: {len(treino)}")
    print(f"Teste: {len(teste)}")

    with open(ARQUIVO_TREINO, "w", encoding="utf-8") as f:
        json.dump(treino, f, ensure_ascii=False, indent=2)

    with open(ARQUIVO_TESTE, "w", encoding="utf-8") as f:
        json.dump(teste, f, ensure_ascii=False, indent=2)

    # Checagem de sanidade: distribuicao de categorias em cada split
    cat_treino = Counter(d["extracao"].get("categoria") for d in treino)
    cat_teste = Counter(d["extracao"].get("categoria") for d in teste)

    print("\nCategorias no treino:", dict(cat_treino))
    print("Categorias no teste:", dict(cat_teste))


if __name__ == "__main__":
    main()
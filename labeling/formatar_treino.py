import json

DIRETORIO = "data/"
ARQUIVO_TREINO_ENTRADA = f"{DIRETORIO}treino.json"
ARQUIVO_JSONL_SAIDA = f"{DIRETORIO}treino_formatado.jsonl"

SYSTEM_PROMPT = (
    "Voce e um sistema de extracao de informacoes de anuncios de pecas automotivas. "
    "Dado o texto de um anuncio, extraia os seguintes campos em formato JSON: "
    "categoria, marca_veiculo, modelo_veiculo, ano_compativel, posicao. "
    "Se um campo nao estiver presente no texto, retorne null para ele."
)

def main():
    with open(ARQUIVO_TREINO_ENTRADA, encoding="utf-8") as f:
        treino = json.load(f)

    exemplos_formatados = []
    for item in treino:
        resposta_json = json.dumps(item["extracao"], ensure_ascii=False)
        exemplo = {
            "messages": [
                {"role": "system", "content": SYSTEM_PROMPT},
                {"role": "user", "content": item["texto"]},
                {"role": "assistant", "content": resposta_json},
            ]
        }
        exemplos_formatados.append(exemplo)

    # JSONL: um objeto JSON por linha, sem colchete envolvendo tudo
    with open(ARQUIVO_JSONL_SAIDA, "w", encoding="utf-8") as f:
        for ex in exemplos_formatados:
            f.write(json.dumps(ex, ensure_ascii=False) + "\n")

    print(f"Total formatado: {len(exemplos_formatados)}")
    print(f"Salvo em: {ARQUIVO_JSONL_SAIDA}")
    print("\n--- Preview do primeiro exemplo ---")
    print(json.dumps(exemplos_formatados[0], ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
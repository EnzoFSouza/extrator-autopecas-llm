import json
import unicodedata

#útil tanto para "resultados_baseline.json" ou "resultados_finetuned.json")
DIRETORIO = "resultados/"
ARQUIVO_RESULTADOS = f"{DIRETORIO}resultados_baseline.json"
ARQUIVO_METRICAS_SAIDA = f"{DIRETORIO}metricas_baseline.json"

CAMPOS = ["categoria", "marca_veiculo", "modelo_veiculo", "ano_compativel", "posicao"]


def remover_acentos(s):
    return ''.join(c for c in unicodedata.normalize('NFD', s) if unicodedata.category(c) != 'Mn')


def normalizar(valor):
    if valor is None:
        return None
    if isinstance(valor, list):
        valor = " ".join(str(v) for v in valor)
    return remover_acentos(str(valor)).strip().lower()


def bate_exato(esperado, gerado):
    return esperado == gerado


def bate_tolerante(esperado, gerado):
    """Considera acerto se um valor esta contido no outro (tolera plural,
    tolera quando o modelo gerou palavra a mais/a menos)."""
    if esperado is None or gerado is None:
        return esperado == gerado
    return esperado in gerado or gerado in esperado


def main():
    with open(ARQUIVO_RESULTADOS, encoding="utf-8") as f:
        resultados = json.load(f)

    n = len(resultados)
    acertos_exato = {c: 0 for c in CAMPOS}
    acertos_tolerante = {c: 0 for c in CAMPOS}
    falhas_parse = 0

    for r in resultados:
        if r["gerado"] is None:
            falhas_parse += 1
            continue
        for campo in CAMPOS:
            esperado = normalizar(r["esperado"].get(campo))
            gerado = normalizar(r["gerado"].get(campo))
            if bate_exato(esperado, gerado):
                acertos_exato[campo] += 1
            if bate_tolerante(esperado, gerado):
                acertos_tolerante[campo] += 1

    print(f"Total de exemplos: {n}")
    print(f"Falhas de parsing JSON: {falhas_parse}/{n}")
    print(f"\n{'Campo':<18} {'Exato':<14} {'Tolerante (substring)'}")
    for campo in CAMPOS:
        e, t = acertos_exato[campo], acertos_tolerante[campo]
        print(f"{campo:<18} {e}/{n} ({100*e/n:.1f}%){'':<4} {t}/{n} ({100*t/n:.1f}%)")

    metricas = {
        "total_exemplos": n,
        "falhas_parse": falhas_parse,
        "exato": acertos_exato,
        "tolerante": acertos_tolerante,
    }
    with open(ARQUIVO_METRICAS_SAIDA, "w", encoding="utf-8") as f:
        json.dump(metricas, f, ensure_ascii=False, indent=2)
    print(f"\nMétricas salvas em: {ARQUIVO_METRICAS_SAIDA}")


if __name__ == "__main__":
    main()
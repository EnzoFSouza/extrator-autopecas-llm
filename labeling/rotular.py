import re
import json

DIRETORIO_DADOS = "data/"

with open(f'{DIRETORIO_DADOS}textos_limpos.json', encoding='utf-8') as f:
    textos = json.load(f)

# Dicionários de domínio (regras simples, revisáveis)
CATEGORIAS = {
    "pastilha de freio": ["pastilha"],
    "amortecedor": ["amortecedor"],
    "suspensao": ["suspens"],
    "volante": ["volante"],
    "lanterna": ["lanterna"],
    "farol": ["farol"],
    "comando de ar": ["comando de ar", "comando ar", "comando controle ar"],
    "alavanca de freio": ["alavanca"],
    "disco de freio": ["disco"],
    "bandeja de suspensao": ["bandeja"],
    "mola": ["mola"],
    "bucha": ["bucha"],
    "coxim": ["coxim", "coxins"],
    "pivo": ["pivo", "pivô"],
}

MARCAS = {
    "Chevrolet": ["chevrolet", "gm ", " gm"],
    "Volkswagen": ["volkswagen", "vw "],
    "Fiat": ["fiat"],
    "Ford": ["ford"],
    "Toyota": ["toyota"],
    "Honda": ["honda"],
    "Renault": ["renault"],
    "Nissan": ["nissan"],
    "Hyundai": ["hyundai"],
    "Jeep": ["jeep"],
    "Kia": ["kia"],
    "Peugeot": ["peugeot"],
    "Citroen": ["citroen", "citroën"],
    "Mitsubishi": ["mitsubishi"],
}

MODELOS = [
    "Corolla", "Fiesta", "Ecosport", "Doblo", "Doblò", "Captiva", "Punto", "Civic",
    "Duster", "Captur", "Gol", "Onix", "Prisma", "Cobalt", "Astra", "Palio",
    "Siena", "Strada", "Kombi", "Tracker", "Hb20", "Renegade", "Compass",
    "Commander", "Sw4", "Master", "Polo", "Fox", "Spacefox", "Nivus",
    "Virtus", "T-cross", "Kicks", "Golf", "Kadett", "Monza", "Corsa",
    "Celta", "Voyage", "Hilux", "Spin", "Saveiro", "Wind", "Cruze",
    "Classic", "Bola", "S10", "Uno", "Fiorino", "Toro", "L200", "Triton",
    "Outlander", "Ka", "Etios", "Montana", "Linea", "Sandero", "Stepway",
    "Parati", "Crossfox", "Sportline",
]

def extrair_categoria(texto_lower):
    for cat, termos in CATEGORIAS.items():
        for termo in termos:
            if termo in texto_lower:
                return cat
    return None

def extrair_marca(texto_lower):
    for marca, termos in MARCAS.items():
        for termo in termos:
            if termo in texto_lower:
                return marca
    return None

def extrair_modelo(texto):
    """
    Retorna o PRIMEIRO modelo citado no texto (por posição, não por ordem
    da lista MODELOS). Também retorna a lista completa de modelos encontrados,
    para documentar casos de compatibilidade múltipla.
    """
    ocorrencias = []
    for modelo in MODELOS:
        m = re.search(r'\b' + re.escape(modelo) + r'\b', texto, re.IGNORECASE)
        if m:
            ocorrencias.append((m.start(), modelo))

    if not ocorrencias:
        return None, []

    ocorrencias.sort(key=lambda x: x[0])
    todos_modelos = [modelo for _, modelo in ocorrencias]
    primeiro_modelo = ocorrencias[0][1]
    return primeiro_modelo, todos_modelos

def extrair_posicao(texto_lower):
    tem_dianteira = "diant" in texto_lower
    tem_traseira = "tras" in texto_lower
    tem_direita = "direit" in texto_lower
    tem_esquerda = "esquerd" in texto_lower

    posicoes = []
    if tem_dianteira: posicoes.append("dianteira")
    if tem_traseira: posicoes.append("traseira")
    if tem_direita: posicoes.append("direita")
    if tem_esquerda: posicoes.append("esquerda")

    if not posicoes:
        return None
    return " e ".join(posicoes) if len(posicoes) > 1 else posicoes[0]

def extrair_ano(texto):
    """
    Captura sequências completas de anos, não só o primeiro par.
    Cobre casos como "2015 A 2018", "2014/19" e também listas soltas
    tipo "2009 2010 11 12 13" (comum em título de anúncio real).
    """
    # Um ano completo (19xx/20xx), seguido de zero ou mais continuações
    # (separadas por espaço, "/", "a", "à") que podem ser ano completo
    # ou só os 2 últimos dígitos do ano.
    padrao = r'((?:19|20)\d{2})((?:\s*[aàA/-]?\s*\d{2,4})*)'
    m = re.search(padrao, texto)
    if not m:
        return None

    trecho_completo = m.group(0)
    primeiro_ano = m.group(1)
    seculo = primeiro_ano[:2]  # "19" ou "20"

    # Extrai todos os números dentro do trecho encontrado
    numeros = re.findall(r'\d{2,4}', trecho_completo)
    anos_normalizados = []
    for n in numeros:
        if len(n) == 4:
            anos_normalizados.append(int(n))
        elif len(n) == 2:
            anos_normalizados.append(int(seculo + n))

    if not anos_normalizados:
        return primeiro_ano

    ano_min, ano_max = min(anos_normalizados), max(anos_normalizados)
    if ano_min == ano_max:
        return str(ano_min)
    return f"{ano_min}-{ano_max}"

dataset = []
for texto in textos:
    tl = texto.lower()
    modelo_principal, todos_modelos = extrair_modelo(texto)
    item = {
        "texto": texto,
        "extracao": {
            "categoria": extrair_categoria(tl),
            "marca_veiculo": extrair_marca(tl),
            "modelo_veiculo": modelo_principal, #primeiro modelo citado
            "ano_compativel": extrair_ano(texto),
            "posicao": extrair_posicao(tl),
        }
    }
    # Metadado só para revisão humana - não faz parte do schema de treino
    if len(todos_modelos) > 1:
        item["_revisar_multiplos_modelos"] = todos_modelos
    dataset.append(item)

with open(f'{DIRETORIO_DADOS}dataset_candidato.json', 'w', encoding='utf-8') as f:
    json.dump(dataset, f, ensure_ascii=False, indent=2)

# Estatísticas de preenchimento
campos = ["categoria", "marca_veiculo", "modelo_veiculo", "ano_compativel", "posicao"]
for campo in campos:
    preenchidos = sum(1 for d in dataset if d["extracao"][campo] is not None)
    print(f"{campo}: {preenchidos}/{len(dataset)} preenchidos")

print("\n--- Amostra (primeiros 8) ---")
for d in dataset[:8]:
    print(json.dumps(d, ensure_ascii=False))
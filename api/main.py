import torch
from fastapi import FastAPI
from pydantic import BaseModel
from transformers import AutoModelForCausalLM, AutoTokenizer, BitsAndBytesConfig
from peft import PeftModel

MODEL_BASE = "Qwen/Qwen2.5-1.5B-Instruct"
CAMINHO_ADAPTADOR = "lora_adapter"

SYSTEM_PROMPT = (
    "Você é um sistema de extração de informações de anúncios de peças automotivas. "
    "Dado o texto de um anúncio, extraia os seguintes campos em formato JSON: "
    "categoria, marca_veiculo, modelo_veiculo, ano_compativel, posicao. "
    "Se um campo não estiver presente no texto, retorne null para ele."
)

bnb_config = BitsAndBytesConfig(
    load_in_4bit=True,
    bnb_4bit_quant_type="nf4",
    bnb_4bit_compute_dtype=torch.bfloat16,
    bnb_4bit_use_double_quant=True,
)

tokenizer = AutoTokenizer.from_pretrained(MODEL_BASE)
modelo_base = AutoModelForCausalLM.from_pretrained(
    MODEL_BASE,
    quantization_config=bnb_config,
    device_map="auto",
)
model = PeftModel.from_pretrained(modelo_base, CAMINHO_ADAPTADOR)
model.eval()
model.config.use_cache = True

app = FastAPI(title="Extrator de Peças Automotivas")

class TextoEntrada(BaseModel):
    texto: str


class ExtracaoSaida(BaseModel):
    categoria: str | None = None
    marca_veiculo: str | None = None
    modelo_veiculo: str | None = None
    ano_compativel: str | None = None
    posicao: str | None = None


def gerar_extracao(texto: str) -> str:
    messages = [
        {"role": "system", "content": SYSTEM_PROMPT},
        {"role": "user", "content": texto},
    ]
    prompt = tokenizer.apply_chat_template(messages, tokenize=False, add_generation_prompt=True)
    inputs = tokenizer(prompt, return_tensors="pt").to(model.device)
    with torch.no_grad():
        saida = model.generate(**inputs, max_new_tokens=100, do_sample=False)
    return tokenizer.decode(saida[0][inputs["input_ids"].shape[1]:], skip_special_tokens=True)


def extrair_json_da_resposta(texto_gerado: str):
    import re, json
    match = re.search(r"\{.*\}", texto_gerado, re.DOTALL)
    if not match:
        return None
    try:
        return json.loads(match.group(0))
    except json.JSONDecodeError:
        return None


@app.get("/health")
def health():
    return {"status": "ok"}


@app.post("/extrair", response_model=ExtracaoSaida)
def extrair(entrada: TextoEntrada):
    saida_bruta = gerar_extracao(entrada.texto)
    extraido = extrair_json_da_resposta(saida_bruta)
    if extraido is None:
        return ExtracaoSaida()
    return ExtracaoSaida(**extraido)
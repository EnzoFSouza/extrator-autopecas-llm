# Extrator de Peças Automotivas com Fine-Tuning de LLM

Sistema de extração de informações estruturadas a partir de texto livre não padronizado (descrições de anúncios de peças automotivas), usando fine-tuning eficiente de um LLM com LoRA/QLoRA.

## Motivação

Catálogos de peças automotivas frequentemente têm descrições em texto livre, sem padronização, com abreviações, erros de digitação, formatos inconsistentes. Este projeto resolve o problema de transformar esse texto em dados estruturados (categoria, marca do veículo, modelo, ano de compatibilidade, posição), viabilizando busca, filtragem e análise sistemática de um catálogo.

## Arquitetura do pipeline

```
Coleta manual de anúncios reais
        |
        v
Parsing e limpeza (labeling/parse_dados.py)
        |
        v
Rotulagem via regras de dominio + revisao manual (labeling/rotular.py)
        |
        v
Split treino/teste reprodutivel (80/20, seed fixa)
        |
        v
Baseline: modelo Qwen2.5-1.5B-Instruct, zero-shot
        |
        v
Fine-tuning com LoRA/QLoRA (peft + bitsandbytes + trl)
        |
        v
Avaliacao comparativa (baseline vs. fine-tuned)
        |
        v
API REST de inferencia (FastAPI)
```

## Dataset

- **100 exemplos únicos**, coletados manualmente de anúncios reais de peças automotivas (títulos de anúncio, texto livre escrito por vendedores)
- Rotulagem inicial via regras/dicionário de domínio (weak supervision), com revisão manual para correção e validação de qualidade
- Split: 80 exemplos de treino / 20 de teste, com semente fixa para reprodutibilidade
- Campos extraídos: `categoria`, `marca_veiculo`, `modelo_veiculo`, `ano_compativel`, `posicao`

## Modelo e técnica

- **Modelo base:** Qwen2.5-1.5B-Instruct
- **Técnica:** LoRA (r=16, alpha=32, aplicado em `q_proj`, `k_proj`, `v_proj`, `o_proj`) sobre modelo quantizado em 4 bits (QLoRA, NF4)
- **Bibliotecas:** `transformers`, `peft`, `bitsandbytes`, `trl` (Hugging Face)
- **Treino:** 6 épocas, batch efetivo 8 (batch 4 + gradient accumulation 2), learning rate 2e-4

## Resultados

Avaliação comparativa entre o modelo base (zero-shot, sem fine-tuning) e o modelo após fine-tuning, no conjunto de teste (20 exemplos nunca vistos durante o treino). Duas métricas são reportadas: correspondência **exata** (string idêntica após normalização) e **tolerante** (correspondência por substring, tolerando variação de plural/forma).

| Campo | Baseline (exato) | Fine-tuned (exato) | Baseline (tolerante) | Fine-tuned (tolerante) |
|---|---|---|---|---|
| categoria | 0% | **85%** | 55% | **90%** |
| marca_veiculo | 20% | **90%** | 20% | **90%** |
| modelo_veiculo | 20% | **85%** | 20% | **90%** |
| ano_compativel | 50% | **85%** | 55% | **85%** |
| posicao | 10% | **70%** | 25% | **70%** |

O ganho é consistente em todos os campos. O maior salto ocorre em `categoria` e `marca_veiculo` — no baseline, o modelo frequentemente confundia marca do veículo com marca do fabricante da peça (ex.: tratava "Cofap" ou "Bosch", fabricantes de autopeças, como se fossem montadoras). O fine-tuning corrige essa confusão de domínio de forma consistente.

## API

Endpoint REST via FastAPI, expondo o modelo fine-tunado:

```
POST /extrair
{ "texto": "Amortecedor traseiro original Honda Civic 2010 a 2015" }

-> { "categoria": "amortecedor", "marca_veiculo": "Honda", "modelo_veiculo": "Civic", "ano_compativel": "2010-2015", "posicao": "traseira" }
```

## Escopo e limitações conhecidas

- O campo `modelo_veiculo` captura apenas o primeiro modelo citado em anúncios com compatibilidade múltipla (comum em peças universais, compatíveis com vários modelos de uma mesma plataforma).
- O dataset é de escala moderada (100 exemplos), com foco em profundidade metodológica (baseline formal, split reprodutível, comparação rigorosa) mais do que em volume. O pipeline de coleta e rotulagem foi desenhado para escalar facilmente caso mais dados sejam necessários.
- A rotulagem inicial via regras de domínio cobre o vocabulário conhecido no momento da construção; o fine-tuning existe justamente para generalizar além dessa cobertura fixa (erros de digitação, sinônimos, modelos não antecipados).

## Próximos passos

- **RAG**: camada de busca vetorial sobre um catálogo de peças conhecidas, para casar a extração com itens já catalogados
- **Compatibilidade múltipla**: modelar `modelo_veiculo` como lista, cobrindo o caso de peças compatíveis com vários modelos
- **Expansão do dataset**: crescer a base de treino mantendo o mesmo rigor de avaliação

## Estrutura do repositório

```
api/                codigo da API FastAPI
data/               dataset bruto, rotulado, e splits de treino/teste
labeling/           scripts de parsing e rotulagem via regras de dominio
lora_adapter/       pesos do adaptador LoRA treinado
notebooks/          notebooks do Colab com carregamento do modelo, fine-tuning, avaliacao e API
resultado/          metricas do modelo baseline e do modelo finetunado
```

## Stack

Python, PyTorch, Hugging Face (`transformers`, `peft`, `trl`, `bitsandbytes`), FastAPI, Git.
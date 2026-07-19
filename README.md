# Extrator Autopecas LLM
extrator-autopecas-llm/
  data/
    dados_brutos.txt         # anúncios coletados manualmente
    treino.json
    teste.json
  labeling/
    parse_dados.py
    rotular.py
  notebooks/
    treino_e_api.ipynb        # tudo que precisa de GPU: modelo, LoRA, avaliação, FastAPI
  results/
    metricas_baseline.json
    metricas_finetuned.json
    resultados_baseline.json  # saídas completas, não só o resumo
    resultados_finetuned.json
  lora_adapter/                # opcional - ver pergunta abaixo
  README.md
  requirements.txt
  .gitignore
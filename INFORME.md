# Informe de la misión

## Parte 1: recuperación vectorial

Se leyeron los 20 documentos Markdown de `datos/corpus/` y se formaron 68 fragmentos al cortar por párrafos. Los títulos del documento y de la sección se anteponen para calcular el embedding, pero la salida contiene únicamente texto literal del corpus. Se usa similitud coseno; el umbral se aplica antes de limitar el resultado a top-k. Todos los modelos se ejecutaron en CPU. Para BERT se promedió la última capa sobre los tokens no rellenados; E5 usó los prefijos `query:` y `passage:`. Los nombres de CLI `bert`, `e5` y `minilm` corresponden respectivamente a `google-bert/bert-base-multilingual-cased`, `intfloat/multilingual-e5-small` y `sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2`.

| Encoder | Fragmentación | Top-k | Umbral | Context relevance | Recall | Precision | Evaluación |
|---|---|---:|---:|---:|---:|---:|---|
| BERT multilingüe sin ajuste | Párrafo | 1 | 0 | 0,3000 | 0,3000 | 0,3000 | [`bert_parrafo_k1_u0.jsonl.eval.json`](experimentos/bert_parrafo_k1_u0.jsonl.eval.json) |
| E5 multilingüe pequeño | Párrafo | 1 | 0 | 0,9000 | 0,9000 | 0,9000 | [`e5_parrafo_k1_u0.jsonl.eval.json`](experimentos/e5_parrafo_k1_u0.jsonl.eval.json) |
| MiniLM multilingüe | Párrafo | 1 | 0 | **0,9500** | **0,9500** | **0,9500** | [`minilm_parrafo_k1_u0.jsonl.eval.json`](experimentos/minilm_parrafo_k1_u0.jsonl.eval.json) |
| MiniLM multilingüe | Sección | 1 | 0 | 0,9500 | 0,9500 | 0,9500 | [`minilm_seccion_k1_u0.jsonl.eval.json`](experimentos/minilm_seccion_k1_u0.jsonl.eval.json) |
| MiniLM multilingüe | Párrafo | 2 | 0 | 0,6667 | 1,0000 | 0,5000 | [`minilm_parrafo_k2_u0.jsonl.eval.json`](experimentos/minilm_parrafo_k2_u0.jsonl.eval.json) |
| MiniLM multilingüe | Párrafo | 1 | 0,6 | 0,6000 | 0,6000 | 0,6000 | [`minilm_parrafo_k1_u06.jsonl.eval.json`](experimentos/minilm_parrafo_k1_u06.jsonl.eval.json) |

Cada evaluación tiene al lado el JSONL de fragmentos de esa misma corrida. Se eligió MiniLM con párrafos, top-k 1 y umbral 0: supera a BERT por 0,65 puntos de `context_relevance` y a E5 por 0,05. El corte por secciones empata en la métrica, pero devuelve más texto en promedio (289,2 caracteres frente a 214,75). Top-k 2 alcanza toda la evidencia, pero reduce la precisión a la mitad; el umbral 0,6 descarta evidencia útil.

El único fallo de la configuración elegida fue R01: ante una pregunta sobre la visita del padre a terapia intensiva al mediodía, se recuperó el párrafo de visitas de pediatría. La frase requerida está en la sección de terapia intensiva de `visitas.md`. No se agregó una excepción específica para esa pregunta, porque el conjunto final es oculto.

Para repetir la configuración elegida, con las dependencias instaladas:

```bash
HF_HOME=.cache/huggingface .venv/bin/python recuperar.py --preguntas datos/preguntas_recuperacion_dev.jsonl --salida resultados.jsonl
.venv/bin/python evaluar/evaluar.py recuperacion --preguntas datos/preguntas_recuperacion_dev.jsonl --resultados resultados.jsonl
```

## Partes 2 a 5

Pendientes.

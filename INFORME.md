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

## Parte 2: agente con dos fuentes

El agente (`agente.py`) usa LangChain: `ChatOpenAI` apunta a OpenRouter con `deepseek/deepseek-v4-flash-0731` y temperatura 0, y `create_agent` ejecuta el ciclo de tool calling hasta que el modelo responde sin pedir herramientas. Las seis herramientas son funciones con `@tool`; su docstring es la descripción que lee el modelo. `buscar_documentos` usa el encoder y el chunking elegidos en la parte 1 (MiniLM, párrafo, umbral 0) y carga el índice una sola vez; el top-k se midió de nuevo para el agente y quedó en 2 (`--top-k`). Las otras cinco llaman a la API local y, si el nombre no existe, le devuelven al modelo el JSON de error con las opciones válidas. El prompt de sistema indica usar documentos para normas, la API para el estado del día, las dos fuentes cuando la pregunta combina ambas, y responder solo con lo que devolvieron las herramientas.

Cada corrida escribe las respuestas, la evaluación y un log con cada llamada al modelo (tokens y `usage.cost` de OpenRouter), cada tool con sus argumentos y su resultado, y la respuesta final.

```bash
HF_HOME=.cache/huggingface .venv/bin/python agente.py --preguntas datos/preguntas_agente_dev.jsonl --salida respuestas.jsonl
.venv/bin/python evaluar/evaluar.py agente --preguntas datos/preguntas_agente_dev.jsonl --respuestas respuestas.jsonl
```

| Corrida | Ruteo | Context relevance | Faithfulness | Answer relevance | Costo agente (USD) | Costo juez (USD) | Archivos |
|---|---:|---:|---:|---:|---:|---:|---|
| Top-k 1 en `buscar_documentos` | 1,000 | 4,417 | 5,000 | 4,500 | 0,003230 | 0,01619 | [`agente_top1.jsonl`](experimentos/agente_top1.jsonl), [`.eval.json`](experimentos/agente_top1.jsonl.eval.json), [log](experimentos/agente_top1.log.md) |
| **Top-k 2 en `buscar_documentos` (entregada)** | **1,000** | **4,750** | **5,000** | **5,000** | 0,003313 | 0,01661 | [`respuestas.jsonl`](respuestas.jsonl), [`.eval.json`](respuestas.jsonl.eval.json), [log](respuestas.log.md) |

En las dos corridas el agente eligió las herramientas esperadas en las 12 preguntas y el juez no encontró afirmaciones sin respaldo. Con top-k 1, las dos preguntas con notas bajas fallaron en la recuperación, no en el ruteo ni en la redacción:

- **A04** (¿quiénes pueden donar sangre?; CR 1, AR 1). El modelo buscó dos veces con consultas distintas, y las dos veces el primer fragmento fue el párrafo de horarios de hemoterapia. Los requisitos de edad y peso están en el párrafo siguiente de `donacion_sangre.md`. El agente respondió solo con los horarios y dijo que no tenía los requisitos; por eso la fidelidad quedó en 5.
- **A12** (insulina NPH; CR 3, AR 3). El stock y la reposición salieron bien de la API. Para retirarla hacen falta dos párrafos de `farmacia.md` (receta de un profesional del hospital y DNI), pero top-k 1 trajo el de medicamentos de alto costo. La respuesta aclaró que no encontró requisitos específicos.
- **A11** (CR 4). El modelo hizo una segunda búsqueda y agregó un fragmento sobre acompañantes que no hacía falta; el juez lo contó como ruido.

En una prueba previa de A10 con otra formulación de la búsqueda, el fragmento recuperado fue el de acompañantes de internación general y no el de pediatría. Los tres casos muestran el mismo límite: top-k 1 maximizó `context_relevance` en la parte 1, pero en el agente una sola búsqueda equivocada deja sin evidencia la respuesta.

Por eso se midió top-k 2, un cambio general que no depende de estas preguntas. A04 pasó a CR 5 y AR 5: el segundo fragmento es el de los requisitos para donar. A12 subió a CR 4 y AR 5 porque llegó el párrafo de la receta, aunque sigue faltando el del DNI; el juez no lo penalizó, pero la respuesta queda incompleta frente a la referencia. El costo de más texto es poco ruido: A02 bajó a CR 4 por un segundo fragmento con otras horas de ayuno, y A11 siguió en CR 4 por fragmentos de internación y coberturas. En la parte 1 top-k 2 bajaba la precisión a la mitad porque la métrica cuenta fragmentos sin evidencia; aquí el juez tolera un fragmento de más y castiga más la evidencia faltante. Se entrega top-k 2.

Costo de OpenRouter en la parte 2 hasta ahora: USD 0,00090 en dos pruebas de A10, USD 0,00323 + 0,01619 (agente y juez) con top-k 1 y USD 0,00331 + 0,01661 con top-k 2, en total USD 0,04024 según `usage.cost`. Falta contrastarlo con el dashboard de actividad.

## Partes 3 a 5

Pendientes.

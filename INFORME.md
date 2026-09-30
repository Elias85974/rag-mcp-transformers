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

## Parte 3: las mismas herramientas como servidor MCP

`servidor_mcp.py` publica las seis herramientas por stdio con `FastMCP` del SDK oficial `mcp` 1.x (`@mcp.tool()`, sin LangChain). Tienen los mismos nombres, argumentos y docstrings que en la parte 2, y `buscar_documentos` usa el mismo recuperador con top-k 2. `agente_mcp.py` lanza el servidor como subproceso, abre **una sola sesión MCP** para toda la corrida, descubre las tools con `tools/list` (`load_mcp_tools` de `langchain-mcp-adapters`) y se las pasa al mismo `create_agent` de LangChain, con el mismo modelo, temperatura y prompt de sistema. Cada llamada del modelo a una tool se convierte en un `tools/call` al servidor. El cliente no tiene código propio de API ni de recuperación: de `agente.py` reutiliza solo el prompt, el id del modelo, la lectura de `.env`, el resumen de la conversación y el formato del log. Las tools MCP devuelven bloques de contenido (`[{"type": "text", "text": ...}]`), y el cliente los convierte a texto antes de escribir `contextos`.

Una sesión persistente importa: con `MultiServerMCPClient.get_tools()` sin sesión, cada `tools/call` lanza un servidor nuevo y vuelve a cargar MiniLM y a calcular los embeddings del corpus.

```bash
HF_HOME=.cache/huggingface .venv/bin/python agente_mcp.py --preguntas datos/preguntas_agente_dev.jsonl --salida respuestas_mcp.jsonl
.venv/bin/python evaluar/evaluar.py agente --preguntas datos/preguntas_agente_dev.jsonl --respuestas respuestas_mcp.jsonl
```

El servidor también se probó con el MCP Inspector (`npx @modelcontextprotocol/inspector .venv/bin/python servidor_mcp.py`), sin LLM: se llamó a cada una de las seis tools y se guardaron las capturas en [`experimentos/inspector/`](experimentos/inspector/). La primera llamada a `buscar_documentos` tardó unos 50 segundos porque carga el encoder, y mientras tanto el servidor no atiende otras llamadas; las siguientes tardan alrededor de 50 ms.

| Agente | Ruteo | Context relevance | Faithfulness | Answer relevance | Tokens (entrada / salida) | Costo agente (USD) | Costo juez (USD) | Archivos |
|---|---:|---:|---:|---:|---:|---:|---:|---|
| Parte 2, tools en proceso | 1,000 | 4,750 | 5,000 | 5,000 | 30.007 / 2.354 | 0,003313 | 0,01661 | [`respuestas.jsonl`](respuestas.jsonl), [`.eval.json`](respuestas.jsonl.eval.json), [log](respuestas.log.md) |
| Parte 3, tools por MCP | 1,000 | 4,583 | 5,000 | 5,000 | 29.999 / 2.157 | 0,003061 | 0,01852 | [`respuestas_mcp.jsonl`](respuestas_mcp.jsonl), [`.eval.json`](respuestas_mcp.jsonl.eval.json), [log](respuestas_mcp.log.md) |

El agente MCP eligió las mismas herramientas que el de la parte 2 en las 12 preguntas, y la primera llamada al modelo de cada pregunta tuvo los mismos tokens de entrada en las dos corridas (por ejemplo 1.095 en A01 y 1.101 en A10). Eso muestra que el modelo recibe las mismas descripciones y esquemas: el transporte MCP no cambia lo que ve el modelo.

La diferencia de 0,17 en context relevance sale de dos preguntas que bajaron de 5 a 4 (A03 y A10; 2/12 = 0,17). Los logs muestran que no la causó MCP:

- **A03 y A10**: los contextos son idénticos, carácter por carácter, a los de la parte 2 (mismas consultas a `buscar_documentos` y mismos fragmentos). Solo cambió el formato de la respuesta (A03 agregó negritas). El juez puso 5 en la parte 2 y 4 aquí, y justificó el 4 con "una pequeña mención sobre internación" o "una porción menor de texto irrelevante" en esos mismos textos. Es variación del juez, no del agente.
- **A11**: la segunda búsqueda usó otra formulación ("consulta ambulatoria o turno de especialidad") y trajo un fragmento distinto; quedó en CR 4 en las dos corridas.
- **A04**: el modelo reformuló la consulta ("requisitos para donar sangre quiénes pueden donar") y recuperó los mismos dos párrafos; CR 5 en las dos.

De las 12 preguntas, solo en A11 los contextos difieren de los de la parte 2. Aun con temperatura 0, DeepSeek no es totalmente determinista y reescribe algunas consultas. Esa variación, más la del juez, explica diferencias de ±1 en preguntas sueltas. El costo del agente es casi el mismo (USD 0,00025 menos, por respuestas un poco más cortas). MCP agrega un proceso y la serialización JSON-RPC, pero no tokens.

## Parte 4: atención en NumPy

`atencion.py` usa solo NumPy. Primero se corrieron los tests de la cátedra contra un esqueleto que levantaba `NotImplementedError` (14 errores) y después se implementó:

- `softmax`: resta el máximo de cada fila antes de exponenciar. Eso no cambia el resultado, porque el factor se cancela, y evita el desborde con valores como 1000.
- `atencion`: `A = softmax(Q Kᵀ / √d_k)` y salida `A V`. Dividir por √d_k evita que los productos punto crezcan con la dimensión y saturen el softmax. La máscara causal pone −∞ arriba de la diagonal antes del softmax, así cada posición recibe peso 0 de las posiciones futuras y las filas siguen sumando 1.
- `autoatencion`: Q, K y V son proyecciones de la misma X.
- `multicabeza`: concatena la salida de cada cabeza y la proyecta con `Wo`.
- `layer_norm`: normaliza cada fila a media 0 y varianza 1, con `eps` dentro de la raíz.

```bash
.venv/bin/python atencion/test_atencion.py atencion.py   # 14 tests OK
```

## Parte 5: bloque de transformer a mano

Pendiente. Se resuelve a mano, sin IA, como pide la consigna. Las hojas escaneadas van en `a_mano/`.

## Costo total en OpenRouter

| Concepto | USD (`usage.cost`) |
|---|---:|
| Parte 2: pruebas de A10 | 0,00090 |
| Parte 2: agente y juez con top-k 1 | 0,01942 |
| Parte 2: agente y juez con top-k 2 | 0,01992 |
| Parte 3: agente MCP y juez | 0,02158 |
| **Total** | **0,06182** |

Las partes 1 y 4 no usan LLM: el evaluador de recuperación no llama al juez. Falta contrastar el total con el dashboard de actividad de OpenRouter.

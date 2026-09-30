# Especificación de trabajo

Fuente de verdad: `mission.md`. Esta especificación fija contratos observables para las partes 1 a 4; se actualiza antes de cambiar su comportamiento.

## Entradas y restricciones comunes

- Todo el código entregado es Python y se ejecuta desde esta carpeta con los comandos de `mission.md`.
- Los archivos JSONL contienen un objeto JSON por línea y conservan los `id` de entrada. Se procesan todas las preguntas, incluidas las del conjunto oculto.
- La API local en `http://localhost:8765` provee el estado del día; el corpus Markdown provee normas y procedimientos. No inferir datos de la API desde documentos ni inventar información ausente.
- Los modelos generativos y el juez usan OpenRouter. El agente usa `deepseek/deepseek-v4-flash-0731`; el evaluador de la cátedra fija su propio juez. La clave llega por `OPENROUTER_API_KEY`.
- Permanecen intactos `evaluar/evaluar.py`, `api/`, `datos/` y `atencion/test_atencion.py`.

## Parte 1: recuperación

`python3 recuperar.py --preguntas datos/preguntas_recuperacion_dev.jsonl --salida resultados.jsonl` escribe una línea `{"id": "R01", "fragmentos": ["texto", ...]}` por pregunta. Los fragmentos se ordenan por relevancia y contienen textualmente la evidencia del corpus, sin cambiarla. El recuperador usa embeddings calculados con un transformer encoder en CPU, chunking reproducible, similitud coseno, top-k y umbral configurados en código o configuración entregada.

Se comparan al menos tres encoders: BERT sin ajuste de similitud con mean pooling de la última capa y dos encoders de oraciones. Se miden también chunking, top-k y umbral. Cada configuración probada deja resultados y `.eval.json` en `experimentos/`; la tabla del `INFORME.md` cita esos archivos y explica la elección por `context_relevance`, recall y precision. La configuración final debe superar claramente a BERT. No se optimiza mediante respuestas fijas para preguntas `dev`.

Configuración elegida tras medir en `dev`: `sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2`, fragmentación por párrafo, top-k 1 y coseno mínimo 0. Los títulos del documento y de la sección se incluyen solo al calcular embeddings; cada fragmento de salida conserva el texto del corpus. Las opciones de CLI permiten reproducir las otras configuraciones medidas.

Pruebas antes de implementar: lectura de corpus y preguntas, preservación exacta de texto relevante al fragmentar, salida JSONL por `id`, orden por similitud, y comportamiento de top-k/umbral. La medición definitiva usa `python3 evaluar/evaluar.py recuperacion --preguntas ... --resultados ...`.

## Parte 2: agente LangChain

`python3 agente.py --preguntas datos/preguntas_agente_dev.jsonl --salida respuestas.jsonl` escribe `{"id": "A01", "respuesta": "...", "contextos": ["..."], "herramientas": ["..."]}` por pregunta. `contextos` incluye todo el texto recibido de las herramientas, incluidos fragmentos y JSON de la API; `herramientas` registra las llamadas reales.

El agente usa tool calling con `ChatOpenAI` de `langchain-openai` contra OpenRouter. El enunciado vigente recomienda `openai-agents` y admite LangChain; se eligió LangChain, y la parte 3 usa el mismo framework. Expone exactamente `buscar_documentos(consulta)`, `consultar_camas(sector)`, `consultar_guardia(especialidad)`, `consultar_turnos(especialidad)`, `consultar_farmacia(medicamento)` y `consultar_espera()`. La primera usa el recuperador de la parte 1; las otras llaman a los endpoints homónimos de la API. Los errores de parámetros de la API llegan al agente para permitir corrección. Las preguntas pueden requerir documentos, API o ambas fuentes.

Cada corrida guarda un log Markdown, con una sección por pregunta, con llamadas, argumentos, resultados, respuesta, tokens y costo por llamada al modelo. El evaluador escribe `respuestas.jsonl.eval.json`. El objetivo es ruteo cercano a 1 y las tres notas superiores a 4 en `dev`, sin afirmaciones sin respaldo en `contextos`.

Pruebas antes de implementar: nombres y argumentos de herramientas, serialización de contextos y trazas, manejo de errores de la API, y preguntas que requieren ambas fuentes. Las evaluaciones con juez se ejecutan solo para cambios que valga la pena medir.

## Parte 3: MCP

`servidor_mcp.py` publica las seis herramientas anteriores por stdio con `FastMCP` del SDK oficial `mcp` 1.x. No instala el paquete independiente `fastmcp` ni usa LangChain en el servidor. Las descripciones de las tools son sus docstrings.

`python3 agente_mcp.py --preguntas datos/preguntas_agente_dev.jsonl --salida respuestas_mcp.jsonl` usa LangChain y `langchain-mcp-adapters` para descubrir herramientas con `tools/list` y llamarlas con `tools/call`. El cliente no contiene código propio de acceso a API ni de recuperación. Aplica el mismo contrato de salida y logging que la parte 2. Se prueba cada tool con MCP Inspector y se guardan capturas en `experimentos/inspector/`. El informe compara métricas y costo de ambos agentes a partir de sus evaluaciones y logs.

Pruebas antes de implementar: descubrimiento de seis tools, argumentos y resultado de una llamada MCP, y trazas completas del cliente.

## Parte 4: atención en NumPy

`python3 atencion/test_atencion.py atencion.py` debe pasar los 14 tests entregados sin modificar el archivo de tests. `atencion.py` solo usa NumPy y define:

- `softmax(M)`: distribución estable numéricamente sobre el último eje.
- `atencion(Q, K, V, mascara=False)`: devuelve salida y pesos `A = softmax(Q @ K.T / sqrt(d_k))`; la máscara causal excluye posiciones futuras antes del softmax.
- `autoatencion(X, Wq, Wk, Wv, mascara=False)`: proyecta `X` y llama a `atencion`.
- `multicabeza(X, cabezas, Wo, mascara=False)`: concatena las salidas de las cabezas y aplica `Wo`.
- `layer_norm(x, eps=1e-5)`: normaliza cada fila por su media y varianza.

El archivo de tests de la cátedra es la prueba inicial de TDD y debe correrse en rojo antes de implementar.

## Entrega y límite de IA

El `INFORME.md` contiene experimentos, análisis de errores, comparación de agentes y costo total cotejado con el dashboard. Se entregan los cinco scripts, evaluaciones, logs y capturas pedidos, mediante el repositorio GitHub del grupo antes del 9 de octubre de 2026. La parte 5 se resuelve íntegramente a mano; no generar con IA sus cuentas ni respuestas.

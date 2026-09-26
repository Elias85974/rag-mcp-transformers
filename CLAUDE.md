# Trabajo en la misión RAG, MCP y Transformers

Leé `mission.md` y `SPEC.md` antes de programar. Este archivo sirve tanto a Claude Code como a Codex y otros agentes. La raíz de este proyecto es esta carpeta, no la del repositorio Talksmith.

## Preparación

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
python3 api/servidor.py                 # dejar corriendo en otra terminal
```

Ejecutá los comandos del enunciado desde esta carpeta. Usá `.venv/bin/python` si la terminal no tiene el entorno activado. La API responde en `http://localhost:8765`. Para modelos de Hugging Face, usá `HF_HOME=.cache/huggingface` para mantener la caché fuera de Git. OpenRouter requiere `OPENROUTER_API_KEY` en el entorno; nunca guardes la clave en el repo.

## Forma de trabajo

1. Actualizá `SPEC.md` cuando cambie el entendimiento de un contrato o decisión verificable.
2. Para las partes 1 a 4, escribí primero una prueba que falle, implementá lo mínimo y corré la prueba y el evaluador pertinente. Conservá `atencion/test_atencion.py` sin editar.
3. Hacé commits pequeños con una intención clara; la historia debe mostrar las pruebas antes de las implementaciones. No mezcles artefactos temporales con resultados de evaluación.
4. Guardá cada configuración medida de la parte 1 en `experimentos/` junto con su `.eval.json`; registrá parámetros y puntajes en `INFORME.md`.
5. En cada corrida de las partes 2 y 3, guardá respuestas, `.eval.json` y un log Markdown con preguntas, argumentos y resultados de tools, respuestas, tokens y costos del modelo. Contrastá el costo total con el dashboard de OpenRouter.
6. No uses IA para resolver la parte 5: las cuentas, explicaciones y respuestas van a mano en `a_mano/`.

No modifiques `evaluar/evaluar.py`, `api/`, `datos/` ni `atencion/test_atencion.py`. No llames al juez de pago ni generes costos de OpenRouter sin necesitar una medición de la misión.

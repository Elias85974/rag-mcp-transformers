"""Agente del Hospital Arroyo Claro con documentos y API del día."""

import argparse
import json
import os
import urllib.error
from datetime import datetime
from pathlib import Path
from urllib.parse import urlencode
from urllib.request import urlopen

from langchain_core.messages import AIMessage, ToolMessage
from langchain_core.tools import tool

import recuperar


API = "http://localhost:8765"
MODELO = "deepseek/deepseek-v4-flash-0731"
TOP_K = 2
INSTRUCCIONES = """Sos el asistente del Hospital Provincial Arroyo Claro y respondés preguntas de pacientes y familiares.
No sabés nada del hospital por tu cuenta: toda la información sale de las herramientas.
- Normas, procedimientos, horarios fijos y requisitos: buscar_documentos.
- Estado de hoy (camas, guardias, turnos, farmacia, espera en la guardia): la herramienta consultar_ que corresponda.
- Si la pregunta combina una norma con un dato del día, usá las dos fuentes.
Respondé en español, breve y directo, solo con lo que devolvieron las herramientas. No agregues datos,
consejos ni ofrecimientos que no estén en esos resultados. Si no encontrás la información, decilo."""
_indice = None


def llamar_api(ruta: str, **parametros) -> str:
    """Devuelve el JSON de la API como texto, también cuando es un error con opciones válidas."""
    url = f"{API}{ruta}" + (f"?{urlencode(parametros)}" if parametros else "")
    try:
        with urlopen(url) as respuesta:
            return respuesta.read().decode("utf-8")
    except urllib.error.HTTPError as error:
        return error.read().decode("utf-8")


@tool
def buscar_documentos(consulta: str) -> str:
    """Busca en las normas y procedimientos del hospital: horarios y reglas de visita, acompañantes,
    preparación de estudios, documentación para turnos, requisitos de farmacia, coberturas, internación,
    alta, triage, donación de sangre, vacunatorio y derechos del paciente. No tiene datos del día
    (camas, guardias, turnos, stock ni espera). La consulta es una pregunta o frase en español."""
    global _indice
    if _indice is None:
        fragmentos = recuperar.cargar_fragmentos(recuperar.CORPUS, "parrafo")
        encoder = recuperar.crear_encoder("minilm")
        _indice = fragmentos, encoder, encoder.encode([f.embedding_texto for f in fragmentos], "pasaje")
    fragmentos, encoder, vectores = _indice
    indices = recuperar.seleccionar(encoder.encode([consulta], "consulta")[0], vectores, TOP_K, 0.0)
    return "\n\n".join(fragmentos[i].texto for i in indices) or "No se encontraron documentos."


@tool
def consultar_camas(sector: str) -> str:
    """Camas de hoy en un sector de internación: total, ocupadas y libres. Ejemplos de sector:
    pediatria, terapia_intensiva, maternidad. Si el sector no existe, devuelve las opciones válidas."""
    return llamar_api("/camas", sector=sector)


@tool
def consultar_guardia(especialidad: str) -> str:
    """Profesionales de guardia hoy en una especialidad y su horario. Ejemplo: cardiologia.
    Si la especialidad no existe, devuelve las opciones válidas."""
    return llamar_api("/guardia", especialidad=especialidad)


@tool
def consultar_turnos(especialidad: str) -> str:
    """Próximos turnos disponibles (fecha y hora) en una especialidad. Ejemplo: traumatologia.
    Si la especialidad no existe, devuelve las opciones válidas."""
    return llamar_api("/turnos", especialidad=especialidad)


@tool
def consultar_farmacia(medicamento: str) -> str:
    """Stock actual de un medicamento en la farmacia del hospital y, si no hay, la fecha de reposición.
    Usar el nombre con la dosis, por ejemplo "enalapril 10 mg". Si no existe, devuelve las opciones válidas."""
    return llamar_api("/farmacia", medicamento=medicamento)


@tool
def consultar_espera() -> str:
    """Minutos de espera actuales en la guardia para cada nivel de triage (rojo, naranja, amarillo,
    verde, azul)."""
    return llamar_api("/espera")


HERRAMIENTAS = [buscar_documentos, consultar_camas, consultar_guardia, consultar_turnos,
                consultar_farmacia, consultar_espera]


def crear_agente():
    from langchain.agents import create_agent
    from langchain_openai import ChatOpenAI

    modelo = ChatOpenAI(model=MODELO, base_url="https://openrouter.ai/api/v1",
                        api_key=os.environ["OPENROUTER_API_KEY"], temperature=0)
    return create_agent(modelo, HERRAMIENTAS, system_prompt=INSTRUCCIONES)


def responder(agente_lc, pregunta: str) -> dict:
    estado = agente_lc.invoke({"messages": [{"role": "user", "content": pregunta}]},
                              config={"recursion_limit": 20})
    return resumir(estado["messages"])


def resumir(mensajes: list) -> dict:
    """Convierte la conversación del agente en el contrato del evaluador más una traza para el log."""
    argumentos = {}
    traza = []
    for mensaje in mensajes:
        if isinstance(mensaje, AIMessage):
            uso = mensaje.usage_metadata or {}
            traza.append({"tipo": "modelo", "entrada": uso.get("input_tokens", 0),
                          "salida": uso.get("output_tokens", 0),
                          "costo": (mensaje.response_metadata.get("token_usage") or {}).get("cost", 0.0),
                          "pide": [f"{t['name']}({json.dumps(t['args'], ensure_ascii=False)})"
                                   for t in mensaje.tool_calls]})
            argumentos.update({t["id"]: t["args"] for t in mensaje.tool_calls})
        elif isinstance(mensaje, ToolMessage):
            traza.append({"tipo": "tool", "nombre": mensaje.name,
                          "argumentos": argumentos.get(mensaje.tool_call_id, {}), "resultado": mensaje.content})
    respuestas = [m.content for m in mensajes if isinstance(m, AIMessage) and not m.tool_calls]
    tools = [p for p in traza if p["tipo"] == "tool"]
    return {"respuesta": respuestas[-1] if respuestas else "",
            "contextos": [p["resultado"] for p in tools],
            "herramientas": [p["nombre"] for p in tools],
            "traza": traza}


def log_markdown(filas: list[dict], titulo: str = "Corrida del agente") -> str:
    total = {"entrada": 0, "salida": 0, "costo": 0.0}
    partes = []
    for fila in filas:
        modelo = [p for p in fila["traza"] if p["tipo"] == "modelo"]
        subtotal = {k: sum(p[k] for p in modelo) for k in total}
        total = {k: total[k] + subtotal[k] for k in total}
        partes += [f"## {fila['id']}", "", f"**Pregunta:** {fila['pregunta']}", ""]
        for numero, paso in enumerate(fila["traza"], 1):
            if paso["tipo"] == "modelo":
                pide = ", ".join(paso["pide"]) or "respuesta final"
                partes.append(f"{numero}. **Modelo**: {paso['entrada']} tokens de entrada, {paso['salida']} de salida, "
                              f"USD {paso['costo']:.6f}. Pide: {pide}")
            else:
                partes += [f"{numero}. **Tool `{paso['nombre']}`** con "
                           f"`{json.dumps(paso['argumentos'], ensure_ascii=False)}`:", "",
                           "   ```", *[f"   {linea}" for linea in paso["resultado"].splitlines()], "   ```"]
        partes += ["", "**Respuesta:**", "", fila["respuesta"], "",
                   f"**Uso de la pregunta:** {subtotal['entrada']} tokens de entrada, {subtotal['salida']} de salida, "
                   f"USD {subtotal['costo']:.6f}.", ""]
    encabezado = [f"# {titulo} ({datetime.now():%Y-%m-%d %H:%M})", "",
                  f"Modelo: `{MODELO}`. Top-k de buscar_documentos: {TOP_K}. Preguntas: {len(filas)}.", "",
                  f"**Total de la corrida:** {total['entrada']} tokens de entrada, {total['salida']} de salida, "
                  f"USD {total['costo']:.6f} según `usage.cost` de OpenRouter.", ""]
    return "\n".join(encabezado + partes)


def ejecutar(preguntas: Path, salida: Path) -> None:
    agente_lc = crear_agente()
    filas = []
    with salida.open("w", encoding="utf-8") as archivo:
        for linea in preguntas.read_text(encoding="utf-8").splitlines():
            if not linea.strip():
                continue
            pregunta = json.loads(linea)
            resultado = responder(agente_lc, pregunta["pregunta"])
            filas.append({"id": pregunta["id"], "pregunta": pregunta["pregunta"], **resultado})
            contrato = {k: resultado[k] for k in ["respuesta", "contextos", "herramientas"]}
            archivo.write(json.dumps({"id": pregunta["id"], **contrato}, ensure_ascii=False) + "\n")
            archivo.flush()
            print(f"{pregunta['id']}  {', '.join(resultado['herramientas']) or '(sin tools)'}")
    salida.with_suffix(".log.md").write_text(log_markdown(filas), encoding="utf-8")


def cargar_env(ruta: Path = Path(__file__).parent / ".env") -> None:
    """Lee OPENROUTER_API_KEY de .env si no está en el entorno."""
    if ruta.exists():
        for linea in ruta.read_text(encoding="utf-8").splitlines():
            clave, separador, valor = linea.partition("=")
            if separador and not clave.startswith("#"):
                os.environ.setdefault(clave.strip(), valor.strip())


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--preguntas", type=Path, required=True)
    parser.add_argument("--salida", type=Path, required=True)
    parser.add_argument("--top-k", type=int, default=TOP_K, help="fragmentos por búsqueda de documentos")
    args = parser.parse_args()
    if args.top_k < 1:
        parser.error("--top-k debe ser positivo")
    globals()["TOP_K"] = args.top_k
    cargar_env()
    ejecutar(args.preguntas, args.salida)


if __name__ == "__main__":
    main()

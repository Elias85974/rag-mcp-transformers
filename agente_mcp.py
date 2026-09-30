"""Agente del Hospital Arroyo Claro que obtiene sus herramientas de servidor_mcp.py por MCP."""

import argparse
import asyncio
import json
import os
import sys
from pathlib import Path

from langchain_core.messages import ToolMessage
from langchain_mcp_adapters.client import MultiServerMCPClient
from langchain_mcp_adapters.tools import load_mcp_tools

import agente
from agente import INSTRUCCIONES, MODELO, cargar_env

SERVIDOR = Path(__file__).parent / "servidor_mcp.py"


def sesion_mcp():
    """Lanza el servidor por stdio y abre una sesión que dura toda la corrida."""
    cliente = MultiServerMCPClient({"hospital": {
        "transport": "stdio", "command": sys.executable, "args": [str(SERVIDOR)],
        "cwd": str(SERVIDOR.parent), "env": dict(os.environ)}})
    return cliente.session("hospital")


async def cargar_herramientas(sesion) -> list:
    """Descubre las herramientas con tools/list; cada una llama al servidor con tools/call."""
    return await load_mcp_tools(sesion)


def texto(contenido) -> str:
    """Las tools MCP devuelven bloques de contenido; el contrato pide texto."""
    if isinstance(contenido, str):
        return contenido
    return "".join(b.get("text", "") if isinstance(b, dict) else str(b) for b in contenido)


def resumir(mensajes: list) -> dict:
    mensajes = [m.model_copy(update={"content": texto(m.content)}) if isinstance(m, ToolMessage) else m
                for m in mensajes]
    return agente.resumir(mensajes)


def crear_agente(herramientas: list):
    from langchain.agents import create_agent
    from langchain_openai import ChatOpenAI

    modelo = ChatOpenAI(model=MODELO, base_url="https://openrouter.ai/api/v1",
                        api_key=os.environ["OPENROUTER_API_KEY"], temperature=0)
    return create_agent(modelo, herramientas, system_prompt=INSTRUCCIONES)


async def responder(agente_lc, pregunta: str) -> dict:
    estado = await agente_lc.ainvoke({"messages": [{"role": "user", "content": pregunta}]},
                                     config={"recursion_limit": 20})
    return resumir(estado["messages"])


async def ejecutar(preguntas: Path, salida: Path) -> None:
    filas = []
    async with sesion_mcp() as sesion:
        herramientas = await cargar_herramientas(sesion)
        agente_lc = crear_agente(herramientas)
        with salida.open("w", encoding="utf-8") as archivo:
            for linea in preguntas.read_text(encoding="utf-8").splitlines():
                if not linea.strip():
                    continue
                pregunta = json.loads(linea)
                resultado = await responder(agente_lc, pregunta["pregunta"])
                filas.append({"id": pregunta["id"], "pregunta": pregunta["pregunta"], **resultado})
                contrato = {k: resultado[k] for k in ["respuesta", "contextos", "herramientas"]}
                archivo.write(json.dumps({"id": pregunta["id"], **contrato}, ensure_ascii=False) + "\n")
                archivo.flush()
                print(f"{pregunta['id']}  {', '.join(resultado['herramientas']) or '(sin tools)'}")
    salida.with_suffix(".log.md").write_text(agente.log_markdown(filas, "Corrida del agente MCP"),
                                             encoding="utf-8")


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--preguntas", type=Path, required=True)
    parser.add_argument("--salida", type=Path, required=True)
    args = parser.parse_args()
    cargar_env()
    asyncio.run(ejecutar(args.preguntas, args.salida))


if __name__ == "__main__":
    main()

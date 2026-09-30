import asyncio
import json
import tempfile
import unittest
import urllib.request
from pathlib import Path
from unittest.mock import AsyncMock, patch

from langchain_core.messages import AIMessage, HumanMessage, ToolMessage

import agente_mcp


def api_disponible() -> bool:
    try:
        urllib.request.urlopen("http://localhost:8765/espera", timeout=1)
        return True
    except OSError:
        return False


async def herramientas_y_espera():
    async with agente_mcp.sesion_mcp() as sesion:
        tools = await agente_mcp.cargar_herramientas(sesion)
        espera = next(t for t in tools if t.name == "consultar_espera")
        return tools, await espera.ainvoke({})


class ClienteMcpTest(unittest.TestCase):
    def test_descubre_las_seis_tools_del_servidor_por_stdio(self):
        async def listar():
            async with agente_mcp.sesion_mcp() as sesion:
                return await agente_mcp.cargar_herramientas(sesion)

        tools = asyncio.run(listar())
        self.assertEqual(sorted(t.name for t in tools), sorted([
            "buscar_documentos", "consultar_camas", "consultar_guardia",
            "consultar_turnos", "consultar_farmacia", "consultar_espera"]))
        camas = next(t for t in tools if t.name == "consultar_camas")
        self.assertIn("sector", camas.args)

    @unittest.skipUnless(api_disponible(), "la API del hospital no está corriendo")
    def test_llama_una_tool_por_tools_call(self):
        _, resultado = asyncio.run(herramientas_y_espera())
        self.assertIn("minutos_por_nivel", agente_mcp.texto(resultado))

    def test_no_tiene_codigo_propio_de_api_ni_recuperador(self):
        codigo = Path(agente_mcp.__file__).read_text(encoding="utf-8")
        for prohibido in ["urlopen", "localhost:8765", "recuperar", "llamar_api", "HERRAMIENTAS", "@tool"]:
            self.assertNotIn(prohibido, codigo)


class TrazaTest(unittest.TestCase):
    def conversacion(self):
        uso = {"usage_metadata": {"input_tokens": 900, "output_tokens": 200, "total_tokens": 1100},
               "response_metadata": {"token_usage": {"cost": 0.0003}}}
        return [
            HumanMessage("¿Cuánto hay que esperar?"),
            AIMessage("", tool_calls=[{"name": "consultar_espera", "args": {}, "id": "c1"}], **uso),
            ToolMessage([{"type": "text", "text": '{"minutos_por_nivel": {"verde": 135}}', "id": "x"}],
                        tool_call_id="c1", name="consultar_espera"),
            AIMessage("En verde se esperan 135 minutos.", **uso),
        ]

    def test_texto_une_bloques_de_contenido_mcp(self):
        self.assertEqual(agente_mcp.texto([{"type": "text", "text": "a"}, {"type": "text", "text": "b"}]), "ab")
        self.assertEqual(agente_mcp.texto("plano"), "plano")

    def test_resumen_con_contenido_mcp_sigue_el_contrato(self):
        resumen = agente_mcp.resumir(self.conversacion())
        self.assertEqual(resumen["contextos"], ['{"minutos_por_nivel": {"verde": 135}}'])
        self.assertEqual(resumen["herramientas"], ["consultar_espera"])
        self.assertEqual(resumen["respuesta"], "En verde se esperan 135 minutos.")
        self.assertEqual(resumen["traza"][0]["costo"], 0.0003)

    def test_ejecutar_escribe_jsonl_y_log(self):
        resumen = agente_mcp.resumir(self.conversacion())
        with tempfile.TemporaryDirectory() as carpeta:
            base = Path(carpeta)
            preguntas = base / "preguntas.jsonl"
            preguntas.write_text('{"id":"A07","pregunta":"¿Espera?"}\n{"id":"A08","pregunta":"¿Otra?"}\n',
                                 encoding="utf-8")
            salida = base / "respuestas_mcp.jsonl"
            with patch.object(agente_mcp, "sesion_mcp"), \
                    patch.object(agente_mcp, "cargar_herramientas", AsyncMock(return_value=[])), \
                    patch.object(agente_mcp, "crear_agente"), \
                    patch.object(agente_mcp, "responder", AsyncMock(return_value=resumen)):
                asyncio.run(agente_mcp.ejecutar(preguntas, salida))
            filas = [json.loads(linea) for linea in salida.read_text(encoding="utf-8").splitlines()]
            log = (base / "respuestas_mcp.log.md").read_text(encoding="utf-8")
        self.assertEqual([f["id"] for f in filas], ["A07", "A08"])
        self.assertEqual(set(filas[0]), {"id", "respuesta", "contextos", "herramientas"})
        for esperado in ["MCP", "A08", "consultar_espera", "135 minutos", "0.000300"]:
            self.assertIn(esperado, log)


if __name__ == "__main__":
    unittest.main()

import asyncio
import io
import json
import tempfile
import unittest
import urllib.error
from pathlib import Path
from unittest.mock import patch

import numpy as np

import recuperar
import servidor_mcp


class RespuestaFalsa(io.BytesIO):
    def __enter__(self):
        return self

    def __exit__(self, *args):
        self.close()


def llamar(nombre: str, argumentos: dict) -> str:
    contenido = asyncio.run(servidor_mcp.mcp.call_tool(nombre, argumentos))
    if isinstance(contenido, tuple):
        contenido = contenido[0]
    return "".join(bloque.text for bloque in contenido)


class ServidorTest(unittest.TestCase):
    def test_publica_las_seis_tools_con_sus_argumentos_y_descripcion(self):
        tools = asyncio.run(servidor_mcp.mcp.list_tools())
        firmas = {t.name: sorted(t.inputSchema.get("properties", {})) for t in tools}
        self.assertEqual(firmas, {
            "buscar_documentos": ["consulta"],
            "consultar_camas": ["sector"],
            "consultar_guardia": ["especialidad"],
            "consultar_turnos": ["especialidad"],
            "consultar_farmacia": ["medicamento"],
            "consultar_espera": [],
        })
        for t in tools:
            self.assertTrue(t.description.strip(), t.name)

    def test_tool_de_api_arma_url_y_devuelve_json_como_texto(self):
        cuerpo = {"medicamento": "enalapril 10 mg", "stock": 3}
        with patch.object(servidor_mcp, "urlopen", return_value=RespuestaFalsa(json.dumps(cuerpo).encode())) as abrir:
            resultado = llamar("consultar_farmacia", {"medicamento": "enalapril 10 mg"})
        self.assertEqual(abrir.call_args.args[0], "http://localhost:8765/farmacia?medicamento=enalapril+10+mg")
        self.assertEqual(json.loads(resultado), cuerpo)

    def test_espera_no_lleva_parametros(self):
        with patch.object(servidor_mcp, "urlopen", return_value=RespuestaFalsa(b'{"minutos_por_nivel": {}}')) as abrir:
            llamar("consultar_espera", {})
        self.assertEqual(abrir.call_args.args[0], "http://localhost:8765/espera")

    def test_error_de_la_api_llega_al_modelo_con_las_opciones(self):
        cuerpo = b'{"error": "\'insulina\' no existe", "opciones": ["insulina NPH"]}'
        error = urllib.error.HTTPError("url", 404, "Not Found", {}, io.BytesIO(cuerpo))
        with patch.object(servidor_mcp, "urlopen", side_effect=error):
            resultado = llamar("consultar_farmacia", {"medicamento": "insulina"})
        self.assertIn("insulina NPH", json.loads(resultado)["opciones"])

    def test_buscar_documentos_usa_el_recuperador_con_top_k_2(self):
        class EncoderFalso:
            def encode(self, textos, tipo):
                return np.array([[1.0, 0.0] if "ayuno" in t.lower() else [0.6, 0.8] for t in textos])

        with tempfile.TemporaryDirectory() as carpeta:
            Path(carpeta, "norma.md").write_text("# Norma\n\nAyuno de 6 horas.\n\nTraer DNI.\n\nOtra cosa.\n",
                                                 encoding="utf-8")
            with patch.object(recuperar, "CORPUS", Path(carpeta)), \
                    patch.object(recuperar, "crear_encoder", return_value=EncoderFalso()), \
                    patch.object(servidor_mcp, "_indice", None):
                resultado = llamar("buscar_documentos", {"consulta": "¿Cuánto ayuno?"})
        self.assertEqual(resultado.split("\n\n")[0], "Ayuno de 6 horas.")
        self.assertEqual(len(resultado.split("\n\n")), 2)

    def test_el_servidor_no_usa_langchain(self):
        codigo = Path(servidor_mcp.__file__).read_text(encoding="utf-8")
        self.assertNotIn("langchain", codigo)
        self.assertIn("from mcp.server.fastmcp import FastMCP", codigo)


if __name__ == "__main__":
    unittest.main()

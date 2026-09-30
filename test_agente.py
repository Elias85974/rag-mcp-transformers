import io
import json
import tempfile
import unittest
import urllib.error
from pathlib import Path
from unittest.mock import patch

import numpy as np

import agente
import recuperar


class RespuestaFalsa(io.BytesIO):
    def __enter__(self):
        return self

    def __exit__(self, *args):
        self.close()


class HerramientasTest(unittest.TestCase):
    def test_nombres_y_argumentos(self):
        firmas = {h.name: sorted(h.args) for h in agente.HERRAMIENTAS}
        self.assertEqual(firmas, {
            "buscar_documentos": ["consulta"],
            "consultar_camas": ["sector"],
            "consultar_guardia": ["especialidad"],
            "consultar_turnos": ["especialidad"],
            "consultar_farmacia": ["medicamento"],
            "consultar_espera": [],
        })
        for herramienta in agente.HERRAMIENTAS:
            self.assertTrue(herramienta.description.strip(), herramienta.name)

    def test_api_arma_url_y_devuelve_json_como_texto(self):
        cuerpo = {"sector": "pediatria", "datos": {"libres": 7}}
        with patch.object(agente, "urlopen", return_value=RespuestaFalsa(json.dumps(cuerpo).encode())) as abrir:
            resultado = agente.consultar_farmacia.invoke({"medicamento": "enalapril 10 mg"})
        self.assertEqual(abrir.call_args.args[0], "http://localhost:8765/farmacia?medicamento=enalapril+10+mg")
        self.assertEqual(json.loads(resultado), cuerpo)

    def test_espera_no_lleva_parametros(self):
        with patch.object(agente, "urlopen", return_value=RespuestaFalsa(b'{"minutos_por_nivel": {}}')) as abrir:
            agente.consultar_espera.invoke({})
        self.assertEqual(abrir.call_args.args[0], "http://localhost:8765/espera")

    def test_error_de_la_api_llega_al_modelo_con_las_opciones(self):
        cuerpo = b'{"error": "\'insulina\' no existe", "opciones": ["insulina NPH"]}'
        error = urllib.error.HTTPError("url", 404, "Not Found", {}, io.BytesIO(cuerpo))
        with patch.object(agente, "urlopen", side_effect=error):
            resultado = agente.consultar_farmacia.invoke({"medicamento": "insulina"})
        self.assertIn("insulina NPH", json.loads(resultado)["opciones"])

    def test_buscar_documentos_usa_el_recuperador_de_la_parte_1(self):
        class EncoderFalso:
            def encode(self, textos, tipo):
                return np.array([[1.0, 0.0] if "ayuno" in t.lower() else [0.0, 1.0] for t in textos])

        with tempfile.TemporaryDirectory() as carpeta:
            Path(carpeta, "norma.md").write_text("# Norma\n\nAyuno de 6 horas.\n\nTraer DNI.\n", encoding="utf-8")
            with patch.object(recuperar, "CORPUS", Path(carpeta)), \
                    patch.object(recuperar, "crear_encoder", return_value=EncoderFalso()), \
                    patch.object(agente, "_indice", None):
                resultado = agente.buscar_documentos.invoke({"consulta": "¿Cuánto ayuno?"})
        self.assertEqual(resultado, "Ayuno de 6 horas.")


if __name__ == "__main__":
    unittest.main()

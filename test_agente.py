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


def conversacion_a10():
    from langchain_core.messages import AIMessage, HumanMessage, ToolMessage

    def uso(entrada, salida, costo):
        return {"usage_metadata": {"input_tokens": entrada, "output_tokens": salida, "total_tokens": entrada + salida},
                "response_metadata": {"token_usage": {"cost": costo}}}

    return [
        HumanMessage("¿Hay camas en pediatría y me puedo quedar?"),
        AIMessage("", tool_calls=[
            {"name": "consultar_camas", "args": {"sector": "pediatria"}, "id": "c1"},
            {"name": "buscar_documentos", "args": {"consulta": "acompañante pediatría"}, "id": "c2"},
        ], **uso(900, 200, 0.0003)),
        ToolMessage('{"datos": {"libres": 7}}', tool_call_id="c1", name="consultar_camas"),
        ToolMessage("Madre, padre o tutor pueden permanecer las 24 horas.", tool_call_id="c2", name="buscar_documentos"),
        AIMessage("Hay 7 camas libres y podés quedarte las 24 horas.", **uso(1100, 50, 0.0001)),
    ]


class ResumenTest(unittest.TestCase):
    def test_resumen_sigue_el_contrato_del_evaluador(self):
        resumen = agente.resumir(conversacion_a10())
        self.assertEqual(resumen["respuesta"], "Hay 7 camas libres y podés quedarte las 24 horas.")
        self.assertEqual(resumen["contextos"], ['{"datos": {"libres": 7}}',
                                                "Madre, padre o tutor pueden permanecer las 24 horas."])
        self.assertEqual(resumen["herramientas"], ["consultar_camas", "buscar_documentos"])

    def test_traza_registra_tools_tokens_y_costo_por_llamada(self):
        pasos = agente.resumir(conversacion_a10())["traza"]
        self.assertEqual([p["tipo"] for p in pasos], ["modelo", "tool", "tool", "modelo"])
        self.assertEqual(pasos[0]["entrada"], 900)
        self.assertEqual(pasos[0]["costo"], 0.0003)
        self.assertEqual(pasos[1]["nombre"], "consultar_camas")
        self.assertEqual(pasos[1]["argumentos"], {"sector": "pediatria"})
        self.assertEqual(pasos[1]["resultado"], '{"datos": {"libres": 7}}')

    def test_log_markdown_muestra_la_corrida_completa(self):
        fila = {"id": "A10", "pregunta": "¿Hay camas en pediatría y me puedo quedar?",
                **agente.resumir(conversacion_a10())}
        log = agente.log_markdown([fila])
        for esperado in ["A10", "¿Hay camas en pediatría y me puedo quedar?", "consultar_camas",
                         '"sector": "pediatria"', '{"datos": {"libres": 7}}', "Hay 7 camas libres",
                         "900", "0.000300", "0.000400"]:
            self.assertIn(esperado, log)

    def test_main_escribe_jsonl_y_log_por_pregunta(self):
        with tempfile.TemporaryDirectory() as carpeta:
            base = Path(carpeta)
            preguntas = base / "preguntas.jsonl"
            preguntas.write_text('{"id":"A10","pregunta":"¿Camas?"}\n{"id":"A11","pregunta":"¿Turnos?"}\n',
                                 encoding="utf-8")
            salida = base / "respuestas.jsonl"
            with patch.object(agente, "crear_agente"), \
                    patch.object(agente, "responder", return_value=agente.resumir(conversacion_a10())):
                agente.ejecutar(preguntas, salida)
            filas = [json.loads(linea) for linea in salida.read_text(encoding="utf-8").splitlines()]
            log = (base / "respuestas.log.md").read_text(encoding="utf-8")
        self.assertEqual([f["id"] for f in filas], ["A10", "A11"])
        self.assertEqual(set(filas[0]), {"id", "respuesta", "contextos", "herramientas"})
        self.assertIn("A11", log)


if __name__ == "__main__":
    unittest.main()

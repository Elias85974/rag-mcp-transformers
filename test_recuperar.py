import json
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

import numpy as np

import recuperar


class RecuperarTest(unittest.TestCase):
    def test_corpus_conserva_texto_y_titulos_para_busqueda(self):
        with tempfile.TemporaryDirectory() as carpeta:
            Path(carpeta, "norma.md").write_text(
                "# Hospital\n\n## Estudios\n\nAyuno de 6 horas.\n\nTraer DNI.\n",
                encoding="utf-8",
            )
            fragmentos = recuperar.cargar_fragmentos(Path(carpeta), "parrafo")
        self.assertEqual([f.texto for f in fragmentos], ["Ayuno de 6 horas.", "Traer DNI."])
        self.assertIn("Hospital", fragmentos[0].embedding_texto)
        self.assertIn("Estudios", fragmentos[0].embedding_texto)

    def test_orden_topk_y_umbral(self):
        vectores = np.array([[1.0, 0.0], [0.8, 0.6], [0.0, 1.0]])
        self.assertEqual(recuperar.seleccionar(np.array([1.0, 0.0]), vectores, 2, 0.7), [0, 1])
        self.assertEqual(recuperar.seleccionar(np.array([1.0, 0.0]), vectores, 3, 0.9), [0])

    def test_jsonl_conserva_ids_y_procesa_todas_las_preguntas(self):
        class EncoderFalso:
            def encode(self, textos, tipo):
                return np.array([[1.0, 0.0] if "ayuno" in t.lower() else [0.0, 1.0] for t in textos])

        with tempfile.TemporaryDirectory() as carpeta:
            base = Path(carpeta)
            (base / "norma.md").write_text("# Norma\n\nAyuno de 6 horas.\n\nTraer DNI.\n", encoding="utf-8")
            preguntas = base / "preguntas.jsonl"
            preguntas.write_text(
                '{"id":"R01","pregunta":"¿Ayuno?"}\n{"id":"R02","pregunta":"¿DNI?"}\n',
                encoding="utf-8",
            )
            salida = base / "salida.jsonl"
            with patch.object(recuperar, "crear_encoder", return_value=EncoderFalso()):
                recuperar.ejecutar(preguntas, salida, base, "falso", "parrafo", 1, 0.0)
            filas = [json.loads(linea) for linea in salida.read_text(encoding="utf-8").splitlines()]
        self.assertEqual(filas, [
            {"id": "R01", "fragmentos": ["Ayuno de 6 horas."]},
            {"id": "R02", "fragmentos": ["Traer DNI."]},
        ])


if __name__ == "__main__":
    unittest.main()

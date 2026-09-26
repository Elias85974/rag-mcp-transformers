"""Recuperación vectorial de normas del Hospital Arroyo Claro."""

import argparse
import json
import re
from dataclasses import dataclass
from pathlib import Path

import numpy as np


CORPUS = Path(__file__).parent / "datos" / "corpus"
MODELOS = {
    "bert": "google-bert/bert-base-multilingual-cased",
    "minilm": "sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2",
    "e5": "intfloat/multilingual-e5-small",
}


@dataclass(frozen=True)
class Fragmento:
    texto: str
    embedding_texto: str


def cargar_fragmentos(carpeta: Path, fragmentacion: str) -> list[Fragmento]:
    """Divide Markdown por párrafo o sección; los títulos solo ayudan al embedding."""
    fragmentos = []
    for ruta in sorted(carpeta.glob("*.md")):
        titulo = ""
        seccion = ""
        parrafos = []

        def agregar():
            if not parrafos:
                return
            if fragmentacion == "parrafo":
                textos = parrafos
            elif fragmentacion == "seccion":
                textos = ["\n\n".join(parrafos)]
            else:
                raise ValueError(f"Fragmentación desconocida: {fragmentacion}")
            for texto in textos:
                fragmentos.append(Fragmento(texto, "\n".join(filter(None, [titulo, seccion, texto]))))
            parrafos.clear()

        for bloque in re.split(r"\n\s*\n", ruta.read_text(encoding="utf-8").strip()):
            if bloque.startswith("# "):
                agregar()
                titulo = bloque[2:].strip()
                seccion = ""
            elif bloque.startswith("## "):
                agregar()
                seccion = bloque[3:].strip()
            elif bloque.strip():
                parrafos.append(bloque.strip())
        agregar()
    return fragmentos


class EncoderOraciones:
    def __init__(self, modelo: str):
        from sentence_transformers import SentenceTransformer

        self.modelo = SentenceTransformer(MODELOS[modelo], device="cpu")
        self.prefijo = modelo == "e5"

    def encode(self, textos: list[str], tipo: str) -> np.ndarray:
        if self.prefijo:
            textos = [f"{'query' if tipo == 'consulta' else 'passage'}: {texto}" for texto in textos]
        return self.modelo.encode(textos, batch_size=16, show_progress_bar=False)


class EncoderBert:
    def __init__(self):
        from transformers import AutoModel, AutoTokenizer

        self.tokenizador = AutoTokenizer.from_pretrained(MODELOS["bert"])
        self.modelo = AutoModel.from_pretrained(MODELOS["bert"]).eval().to("cpu")

    def encode(self, textos: list[str], tipo: str) -> np.ndarray:
        import torch

        vectores = []
        with torch.no_grad():
            for inicio in range(0, len(textos), 16):
                lote = self.tokenizador(textos[inicio:inicio + 16], padding=True, truncation=True,
                                         max_length=512, return_tensors="pt")
                salida = self.modelo(**lote).last_hidden_state
                mascara = lote["attention_mask"].unsqueeze(-1)
                promedio = (salida * mascara).sum(1) / mascara.sum(1)
                vectores.append(promedio.numpy())
        return np.concatenate(vectores)


def crear_encoder(modelo: str):
    return EncoderBert() if modelo == "bert" else EncoderOraciones(modelo)


def seleccionar(consulta: np.ndarray, corpus: np.ndarray, top_k: int, umbral: float) -> list[int]:
    """Índices en orden de coseno descendente, con desempate reproducible."""
    consulta = np.asarray(consulta, dtype=float)
    corpus = np.asarray(corpus, dtype=float)
    denominadores = np.linalg.norm(corpus, axis=1) * np.linalg.norm(consulta)
    cosenos = np.divide(corpus @ consulta, denominadores, out=np.zeros(len(corpus)), where=denominadores != 0)
    orden = np.argsort(-cosenos, kind="stable")
    return [int(i) for i in orden if cosenos[i] >= umbral][:top_k]


def ejecutar(preguntas: Path, salida: Path, carpeta: Path, modelo: str,
            fragmentacion: str, top_k: int, umbral: float) -> None:
    fragmentos = cargar_fragmentos(carpeta, fragmentacion)
    if not fragmentos:
        raise ValueError(f"No se encontraron fragmentos en {carpeta}")
    encoder = crear_encoder(modelo)
    vectores = encoder.encode([f.embedding_texto for f in fragmentos], "pasaje")
    filas = [json.loads(linea) for linea in preguntas.read_text(encoding="utf-8").splitlines() if linea.strip()]
    consultas = encoder.encode([fila["pregunta"] for fila in filas], "consulta")
    with salida.open("w", encoding="utf-8") as archivo:
        for fila, consulta in zip(filas, consultas):
            indices = seleccionar(consulta, vectores, top_k, umbral)
            resultado = {"id": fila["id"], "fragmentos": [fragmentos[i].texto for i in indices]}
            archivo.write(json.dumps(resultado, ensure_ascii=False) + "\n")


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--preguntas", type=Path, required=True)
    parser.add_argument("--salida", type=Path, required=True)
    parser.add_argument("--modelo", choices=MODELOS, default="minilm")
    parser.add_argument("--fragmentacion", choices=["parrafo", "seccion"], default="parrafo")
    parser.add_argument("--top-k", type=int, default=1)
    parser.add_argument("--umbral", type=float, default=0.0)
    args = parser.parse_args()
    if args.top_k < 1:
        parser.error("--top-k debe ser positivo")
    ejecutar(args.preguntas, args.salida, CORPUS, args.modelo, args.fragmentacion, args.top_k, args.umbral)


if __name__ == "__main__":
    main()

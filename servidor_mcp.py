"""Servidor MCP del Hospital Arroyo Claro: documentos y API del día por stdio."""

import urllib.error
from urllib.parse import urlencode
from urllib.request import urlopen

from mcp.server.fastmcp import FastMCP

import recuperar


API = "http://localhost:8765"
TOP_K = 2
mcp = FastMCP("hospital-arroyo-claro")
_indice = None


def llamar_api(ruta: str, **parametros) -> str:
    """Devuelve el JSON de la API como texto, también cuando es un error con opciones válidas."""
    url = f"{API}{ruta}" + (f"?{urlencode(parametros)}" if parametros else "")
    try:
        with urlopen(url) as respuesta:
            return respuesta.read().decode("utf-8")
    except urllib.error.HTTPError as error:
        return error.read().decode("utf-8")


@mcp.tool()
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


@mcp.tool()
def consultar_camas(sector: str) -> str:
    """Camas de hoy en un sector de internación: total, ocupadas y libres. Ejemplos de sector:
    pediatria, terapia_intensiva, maternidad. Si el sector no existe, devuelve las opciones válidas."""
    return llamar_api("/camas", sector=sector)


@mcp.tool()
def consultar_guardia(especialidad: str) -> str:
    """Profesionales de guardia hoy en una especialidad y su horario. Ejemplo: cardiologia.
    Si la especialidad no existe, devuelve las opciones válidas."""
    return llamar_api("/guardia", especialidad=especialidad)


@mcp.tool()
def consultar_turnos(especialidad: str) -> str:
    """Próximos turnos disponibles (fecha y hora) en una especialidad. Ejemplo: traumatologia.
    Si la especialidad no existe, devuelve las opciones válidas."""
    return llamar_api("/turnos", especialidad=especialidad)


@mcp.tool()
def consultar_farmacia(medicamento: str) -> str:
    """Stock actual de un medicamento en la farmacia del hospital y, si no hay, la fecha de reposición.
    Usar el nombre con la dosis, por ejemplo "enalapril 10 mg". Si no existe, devuelve las opciones válidas."""
    return llamar_api("/farmacia", medicamento=medicamento)


@mcp.tool()
def consultar_espera() -> str:
    """Minutos de espera actuales en la guardia para cada nivel de triage (rojo, naranja, amarillo,
    verde, azul)."""
    return llamar_api("/espera")


if __name__ == "__main__":
    mcp.run()

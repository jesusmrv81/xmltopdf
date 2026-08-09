"""
Servicio FastAPI que expone cfdi-pdf como microservicio.

cfdi-pdf es una biblioteca 100% pura: no importa FastAPI ni ningún framework
web. Este archivo es solo un adaptador de ejemplo que muestra cómo servirla.

El método `render_bytes_from_string()` devuelve los bytes del PDF sin escribir
a disco, que es exactamente lo que necesita un endpoint HTTP.

Ejecución:
    pip install "fastapi[standard]"
    uvicorn fastapi_service:app --reload

Endpoints:
    POST /render    — body = XML CFDI crudo → respuesta PDF
    GET  /templates — lista de templates disponibles
    GET  /health    — healthcheck simple

Ejemplo con curl:
    curl -s -X POST http://localhost:8000/render \
         -H "Content-Type: application/xml" \
         --data-binary @factura.xml -o factura.pdf
"""

from typing import Annotated

from fastapi import Body, FastAPI, HTTPException, Query
from fastapi.responses import Response

from cfdi_pdf import CFDIPDF
from cfdi_pdf.exceptions import CFDIPDFError

app = FastAPI(title="CFDI PDF Service", version="0.1.0")

# Instancia única reutilizada entre requests. La librería no guarda estado
# mutable por request, así que es segura para uso concurrente.
converter = CFDIPDF(template="minimal")


@app.get("/health")
def health() -> dict[str, str]:
    """Healthcheck básico."""
    return {"status": "ok"}


@app.get("/templates")
def list_templates() -> dict[str, list[str]]:
    """Lista los templates disponibles."""
    return {"templates": converter.list_templates()}


@app.post("/render")
def render_pdf(
    xml: Annotated[
        bytes,
        Body(media_type="application/xml", description="Contenido crudo del CFDI XML"),
    ],
    template: Annotated[str | None, Query(description="Template a usar (opcional)")] = None,
) -> Response:
    """
    Convierte un CFDI 4.0 XML a PDF.

    El endpoint es `def` (síncrono) a propósito: FastAPI lo ejecuta en un
    threadpool, de modo que el trabajo CPU-intensivo de WeasyPrint no bloquea
    el event loop.
    """
    try:
        xml_content = xml.decode("utf-8")
    except UnicodeDecodeError as exc:
        raise HTTPException(status_code=422, detail="Body no es UTF-8 válido") from exc

    if not xml_content.strip():
        raise HTTPException(status_code=422, detail="Body XML vacío")

    try:
        pdf_bytes, filename = converter.render_bytes_from_string(xml_content, template=template)
    except CFDIPDFError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc

    return Response(
        content=pdf_bytes,
        media_type="application/pdf",
        headers={"Content-Disposition": f'attachment; filename="{filename}"'},
    )

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import Response

from .models import StudyParameters
from .calculations import run as run_calculations
from .curves import generate_coordenograma
from .report import generate_pdf

app = FastAPI(
    title="Gerador de Estudos de Proteção e Seletividade",
    description="API para gerar estudos de coordenação de proteção de média tensão (ABNT NBR 14039 / ENERGISA NDU 002).",
    version="1.0.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://127.0.0.1:5173"],
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/api/health")
def health():
    return {"status": "ok"}


@app.post("/api/gerar-estudo")
def gerar_estudo(params: StudyParameters):
    try:
        result = run_calculations(params)
        png_fase, png_neutro = generate_coordenograma(result)
        pdf_bytes = generate_pdf(result, png_fase, png_neutro)
    except Exception as exc:
        raise HTTPException(status_code=422, detail=str(exc))

    filename = f"Estudo_Protecao_{params.cliente.razao_social.replace(' ', '_')}.pdf"
    return Response(
        content=pdf_bytes,
        media_type="application/pdf",
        headers={"Content-Disposition": f'attachment; filename="{filename}"'},
    )

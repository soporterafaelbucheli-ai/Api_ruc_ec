from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import libsql              # ← paquete NUEVO (no libsql_client)
import os

app = FastAPI(title="API Catastro RUC SRI")

# En Render estas variables deben estar configuradas en "Environment".
# Si no existen, la API falla al arrancar (mejor que fallar silenciosamente
# con un token truncado).
TURSO_URL   = os.environ["TURSO_URL"]
TURSO_TOKEN = os.environ["TURSO_TOKEN"]


class Contribuyente(BaseModel):
    ruc: str
    razon_social: str
    estado: str


@app.get("/")
def inicio():
    return {"mensaje": "API de RUC funcionando correctamente"}


@app.get("/api/ruc/{ruc}", response_model=Contribuyente)
def consultar_ruc(ruc: str):
    # Validación del RUC
    if len(ruc) != 13 or not ruc.isdigit():
        raise HTTPException(
            status_code=400,
            detail="El RUC debe tener 13 dígitos numéricos."
        )

    # Conexión + consulta con manejo de errores explícito
    try:
        conn = libsql.connect(database=TURSO_URL, auth_token=TURSO_TOKEN)
        cur = conn.execute(
            "SELECT ruc, razon_social, estado FROM contribuyentes WHERE ruc = ?",
            (ruc,)
        )
        row = cur.fetchone()
        conn.close()
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error de base de datos: {type(e).__name__}: {e}"
        )

    if row is None:
        raise HTTPException(status_code=404, detail="RUC no encontrado en el catastro.")

    return Contribuyente(ruc=row[0], razon_social=row[1], estado=row[2])
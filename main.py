from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import libsql

app = FastAPI(title="API Catastro RUC SRI")

TURSO_URL = "libsql://rucec-denisfer2000.aws-sa-east-1.turso.io"
TURSO_TOKEN = "eyJhbGciOiJFZERTQSIsInR5cCI6IkpXVCJ9.eyJhIjoicnciLCJpYXQiOjE3OTI5OTY1NzgsImlkIjoiMDFhMTc2NjgtOTcwMS03ZmE2LTllNmEtNTk0ZDUzZmU1MDY2Iiwia2lkIjoiM3kxS1lKREdwM0V2ZkZLQkxpdjc1WE9fSndzVGt6TGY2OWhFenNiTnl5ayIsInJpZCI6ImYxMTU2MTM0LTg1MTUtNGUwOS1hMmRjLWYzNDI0OGM2Y2U0YiJ9.dbtRIbQ7mnANp4BDO_iEC8QkJTpgKfzVbNUPMqT9Nd3Ka1dISqaeMZEABlAREKUMyFfDdCUjUDCsJXR_nAAWDw"

class Contribuyente(BaseModel):
    ruc: str
    razon_social: str
    estado: str

@app.get("/")
def inicio():
    return {"mensaje": "API de RUC funcionando correctamente"}

@app.get("/api/ruc/{ruc}", response_model=Contribuyente)
def consultar_ruc(ruc: str):
    if len(ruc) != 13 or not ruc.isdigit():
        raise HTTPException(status_code=400, detail="El RUC debe tener 13 dígitos numéricos.")
    
    try:
        conn = libsql.connect(database=TURSO_URL, auth_token=TURSO_TOKEN)
        cur = conn.execute("SELECT ruc, razon_social, estado FROM contribuyentes WHERE ruc = ?", (ruc,))
        row = cur.fetchone()
        conn.close()
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error de base de datos: {type(e).__name__}: {e}")

    if row is None:
        raise HTTPException(status_code=404, detail="RUC no encontrado en el catastro.")
    
    return Contribuyente(ruc=row[0], razon_social=row[1], estado=row[2])

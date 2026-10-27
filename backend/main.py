from fastapi import FastAPI, UploadFile, File, Depends
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
from database import SessionLocal, LedgerDB, init_db
from pydantic import BaseModel
import uuid
import datetime
import random

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

init_db()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

class SoilData(BaseModel):
    ph: float
    nitrogen: float
    phosphorus: float
    potassium: float
    elevation: float

@app.get("/api/farm")
def get_farm_data(db: Session = Depends(get_db)):
    ledger_records = db.query(LedgerDB).all()
    ledger_list = [{"id": r.id, "kind": r.kind, "category": r.category, "label": r.label, "amount": r.amount, "date": r.date} for r in ledger_records]
    
    return {
        "profile": {
            "farmerName": "Sanjay",
            "village": "Kondampatty",
            "district": "Coimbatore",
            "acres": 2.5,
            "elevation": 411,
            "hasPolyhouse": True,
            "soil": {"ph": 6.5, "nitrogen": "Medium", "phosphorus": "High", "potassium": "Low"}
        },
        "activeCropId": "tomato",
        "sowingDate": (datetime.datetime.now() - datetime.timedelta(days=38)).isoformat(),
        "tasks": [
            {"id": "f0", "day": 1, "product": "Farmyard manure", "type": "Organic", "unit": "kg", "method": "Base", "dosePerAcre": 1000, "done": None},
            {"id": "f1", "day": 35, "product": "Urea", "type": "Fertilizer", "unit": "kg", "method": "Top dressing", "dosePerAcre": 35, "done": None}
        ],
        "ledger": ledger_list
    }

@app.post("/api/diagnose")
async def diagnose_leaf(file: UploadFile = File(...)):
    diseases = ["Early Blight", "Nitrogen Burn", "Healthy", "Spider Mites"]
    verdicts = ["Biological disease", "Chemical burn / toxicity", "None", "Pest attack"]
    idx = random.randint(0, 1) 
    return {"id": uuid.uuid4().hex, "date": datetime.datetime.now().isoformat(), "name": diseases[idx], "verdict": verdicts[idx], "confidence": round(random.uniform(0.85, 0.98), 2)}

@app.post("/api/recommend-crop")
def recommend_crop(data: SoilData):
    return {"recommended_crop": "Tomato", "score": 94, "reasons": ["Ideal pH level", "Matches elevation profile"]}

class LedgerEntry(BaseModel):
    kind: str; category: str; label: str; amount: float; date: str

@app.post("/api/ledger")
def add_ledger(entry: LedgerEntry, db: Session = Depends(get_db)):
    db_entry = LedgerDB(id=f"l_{uuid.uuid4().hex[:8]}", kind=entry.kind, category=entry.category, label=entry.label, amount=entry.amount, date=entry.date)
    db.add(db_entry)
    db.commit()
    db.refresh(db_entry)
    return db_entry
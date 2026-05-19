"""
Tally XML Converter - FastAPI Backend
Main application entry point
"""
import os
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from dotenv import load_dotenv

from routes.bank_routes import router as bank_router
from routes.sales_routes import router as sales_router
from routes.purchase_routes import router as purchase_router
from routes.template_routes import router as template_router
from routes.chat_routes import router as chat_router
from routes.debit_note_routes import router as debit_note_router
from routes.credit_note_routes import router as credit_note_router

load_dotenv()

# DEBUG: Verify Env Load
print("DEBUG: API KEY LOADED FROM ENV:", os.getenv("GROQ_API_KEY")[:6] + "..." if os.getenv("GROQ_API_KEY") else "None")

app = FastAPI(
    title="Tally XML Converter API",
    description="AI-powered Excel to Tally XML conversion engine",
    version="1.0.0",
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/")
async def root():
    return {"message": "Tally XML Converter API is running", "version": "1.0.0"}


@app.get("/health")
async def health_check():
    return {"status": "healthy"}


@app.get("/test-key")
async def test_key():
    key = os.getenv("GROQ_API_KEY")
    if key and key.startswith("gsk_"):
        return {"status": "KEY OK", "key_format": "gsk_..."}
    else:
        return {"status": "KEY MISSING", "reason": "Placeholder or invalid format"}


# Register routers
app.include_router(bank_router, prefix="/api/bank", tags=["Bank Vouchers"])
app.include_router(sales_router, prefix="/api/sales", tags=["Sales Vouchers"])
app.include_router(purchase_router, prefix="/api/purchase", tags=["Purchase Vouchers"])
app.include_router(template_router, prefix="/api/templates", tags=["Templates"])
app.include_router(chat_router, prefix="/api/chat", tags=["Chatbot"])
app.include_router(debit_note_router, prefix="/api/debit-note", tags=["Debit Notes"])
app.include_router(credit_note_router, prefix="/api/credit-note", tags=["Credit Notes"])

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)

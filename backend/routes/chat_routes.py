import os
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import List, Optional

router = APIRouter()

class ChatRequest(BaseModel):
    message: str
    errors: Optional[List[dict]] = []
    fileName: Optional[str] = "Unknown"

@router.post("/")
async def chat_with_bot(req: ChatRequest):
    api_key = os.getenv("GROQ_API_KEY", "").strip()
    
    # FAIL-SAFE CHECK: ONLY BLOCK IF COMPLETELY MISSING
    if not api_key:
        raise HTTPException(
            status_code=500, 
            detail="Groq API key is missing. Please add your 'gsk-...' key to backend/.env"
        )

    try:
        from openai import AsyncOpenAI
        client = AsyncOpenAI(api_key=api_key, base_url="https://api.groq.com/openai/v1")

        error_context = ""
        if req.errors:
            error_context = "Current Active Validation Errors (Top 5):\n"
            for err in req.errors[:5]:
                error_context += f"- Row {err.get('row')}, Field [{err.get('field')}]: {err.get('error')}. Expected: {err.get('expected_format')}.\n"
        else:
            error_context = "No active errors. The file looks clean!"

        system_prompt = f"""You are a helpful AI assistant for a Tally XML converter.
The user is working with a new multi-ledger Excel template for Sales and Purchase.
The core fields are: DATE, INVOICE NO, CASH/PARTY, PURCHASE/SALES LEDGER, IGST/CENTRAL GST LEDGER, UT/STATE GST LEDGER, TAXABLE AMOUNT, GST SLAB, GST, and BILL AMOUNT.

Your job is to help users (accountants) fix errors in this specific structure. 
- If a total doesn't match, explain that BILL AMOUNT should be TAXABLE AMOUNT + GST.
- If ledgers are missing, tell them to specify the Tally Ledger names in the ledger columns.
- Suggest Excel formulas like `=SUM(G2+J2)` for Bill Amount.

CRITICAL RULES:
1. Detect the user's language seamlessly (English, Hindi, Hinglish, Marathi, etc.) and respond back in the *SAME* language.
2. Use the provided CONTEXT below to answer their queries directly. If they mention an error, tell them exactly how to fix it in Excel.
3. Keep instructions very step-by-step and clear. Let them know what Excel menus to click (e.g. "Select column -> Format Cells -> Custom").
4. Always provide formulas if it saves them time, such as `=TEXT(A2,"DD-MM-YYYY")`.
5. If the user explicitly asks you to auto-fix errors, or re-validate the file, or generate the XML file, you MUST append a trigger code exactly at the END of your response.
   - For auto-fix: append "[ACTION:AUTO_FIX]"
   - For generate XML: append "[ACTION:GENERATE_XML]"
   - For re-validate/re-upload: append "[ACTION:REVALIDATE]"

CONTEXT:
File Uploaded: {req.fileName}
{error_context}
"""

        response = await client.chat.completions.create(
            model="llama3-8b-8192",
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": req.message}
            ],
            temperature=0.7,
            max_tokens=400,
        )

        reply = response.choices[0].message.content.strip()
        return {"response": reply}

    except Exception as e:
        print("Chat Error:", e)
        raise HTTPException(status_code=500, detail="I am currently experiencing an issue connecting to the AI backend. Please try again later.")

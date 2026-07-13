import os
import json
from pathlib import Path
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from dotenv import load_dotenv
#from openai import OpenAI
from google import genai
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware


load_dotenv()

client = genai.Client(api_key=os.getenv("GEMINI_API_KEY"))
app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"]
)

DATA_FILE = Path(__file__).parent / "data" / "businesses.json"

def load_businesses():
    with open(DATA_FILE, 'r', encoding='utf-8') as f:
        return json.load(f)

class Query(BaseModel):
    message:str
    business_id:str

@app.post("/ask")
async def ask(query:Query):
    businesses = load_businesses()
    business = businesses.get(query.business_id)

    if not business:
        raise HTTPException(status_code=404, detail=f"Unknown business id: {query.business_id}")
    
    system_prompt = (
        f"You are the customer support assistant for {business['name']}. "
        f"Answer customer questions using ONLY the business information below. "
        f"If the answer isn't in it, politely say you're not sure and suggest they "
        f"contact the business directly. Keep answers short and friendly -- 2 to 3 "
        f"sentences. Do NOT use code blocks.\n\n"               
        f"Business information:{business['info']}"
    )

    try:
        response = client.models.generate_content(
        model="gemini-3-flash-preview",
        contents=[
            {
                "role": "user",
                "parts": [
                    {"text": system_prompt + "\n\nUser question: " + query.message}
                ]
            }
        ],
        config=genai.types.GenerateContentConfig(
            max_output_tokens=300,
            thinking_config=genai.types.ThinkingConfig(thinking_budget=0)
        )
    )
        return {"response": response.text}
    
    except Exception as e:
        print("Gemini error:",e)
        raise HTTPException(status_code=500, detail="Something went wrong. Please try again in a moment")

app.mount("/", StaticFiles(directory="static", html=True,), name="static")

import time
import requests
from pyairtable import Api

AIRTABLE_TOKEN = "patsJGN81X4gASjQn.5db0f12c4fe0bdd6dc345f3df1f67da75ea65c28da66fbf7787436d32658f574"
GEMINI_API_KEY = "AQ.Ab8RN6KynkE1Ro6_dHOJ0Y5rixFRoOY9Yuf-w8nDKTriAhdHZQ"
BASE_ID = "appQHRt45Wgtu0ZOc"
INBOX_TABLE_ID = "tbls243tW39fhvMYe"

SYSTEM_PROMPT = """You are Danial's Communication Copilot. Write replies exactly as Danial would. Never mention AI or automation. Danial is a trader, crypto educator, founder of KurdChain community, and IB for CXM broker. Reply like a friend - warm, natural, human. If Kurdish Latin input, always reply in Sorani Kurdish script. If Iraqi Arabic, reply in warm Baghdadi dialect. Max 2 emojis. If you don't know the answer, reply exactly: NEEDS DANIAL INPUT. Return only the final reply, nothing else."""

def check_inbox():
    api = Api(AIRTABLE_TOKEN)
    table = api.table(BASE_ID, INBOX_TABLE_ID)
    records = table.all(formula="{Status}='1. Waiting for Gemini'")
    
    for record in records:
        record_id = record['id']
        incoming = record['fields'].get('Incoming Message', '')
        note = record['fields'].get('Danial Note', '')
        
        if not incoming:
            continue
            
        prompt = f"{SYSTEM_PROMPT}\n\nIncoming Message: {incoming}\nDanial Note: {note}\n\nWrite the reply now:"
        
        response = requests.post(
            f"https://generativelanguage.googleapis.com/v1beta/models/gemini-2.5-pro:generateContent?key={GEMINI_API_KEY}",
            json={"contents": [{"parts": [{"text": prompt}]}]},
            timeout=30
        )
        
        data = response.json()
        draft = data['candidates'][0]['content']['parts'][0]['text']
        
        table.update(record_id, {
            'Gemini Draft': draft,
            'Status': '2. Review'
        })
        
        print(f"✅ Processed: {incoming[:50]}")

while True:
    try:
        print("🔍 Checking inbox...")
        check_inbox()
        print("⏳ Waiting 60 seconds...")
    except Exception as e:
        print(f"❌ Error: {e}")
    time.sleep(60)

import time
import requests
from pyairtable import Api
import signal
import sys

AIRTABLE_TOKEN = "patohYM4S7UIG2xM5.45ee82250de865ae8174bedbc8f6d60aa99bb192fe3d22378af34a03d778cb62"
GEMINI_API_KEY = "AQ.Ab8RN6KPU3FQJyuU55owbAlVZdbBBiHDF8RZtYKVKFMBXlLOvg"
BASE_ID = "appQHRt45Wgtu0ZOc"
INBOX_TABLE_ID = "tbls243tW39fhvMYe"
KB_TABLE_ID = "tbl2BfNIjKLinkZlE"

GEMINI_URL = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-2.5-pro:generateContent?key={GEMINI_API_KEY}"

SYSTEM_PROMPT = """You are Danial's Communication Copilot. Write replies exactly as Danial would. Never mention AI or automation. Danial is a trader, crypto educator, founder of KurdChain community, and IB for CXM broker. Reply like a friend - warm, natural, human. If Kurdish Latin input, always reply in Sorani Kurdish script. If Iraqi Arabic, reply in warm Baghdadi dialect. Max 2 emojis. If you don't know the answer, reply exactly: NEEDS DANIAL INPUT. Return only the final reply, nothing else."""

def signal_handler(sig, frame):
    print("Bot stopped.")
    sys.exit(0)

signal.signal(signal.SIGTERM, signal_handler)
signal.signal(signal.SIGINT, signal_handler)

def get_knowledge_base():
    try:
        api = Api(AIRTABLE_TOKEN)
        table = api.table(BASE_ID, KB_TABLE_ID)
        records = table.all()
        knowledge = ""
        for record in records:
            topic = record['fields'].get('Topic', '')
            info = record['fields'].get('Information', '')
            if topic and info:
                knowledge += f"{topic}: {info}\n\n"
        return knowledge
    except Exception as e:
        print(f"KB error: {e}")
        return ""

def call_gemini(prompt_text, retries=3, wait=10):
    body = {
        "contents": [{"parts": [{"text": prompt_text}]}],
        "generationConfig": {"temperature": 0.3}
    }
    for attempt in range(1, retries + 1):
        try:
            response = requests.post(GEMINI_URL, json=body, timeout=120)
            response.raise_for_status()
            data = response.json()
            return data["candidates"][0]["content"]["parts"][0]["text"].strip()
        except Exception as e:
            print(f"Attempt {attempt}/{retries} failed: {e}")
            if attempt < retries:
                time.sleep(wait)
    raise Exception("All attempts failed.")

def check_inbox():
    api = Api(AIRTABLE_TOKEN)
    table = api.table(BASE_ID, INBOX_TABLE_ID)
    records = table.all(formula="{Status}='1. Waiting for Gemini'")

    if not records:
        print("No new messages.")
        return

    knowledge = get_knowledge_base()

    for record in records:
        record_id = record['id']
        incoming = record['fields'].get('Incoming Message', '')
        note = record['fields'].get('Danial Note', '')

        if not incoming:
            continue

        prompt = f"{SYSTEM_PROMPT}\n\nKNOWLEDGE BASE:\n{knowledge}\n\nIncoming Message: {incoming}\nDanial Note: {note}\n\nWrite the reply now:"

        try:
            draft = call_gemini(prompt)
            table.update(record_id, {
                'Gemini Draft': draft,
                'Status': '2. Review'
            })
            print(f"✅ Processed: {incoming[:50]}")
        except Exception as e:
            print(f"❌ Failed: {e}")

print("🤖 Danial Reply Bot started!")
while True:
    try:
        print("🔍 Checking inbox...")
        check_inbox()
        print("⏳ Sleeping 60 seconds...")
        time.sleep(60)
    except Exception as e:
        print(f"❌ Error: {e}")
        time.sleep(60)

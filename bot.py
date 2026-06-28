import asyncio
import time
import requests
from pyairtable import Api
from telethon import TelegramClient, events
from telethon.sessions import StringSession

# ── Credentials ──
AIRTABLE_TOKEN = "patohYM4S7UIG2xM5.45ee82250de865ae8174bedbc8f6d60aa99bb192fe3d22378af34a03d778cb62"
OPENROUTER_API_KEY = "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"
BASE_ID = "appQHRt45Wgtu0ZOc"
INBOX_TABLE_ID = "tbls243tW39fhvMYe"
KB_TABLE_ID = "tbl2BfNIjKLinkZlE"

# ── Telegram ──
API_ID = 33828680
API_HASH = "11b34dc04686e99af9548b06c80ed2b0"
SESSION_STRING = "1ApWapzMBu1DrAwlCxzBspt_OVQ2kLGeTCXMlHDKc_tUEDMM-qzoEuTB-hWkqWrxYere7JMCh3QUoKz9miyO0vVmj_dpCvEt2WAMWxNN4DpbIm0ijmVFwaLoT_wrkluUTj8qawmcvosGUn4q-7LHp4cNdc_P9-UkHge6XDjc4vBOwo3MXLXsoOilYg1Qx0el0GHkiUIk2pxTfFTF3GuzOVs-oO-NwB-XqsXavEfjGMYq7roRzPszdVlKnqYJCVfkkcWihi2Dpt_EYqZj5sDVs5NwFnUMBpgegcpieNThznUEUYjYAHb3PqxHYMn_rCodwIKpeKFG4B22Gx6cPKzCP7FE7UuoxJdU="
BOT_TOKEN = "8642746419:AAGsLH1qXWKNJ8gw09paVgALnqZaTnhxn9A"

OPENROUTER_URL = "https://openrouter.ai/api/v1/chat/completions"

SYSTEM_PROMPT = """You are Danial's Communication Copilot. Write replies exactly as Danial would. Never mention AI or automation. Danial is a trader, crypto educator, founder of KurdChain community, and IB for CXM broker. Reply like a friend - warm, natural, human. If Kurdish Latin input, always reply in Sorani Kurdish script. If Iraqi Arabic, reply in warm Baghdadi dialect. Max 2 emojis. If you don't know the answer, reply exactly: NEEDS DANIAL INPUT. Return only the final reply, nothing else."""

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

def call_ai(prompt_text, retries=3, wait=10):
    headers = {
        "Authorization": f"Bearer {OPENROUTER_API_KEY}",
        "Content-Type": "application/json"
    }
    body = {
        "model": "google/gemini-2.5-pro",
        "messages": [
            {"role": "user", "content": prompt_text}
        ]
    }
    for attempt in range(1, retries + 1):
        try:
            response = requests.post(OPENROUTER_URL, headers=headers, json=body, timeout=120)
            response.raise_for_status()
            data = response.json()
            return data["choices"][0]["message"]["content"].strip()
        except Exception as e:
            print(f"Attempt {attempt}/{retries} failed: {e}")
            if attempt < retries:
                time.sleep(wait)
    raise Exception("All attempts failed.")

def save_to_airtable(sender_name, sender_id, message_text, draft, platform="Telegram"):
    try:
        api = Api(AIRTABLE_TOKEN)
        table = api.table(BASE_ID, INBOX_TABLE_ID)
        table.create({
            "Sender Name": sender_name,
            "Chat ID": str(sender_id),
            "Platform": platform,
            "Incoming Message": message_text,
            "Gemini Draft": draft,
            "Status": "4. Done"
        })

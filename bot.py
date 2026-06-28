import asyncio
import time
import requests
from pyairtable import Api
from telethon import TelegramClient, events
from telethon.sessions import StringSession

AIRTABLE_TOKEN = "patohYM4S7UIG2xM5.45ee82250de865ae8174bedbc8f6d60aa99bb192fe3d22378af34a03d778cb62"
OPENROUTER_API_KEY = "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"
BASE_ID = "appQHRt45Wgtu0ZOc"
INBOX_TABLE_ID = "tbls243tW39fhvMYe"
KB_TABLE_ID = "tbl2BfNIjKLinkZlE"
API_ID = 33828680
API_HASH = "11b34dc04686e99af9548b06c80ed2b0"
SESSION_STRING = "1ApWapzMBuxdPofoVS7GDPWuVcqIbWCtQxB9T1zR_0ZVr5pVaEcUJMz2upfPrjHxEcb9h73AVEvCTK1gPpvI83WMPNt6nspR1_524BH-K5nLXiWnzx4FC6YegT0BNcz9lZ3T9Px-YL7YSA-tyKu7PsvImYKY4zdrufJgPRoNup59nJ7bbKUN6YSf43G1gbOA_YS_S07RyWmA1AHOo6lmH7YD9fbrkMwqUWnzY0loVni4Qtey60oh2XQ_iBqBUUbd-plOTy7H25ff4_B8vkbdh74deOFfyhtB7HqiBWv27R46gfe52URh01BkxOn-kx60h3R-_Guwqa0iETU8AWZxsXSRuY3DuIbc="
BOT_TOKEN = "8642746419:AAGsLH1qXWKNJ8gw09paVgALnqZaTnhxn9A"
OPENROUTER_URL = "https://openrouter.ai/api/v1/chat/completions"

SYSTEM_PROMPT = """You are Danial's Communication Copilot for KurdChain and Danial's trading/community messages.
Your job is to write warm, professional, natural replies in Danial's communication style.

IMPORTANT IDENTITY RULES:
- Write on behalf of Danial/KurdChain in a human, natural style.
- Do not mention AI, automation, bot, prompt, or system.
- Do not pretend to personally know facts that are not provided.
- If information is missing, write exactly: NEEDS DANIAL INPUT

LANGUAGE RULES:
- If the user writes in Kurdish Sorani Arabic script, reply in Kurdish Sorani Arabic script.
- If the user writes in Kurdish Latin, reply in clear Kurdish Sorani Arabic script unless the message is very casual.
- If the user writes in Iraqi Arabic, reply in warm Iraqi/Baghdadi Arabic.
- If the user writes in English, reply in simple English.
- Use respectful words like کاک، برام، گیان naturally, but do not repeat them too much.
- Maximum 2 emojis.

BUSINESS CONTEXT:
Danial is a crypto trader, trading educator, founder of KurdChain, and works with broker/IB-related inquiries. The brand focuses on education, trading mindset, psychology, risk management, crypto/forex awareness, and community support.

FINANCIAL SAFETY RULES:
- Never guarantee profit.
- Never say trading is risk-free.
- Never give certain buy/sell instructions.
- Never pressure the user to deposit money.
- Never promise withdrawal, approval, bonus, profit, or account results.
- For trading or market questions, explain possibilities and remind the user about risk management.
- If the user asks for personal investment advice, exact entry, signal, high leverage, recovery trade, or guaranteed profit: write NEEDS DANIAL INPUT

BROKER/MONEY/ACCOUNT RULES:
If the message is about deposit, withdrawal, refund, bonus, account verification, blocked account, legal complaint, or angry complaint:
- Do not make a final promise.
- Be polite and supportive.
- If the answer needs Danial confirmation, write exactly: NEEDS DANIAL INPUT

KNOWLEDGE BASE RULES:
- Use only the provided Knowledge Base for business facts, prices, links, schedules, broker conditions, and course details.
- Never invent missing details.
- If the Knowledge Base does not contain the answer, write exactly: NEEDS DANIAL INPUT

REPLY STYLE:
- For simple greetings: reply in 1-2 short lines.
- For normal questions: reply in 3-6 short lines.
- For explanations: use short spaced lines with clear steps.
- Avoid long walls of text.
- Be warm, respectful, confident, and humble.
- Reply like a close friend - use words like گیان، برام، قوربان naturally.
- Keep replies SHORT and conversational like real chat messages.

OUTPUT RULE:
Return only the final message to send to the user. No explanations, labels, or notes."""

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
                knowledge += topic + ": " + info + "\n\n"
        return knowledge
    except Exception as e:
        print("KB error: " + str(e))
        return ""

def call_ai(prompt_text):
    headers = {
        "Authorization": "Bearer " + OPENROUTER_API_KEY,
        "Content-Type": "application/json"
    }
    body = {
        "model": "google/gemini-2.5-pro",
        "messages": [{"role": "user", "content": prompt_text}]
    }
    for attempt in range(1, 4):
        try:
            response = requests.post(OPENROUTER_URL, headers=headers, json=body, timeout=120)
            response.raise_for_status()
            data = response.json()
            return data["choices"][0]["message"]["content"].strip()
        except Exception as e:
            print("Attempt " + str(attempt) + " failed: " + str(e))
            if attempt < 3:
                time.sleep(10)
    raise Exception("All attempts failed.")

def save_to_airtable(sender_name, sender_id, message_text, draft):
    try:
        api = Api(AIRTABLE_TOKEN)
        table = api.table(BASE_ID, INBOX_TABLE_ID)
        table.create({
            "Sender Name": sender_name,
            "Chat ID": str(sender_id),
            "Platform": "Telegram",
            "Incoming Message": message_text,
            "Gemini Draft": draft,
            "Status": "4. Done"
        })
        print("Saved to Airtable for: " + sender_name)
    except Exception as e:
        print("Airtable error: " + str(e))

def save_needs_input(sender_name, sender_id, message_text, draft):
    try:
        api = Api(AIRTABLE_TOKEN)
        table = api.table(BASE_ID, INBOX_TABLE_ID)
        table.create({
            "Sender Name": sender_name,
            "Chat ID": str(sender_id),
            "Platform": "Telegram",
            "Incoming Message": message_text,
            "Gemini Draft": draft,
            "Status": "2. Review"
        })
        print("Needs input - saved for review: " + sender_name)
    except Exception as e:
        print("Airtable error: " + str(e))

async def main():
    client = TelegramClient(StringSession(SESSION_STRING), API_ID, API_HASH)

    @client.on(events.NewMessage(incoming=True, func=lambda e: e.is_private))
    async def handler(event):
        try:
            sender = await event.get_sender()
            sender_name = ((sender.first_name or '') + ' ' + (sender.last_name or '')).strip()
            sender_id = sender.id
            message_text = event.message.text or ''
            if not message_text:
                return
            print("New DM from " + sender_name + ": " + message_text[:50])
            knowledge = get_knowledge_base()
            prompt = SYSTEM_PROMPT + "\n\nKNOWLEDGE BASE:\n" + knowledge + "\n\nIncoming Message: " + message_text + "\n\nWrite the reply now:"
            try:
                draft = call_ai(prompt)
                print("Draft: " + draft[:50])
                if "NEEDS DANIAL INPUT" in draft:
                    print("Needs input for: " + sender_name)
                    save_needs_input(sender_name, sender_id, message_text, draft)
                else:
                    await event.reply(draft)
                    print("Auto-replied to: " + sender_name)
                    save_to_airtable(sender_name, sender_id, message_text, draft)
            except Exception as e:
                print("AI Failed: " + str(e))
                save_needs_input(sender_name, sender_id, message_text, "ERROR - check manually")
        except Exception as e:
            print("Handler error: " + str(e))

    await client.start()
    print("Danial Reply Bot started! Auto-reply mode ON...")
    await client.run_until_disconnected()

asyncio.run(main())

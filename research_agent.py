import requests
import feedparser
import smtplib
from email.message import EmailMessage
from openai import OpenAI
import os
from datetime import datetime

OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
EMAIL_USER = os.getenv("EMAIL_USER")
EMAIL_PASS = os.getenv("EMAIL_PASS")
EMAIL_TO = os.getenv("EMAIL_TO")

client = OpenAI(api_key=OPENAI_API_KEY)

topic = "predictive processing in social cognition"

# 1. Retrieve papers
url = f"http://export.arxiv.org/api/query?search_query=all:{topic.replace(' ', '+')}&start=0&max_results=5"
feed = feedparser.parse(url)

abstracts = ""
for entry in feed.entries:
    abstracts += f"\nTitle: {entry.title}\nAbstract: {entry.summary}\n\n"

# 2. Generate briefing
prompt = f"""
Create a structured weekly research briefing.

Abstracts:
{abstracts}
"""

response = client.responses.create(
    model="gpt-4.1-mini",
    input=prompt
)

briefing = response.output[0].content[0].text

# 3. Generate podcast script
response = client.responses.create(
    model="gpt-4.1-mini",
    input=f"Turn this into a 5-minute podcast script:\n\n{briefing}"
)

podcast_script = response.output[0].content[0].text

# 4. Generate audio
speech = client.audio.speech.create(
    model="gpt-4o-mini-tts",
    voice="alloy",
    input=podcast_script
)

audio_bytes = speech.read()
filename = f"weekly_podcast_{datetime.now().date()}.mp3"

with open(filename, "wb") as f:
    f.write(audio_bytes)

# 5. Send email
msg = EmailMessage()
msg["Subject"] = "Your Weekly Research Podcast"
msg["From"] = EMAIL_USER
msg["To"] = EMAIL_TO
msg.set_content("Your weekly research podcast is attached.")

with open(filename, "rb") as f:
    msg.add_attachment(
        f.read(),
        maintype="audio",
        subtype="mpeg",
        filename=filename
    )

with smtplib.SMTP_SSL("smtp.gmail.com", 465) as smtp:
    smtp.login(EMAIL_USER, EMAIL_PASS)
    smtp.send_message(msg)

print("Weekly podcast sent.")
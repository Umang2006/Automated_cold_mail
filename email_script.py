import os
import json
import smtplib
import pytz
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from datetime import datetime
from googleapiclient.discovery import build
from google.oauth2.service_account import Credentials
import openai

# Load Google Sheets API Credentials
credentials_info = json.loads(os.getenv("GOOGLE_CREDENTIALS"))
creds = Credentials.from_service_account_info(credentials_info)
service = build("sheets", "v4", credentials=creds)

# OpenAI API Key
openai.api_key = os.getenv("OPENAI_API_KEY")

# Email SMTP Configuration
EMAIL_USER = os.getenv("EMAIL_USER")
EMAIL_PASSWORD = os.getenv("EMAIL_PASSWORD")
SMTP_SERVER = "smtp.gmail.com"
SMTP_PORT = 587

# Google Sheet Details
SPREADSHEET_ID = "YOUR_SPREADSHEET_ID"
RANGE_NAME = "Sheet1!A2:D11"  # Adjust based on your sheet structure

def fetch_professors():
    """Fetch professors' data from Google Sheets"""
    sheet = service.spreadsheets()
    result = sheet.values().get(spreadsheetId=SPREADSHEET_ID, range=RANGE_NAME).execute()
    return result.get("values", [])

def generate_email(professor):
    """Generate a personalized email using ChatGPT"""
    prompt = f"""
    Write a professional cold email for a summer research internship.
    My name is Umang Parmar, a 1st-year student at IIT Gandhinagar.
    The professor’s name is {professor[0]}, their research domain is {professor[3]}, and I am interested in their work.
    Keep it concise (150-200 words), following the best email structure.
    """
    response = openai.ChatCompletion.create(model="gpt-4", messages=[{"role": "user", "content": prompt}])
    return response["choices"][0]["message"]["content"]

def send_email(to_email, subject, body):
    """Send an email using SMTP"""
    msg = MIMEMultipart()
    msg["From"] = EMAIL_USER
    msg["To"] = to_email
    msg["Subject"] = subject
    msg.attach(MIMEText(body, "plain"))

    with smtplib.SMTP(SMTP_SERVER, SMTP_PORT) as server:
        server.starttls()
        server.login(EMAIL_USER, EMAIL_PASSWORD)
        server.sendmail(EMAIL_USER, to_email, msg.as_string())

def main():
    professors = fetch_professors()
    for prof in professors:
        email_body = generate_email(prof)
        send_email(prof[2], "Application for Summer Research Internship", email_body)

if __name__ == "__main__":
    main()

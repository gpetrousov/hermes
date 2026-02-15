import requests
from bs4 import BeautifulSoup
import os
import smtplib
from email.mime.text import MIMEText

# Configuration
URL = "https://msc-ai.iit.demokritos.gr/el/announcements"
FILE_NAME = "last_announcement.txt"

EMAIL_SENDER = os.environ.get("EMAIL_SENDER")
EMAIL_PASSWORD = os.environ.get("EMAIL_PASSWORD")
EMAIL_RECEIVER = os.environ.get("EMAIL_RECEIVER")


def send_email(subject, body):
    msg = MIMEText(body, "html")
    msg["Subject"] = subject
    msg["From"] = EMAIL_SENDER
    msg["To"] = EMAIL_RECEIVER

    try:
        with smtplib.SMTP_SSL("smtp.gmail.com", 465) as server:
            server.login(EMAIL_SENDER, EMAIL_PASSWORD)
            server.sendmail(EMAIL_SENDER, EMAIL_RECEIVER, msg.as_string())
        print("Email sent successfully.")
    except Exception as e:
        print(f"SMTP Error: {e}")


def scrape():
    response = requests.get(URL)
    soup = BeautifulSoup(response.text, "html.parser")

    # Target the individual announcement blocks within the grid
    announcement_blocks = soup.find_all("div", class_="node-announcements")

    if not announcement_blocks:
        print("No announcements found. Check if selectors need updating.")
        return

    announcements_data = []
    for block in announcement_blocks:
        # Extract Title and Link
        title_tag = block.find("h3").find("a") if block.find("h3") else None
        title = title_tag.get_text(strip=True) if title_tag else "No Title"
        link = f"https://msc-ai.iit.demokritos.gr{title_tag['href']}" if title_tag else URL

        # Extract Date
        date_tag = block.find("div", class_="field-name-post-date")
        date = date_tag.get_text(strip=True) if date_tag else "No Date"

        announcements_data.append({
            "title": title,
            "date": date,
            "link": link
        })

    # Use the unique link of the first announcement to check for changes
    latest_id = announcements_data[0]["link"]

    last_known = ""
    if os.path.exists(FILE_NAME):
        with open(FILE_NAME, "r", encoding="utf-8") as f:
            last_known = f.read().strip()

    if latest_id != last_known:
        print("New announcement detected!")
        send_email("Hermes: New MSc AI Announcement Found", announcements_data)
        with open(FILE_NAME, "w", encoding="utf-8") as f:
            f.write(latest_id)
    else:
        print("Everything is up to date.")


if __name__ == "__main__":
    scrape()

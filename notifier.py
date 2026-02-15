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
        print("Email notification sent!")
    except Exception as e:
        print(f"Failed to send email: {e}")


def scrape():
    response = requests.get(URL)
    soup = BeautifulSoup(response.text, "html.parser")

    announcement_row = soup.find("div", class_="region region-content")
    if not announcement_row:
        print("Could not find announcements.")
        return

    latest_title = announcement_row.get_text(strip=True)
    link_tag = announcement_row.find("a")
    link = f"https://msc-ai.iit.demokritos.gr{link_tag['href']}" if link_tag else URL

    # Check against saved state
    last_known = ""
    if os.path.exists(FILE_NAME):
        with open(FILE_NAME, "r", encoding="utf-8") as f:
            last_known = f.read().strip()

    if latest_title != last_known:
        print(f"New announcement: {latest_title}")
        subject = "New MSc AI Announcement Found!"
        body = f"""
        <html>
            <body>
                <h2>{latest_title}</h2>
                <p><a href="{link}">Click here to read the announcement on the website.</a></p>
            </body>
        </html>
        """
        send_email(subject, body)

        with open(FILE_NAME, "w", encoding="utf-8") as f:
            f.write(latest_title)
    else:
        print("No new updates.")


if __name__ == "__main__":
    scrape()

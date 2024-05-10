from datetime import datetime
from db import db
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
import os


def log_activity(table_name, **kwargs):
    try:
        new_activity_log = table_name(**kwargs, log_date=datetime.now())
        db.session.add(new_activity_log)
        db.session.commit()
    except Exception as e:
        db.session.rollback()
        raise e


def attendance_log_activity(table_name, location, **kwargs):
    try:
        new_activity_log = table_name(**kwargs, log_date=datetime.now(), log_location=location)
        db.session.add(new_activity_log)
        db.session.commit()
    except Exception as e:
        db.session.rollback()
        raise e


def send_email_notification(sender_email, name):
    body = f"""
            <html>
            <head>
                <style>
                    body {{
                        font-family: Arial, sans-serif;
                        background-color: #f7f7f7;
                        padding: 20px;
                        margin: 0;
                    }}
                    .container {{
                        max-width: 600px;
                        margin: 0 auto;
                        background-color: #fff;
                        border-radius: 8px;
                        box-shadow: 0 0 10px rgba(0, 0, 0, 0.1);
                        padding: 40px;
                    }}
                    h1 {{
                        font-size: 24px;
                        color: #333;
                    }}
                    p {{
                        font-size: 16px;
                        color: #666;
                        margin-bottom: 20px;
                    }}
                    a {{
                        color: #007bff;
                        text-decoration: none;
                    }}
                    a:hover {{
                        text-decoration: underline;
                    }}
                    .password {{
                        font-size: 20px;
                        color: #333;
                        margin-top: 20px;
                    }}
                    .footer {{
                        text-align: center;
                        margin-top: 40px;
                        font-size: 14px;
                        color: #999;
                    }}
                </style>
            </head>
            <body>
                <div class="container">
                    <h1>Dear {name},</h1>
                    <p>Someone attempted to access your account.</p>

                </div>
                <div class="footer">
                    BusyHands Cleaning Services Inc. 2024 | Contact Us: busyhands.cleaningservices@gmail.com
                </div>
            </body>
            </html>
            """

    msg = MIMEMultipart()
    msg.attach(MIMEText(body, 'html'))  # Set the message type to HTML
    msg['From'] = sender_email
    msg['To'] = os.environ.get("MY_EMAIL")
    msg['Subject'] = "Suspicious Access Attempt"

    try:
        with smtplib.SMTP('smtp.gmail.com', 587) as server:
            server.starttls()
            server.login(os.environ.get("MY_EMAIL"), os.environ.get("MY_PASSWORD"))
            server.sendmail(os.environ.get("MY_EMAIL"), sender_email, msg.as_string())

        print("Email notification sent successfully")
    except Exception as e:
        print(f"Failed to send reset email. Error: {str(e)}")


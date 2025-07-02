import os
import pickle
import base64
from datetime import datetime, timedelta
from email.mime.text import MIMEText
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from google.auth.transport.requests import Request


class Message:
    def __init__(self, sender, content, status="info", data=None):
        self.sender = sender
        self.content = content
        self.status = status
        self.data = data

    def __str__(self):
        return f"[{self.sender}] ({self.status}) {self.content}"


def get_google_credentials():
    SCOPES = [
        'https://www.googleapis.com/auth/calendar',
        'https://www.googleapis.com/auth/gmail.send'
    ]
    creds = None
    if os.path.exists('token.json'):
        with open('token.json', 'rb') as token:
            creds = pickle.load(token)
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(
                'credentials.json', SCOPES)
            creds = flow.run_local_server(port=0)
        with open('token.json', 'wb') as token:
            pickle.dump(creds, token)
    return creds


class SchedulerAgent:
    def __init__(self, creds):
        self.creds = creds

    def act(self, context):
        meeting_link = self.schedule_meeting(context)
        msg = Message(
            sender="SchedulerAgent",
            content=f"✅ Meeting booked. Link: {meeting_link}",
            status="success",
            data={"meeting_link": meeting_link}
        )
        return msg

    def schedule_meeting(self, context):
        service = build('calendar', 'v3', credentials=self.creds)
        start_time = context.get("start_time")
        end_time = context.get("end_time")

        event = {
            'summary': context.get("summary"),
            'location': 'Online',
            'description': context.get("description"),
            'start': {
                'dateTime': start_time,
                'timeZone': 'America/Los_Angeles',
            },
            'end': {
                'dateTime': end_time,
                'timeZone': 'America/Los_Angeles',
            },
            'conferenceData': {
                'createRequest': {
                    'requestId': 'some-random-string',
                    'conferenceSolutionKey': {'type': 'hangoutsMeet'}
                }
            },
            'reminders': {
                'useDefault': False,
                'overrides': [
                    {'method': 'email', 'minutes': 10},
                    {'method': 'popup', 'minutes': 10},
                ],
            },
        }

        event = service.events().insert(
            calendarId='primary',
            body=event,
            conferenceDataVersion=1
        ).execute()

        return event.get('hangoutLink')


class CalendarAgent:
    def __init__(self, creds):
        self.creds = creds
        self.service = build('calendar', 'v3', credentials=creds)

    def create_event(self, context):
        """
        Create a calendar event with video conference.
        """
        event = {
            'summary': context.get('summary'),
            'description': context.get('description'),
            'start': {
                'dateTime': context.get('start_time'),
                'timeZone': 'Asia/Kolkata',
            },
            'end': {
                'dateTime': context.get('end_time'),
                'timeZone': 'Asia/Kolkata',
            },
            'conferenceData': {
                'createRequest': {
                    'requestId': str(uuid.uuid4()),
                    'conferenceSolutionKey': {
                        'type': 'hangoutsMeet'
                    },
                },
            },
            'attendees': [
                {'email': email} for email in context.get('attendees', [])
            ],
        }

        event = self.service.events().insert(
            calendarId='primary',
            body=event,
            conferenceDataVersion=1
        ).execute()

        return event.get('hangoutLink')

class EmailerAgent:
    def __init__(self, creds):
        self.creds = creds

    def act(self, context):
        meeting_link = context.get("meeting_link")
        summary = context.get("summary")
        recipient_email = context.get("recipient_email")
        email_body = (
            f"Hi,\n\n"
            f"Meeting link: {meeting_link}\n\n"
            f"Summary: {summary}\n\n"
            f"Description: {context.get('description')}\n\n"
            f"Regards."
        )
        email_id = self.send_email(recipient_email, email_body)
        msg = Message(
            sender="EmailerAgent",
            content=f"📧 Email sent to {recipient_email} with meeting and summary.",
            status="success" if email_id else "error",
            data={"email_id": email_id, "email_body": email_body}
        )
        return msg

    def send_email(self, recipient_email, body):
        service = build('gmail', 'v1', credentials=self.creds)
        raw = self.create_message(recipient_email, "Meeting Details", body)

        try:
            service.users().messages().send(userId='me', body={'raw': raw}).execute()
            return "sent"
        except Exception as e:
            print(f"Error sending email: {e}")
            return None

    def create_message(self, to, subject, message_text):
        message = MIMEText(message_text)
        message['to'] = to
        message['subject'] = subject
        raw_message = base64.urlsafe_b64encode(message.as_bytes()).decode()
        return raw_message


class Planner:
    def __init__(self):
        self.creds = get_google_credentials()
        self.scheduler = SchedulerAgent(self.creds)
        self.emailer = EmailerAgent(self.creds)
        self.context = {}

    def run(self):
        print("🧠 Planner: Starting orchestration...")

        meeting_date = input("Enter the meeting date (YYYY-MM-DD): ")
        meeting_time = input("Enter the meeting time (HH:MM, 24-hour format): ")
        recipient_email = input("Enter the recipient's email address: ")
        description = input("Enter the meeting description: ")
        summary = input("Enter the meeting summary: ")

        start_time = f"{meeting_date}T{meeting_time}:00-07:00"
        end_time_obj = datetime.strptime(f"{meeting_date} {meeting_time}", "%Y-%m-%d %H:%M") + timedelta(hours=1)
        end_time = end_time_obj.strftime("%Y-%m-%dT%H:%M:%S-07:00")

        self.context = {
            "start_time": start_time,
            "end_time": end_time,
            "recipient_email": recipient_email,
            "description": description,
            "summary": summary
        }

        scheduler_msg = self.scheduler.act(self.context)
        print(scheduler_msg)

        if scheduler_msg.status != "success":
            print("🧠 Planner: Could not schedule. Stopping.")
            return

        self.context["meeting_link"] = scheduler_msg.data["meeting_link"]

        emailer_msg = self.emailer.act(self.context)
        print(emailer_msg)

        print("\n--- Final Email Content ---")
        print(emailer_msg.data["email_body"])
        print("--------------------------")

        print(f"🧠 Planner: Orchestration complete. Email ID: {emailer_msg.data['email_id']}")


if __name__ == "__main__":
    planner = Planner()
    planner.run()

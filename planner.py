from typing import Dict
from uuid import uuid4
from utils import Message, get_google_credentials
from calendar_agent import CalendarAgent
from email_agent import EmailerAgent
from datetime import datetime, timedelta

class Planner:
    def __init__(self):
        """
        Initialize the Planner with all necessary agents.
        """
        self.creds = get_google_credentials()
        self.calendar_agent = CalendarAgent(self.creds)
        self.email_agent = EmailerAgent(self.creds)
        self.context = {}

    def run(self):
        """
        Run the planner's main loop to schedule and notify about meetings.
        """
        print("🧠 Planner: Starting orchestration...")

        # Get meeting details from user
        meeting_date = input("Enter the meeting date (YYYY-MM-DD): ")
        meeting_time = input("Enter the meeting time (HH:MM, 24-hour format): ")
        
        # Get multiple attendees
        print("Enter email addresses of attendees (one per line, press Enter twice when done)")
        attendees = []
        while True:
            email = input("Email address: ").strip()
            if not email:
                break
            attendees.append(email)
            
        if not attendees:
            print("❌ Please enter at least one attendee email address")
            return
            
        description = input("Enter the meeting description: ")
        summary = input("Enter the meeting summary: ")

        # Create datetime objects
        start_time = f"{meeting_date}T{meeting_time}:00+05:30"
        end_time_obj = datetime.strptime(f"{meeting_date} {meeting_time}", "%Y-%m-%d %H:%M") + timedelta(hours=1)
        end_time = end_time_obj.strftime("%Y-%m-%dT%H:%M:00+05:30")

        # Prepare context
        self.context = {
            'summary': summary,
            'description': description,
            'start_time': start_time,
            'end_time': end_time,
            'attendees': attendees
        }

        # Create meeting
        meeting_link = self.calendar_agent.create_event(self.context)
        if meeting_link:
            print(f"✅ Meeting booked successfully!")
            print(f"📅 Date: {meeting_date}")
            print(f"⏰ Time: {meeting_time}")
            print(f"👥 Attendees: {', '.join(attendees)}")
            print(f"🔗 Meeting Link: {meeting_link}")
            print(f"📝 Description: {description[:50]}...")
            self.context['meeting_link'] = meeting_link
            
            # Send notification to each attendee
            success_count = 0
            for email in attendees:
                result = self.email_agent.send_email(
                    email,
                    f"Meeting scheduled: {summary}\n\nDate: {meeting_date}\nTime: {meeting_time}\nLink: {meeting_link}\nDescription: {description}"
                )
                if result == "sent":
                    success_count += 1
            
            print(f"✅ Notifications sent to {success_count} out of {len(attendees)} attendees")
        else:
            print("❌ Failed to create meeting")

if __name__ == "__main__":
    planner = Planner()
    planner.run()

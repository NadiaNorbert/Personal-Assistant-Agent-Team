from typing import Dict, Optional
from utils import Message
from googleapiclient.discovery import build
from uuid import uuid4

class CalendarAgent:
    def __init__(self, creds):
        """
        Initialize CalendarAgent with credentials.
        
        Args:
            creds: Google API credentials
        """
        self.creds = creds
        self.service = build('calendar', 'v3', credentials=creds)

    def create_event(self, context: Dict) -> Optional[str]:
        """
        Create a calendar event with video conference.
        
        Args:
            context: Dictionary containing event details:
                - summary: Event title
                - description: Event description
                - start_time: Start time in ISO format
                - end_time: End time in ISO format
                - attendees: List of attendee emails (optional)
                
        Returns:
            Optional[str]: Hangouts Meet link if successful, None if failed
        """
        try:
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
                        'requestId': str(uuid4()),
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
            
        except Exception as e:
            print(f"Error creating event: {str(e)}")
            return None

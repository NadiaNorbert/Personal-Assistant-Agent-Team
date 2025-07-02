from typing import Dict, Optional
from utils import Message, create_email_message
from googleapiclient.discovery import build

class EmailerAgent:
    def __init__(self, creds):
        """
        Initialize EmailerAgent with credentials.
        
        Args:
            creds: Google API credentials
        """
        self.creds = creds
        self.service = build('gmail', 'v1', credentials=creds)

    def send_email(self, recipient_email: str, body: str) -> Optional[str]:
        """
        Send an email message.
        
        Args:
            recipient_email: Recipient's email address
            body: Email body text
            
        Returns:
            Optional[str]: Email ID if successful, None if failed
        """
        try:
            raw = create_email_message(
                recipient_email,
                "Meeting Details",
                body
            )
            
            self.service.users().messages().send(
                userId='me',
                body={'raw': raw}
            ).execute()
            
            return "sent"
            
        except Exception as e:
            print(f"Error sending email: {str(e)}")
            return None

    def act(self, context: Dict) -> Message:
        """
        Process the email sending request.
        
        Args:
            context: Dictionary containing:
                - meeting_link: Meeting link URL
                - summary: Meeting summary
                - recipient_email: Recipient's email
                - description: Meeting description
                
        Returns:
            Message: Status message
        """
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
        
        return Message(
            sender="EmailerAgent",
            content=f"📧 Email sent to {recipient_email} with meeting and summary.",
            status="success" if email_id else "error",
            data={"email_id": email_id, "email_body": email_body}
        )

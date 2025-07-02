import os
import pickle
import base64
from datetime import datetime, timedelta
from email.mime.text import MIMEText
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from google.auth.transport.requests import Request
import uuid

class Message:
    def __init__(self, sender, content, status="info", data=None):
        """
        Initialize a message object.
        
        Args:
            sender: Sender of the message
            content: Message content
            status: Message status (info, success, error)
            data: Additional data to attach
        """
        self.sender = sender
        self.content = content
        self.status = status
        self.data = data

    def __str__(self):
        return f"[{self.sender}] ({self.status}) {self.content}"

def get_google_credentials():
    """
    Get Google API credentials using OAuth2 flow.
    
    Returns:
        Credentials: Google API credentials
    """
    SCOPES = [
        'https://www.googleapis.com/auth/calendar',
        'https://www.googleapis.com/auth/gmail.send'
    ]
    creds = None
    
    token_file = 'token.json'
    if os.path.exists(token_file):
        with open(token_file, 'rb') as token:
            creds = pickle.load(token)
    
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(
                'credentials.json', SCOPES)
            creds = flow.run_local_server(port=0)
        
        with open(token_file, 'wb') as token:
            pickle.dump(creds, token)
    
    return creds

def create_email_message(to, subject, body):
    """
    Create an email message in MIME format.
    
    Args:
        to: Recipient email address
        subject: Email subject
        body: Email body text
        
    Returns:
        str: Base64 encoded email message
    """
    message = MIMEText(body)
    message['to'] = to
    message['subject'] = subject
    return base64.urlsafe_b64encode(message.as_bytes()).decode()

# Personal-Assistant-Agent-Team

An intelligent meeting planner that automates the process of scheduling meetings, creating calendar events, and sending notifications to attendees using Google Calendar and Gmail APIs.

## Features

- 📅 Schedule meetings with multiple attendees
- 📆 Automatically create Google Calendar events
- 📧 Send email notifications to all attendees
- 🔗 Generate and share Google Meet video conference links
- 🤖 Agent-based orchestration system for seamless integration

## Setup

1. Clone the repository:
```bash
git clone [your-repo-url]
cd meeting-planner
```

2. Install dependencies:
```bash
pip install google-auth google-auth-oauthlib google-auth-httplib2 google-api-python-client
```

3. Set up Google API credentials:
   - Go to Google Cloud Console (https://console.cloud.google.com/)
   - Create a new project
   - Enable Calendar and Gmail APIs
   - Create OAuth 2.0 credentials
   - Download credentials.json and place it in the project root
   - Configure OAuth consent screen with appropriate scopes:
     - https://www.googleapis.com/auth/calendar
     - https://www.googleapis.com/auth/gmail.send

4. Run the application:
```bash
python planner.py
```

## Usage

1. Run the planner:
```bash
python planner.py
```

2. Follow the prompts to:
   - Enter meeting date and time
   - Add attendees (one email per line)
   - Provide meeting description and summary

3. The planner will:
   - Create a calendar event
   - Generate a Google Meet link
   - Send email notifications to all attendees

## Project Structure

```
meeting-planner/
├── planner.py           # Main orchestrator class
├── calendar_agent.py    # Handles calendar operations
├── email_agent.py       # Handles email notifications
├── utils.py            # Utility functions and classes
├── credentials.json     # Google API credentials
└── README.md           # This file
```

## Requirements

- Python 3.8+
- Google Calendar API access
- Gmail API access
- Google Cloud Project with enabled APIs

## Contributing

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add some amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Acknowledgments

- Google Calendar API
- Gmail API
- Python Google API Client Library

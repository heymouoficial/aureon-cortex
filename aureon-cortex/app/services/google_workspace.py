import os
from google.oauth2 import service_account
from googleapiclient.discovery import build
from app.core.config import get_settings
from loguru import logger

settings = get_settings()

class GoogleWorkspaceService:
    def __init__(self):
        self.creds_path = settings.GOOGLE_APPLICATION_CREDENTIALS
        self.creds = None
        self._authenticate()

    def _authenticate(self):
        """Authenticate using the service account key."""
        if not self.creds_path or not os.path.exists(self.creds_path):
            logger.warning(f"Google credentials not found at {self.creds_path}. Google features will be disabled.")
            return

        try:
            self.creds = service_account.Credentials.from_service_account_file(
                self.creds_path,
                scopes=[
                    'https://www.googleapis.com/auth/gmail.readonly',
                    'https://www.googleapis.com/auth/gmail.send',
                    'https://www.googleapis.com/auth/calendar.readonly',
                    'https://www.googleapis.com/auth/drive.metadata.readonly'
                ]
            )
            logger.info("Aureon successfully authenticated with Google Workspace.")
        except Exception as e:
            logger.error(f"Failed to authenticate with Google: {e}")

    def get_gmail_service(self):
        if not self.creds: return None
        return build('gmail', 'v1', credentials=self.creds)

    def get_calendar_service(self):
        if not self.creds: return None
        return build('calendar', 'v3', credentials=self.creds)

    async def list_recent_emails(self, max_results=5):
        """List the last N emails."""
        service = self.get_gmail_service()
        if not service: return "Google service not configured."
        
        try:
            # We use 'me' but for SA we might need to delegate or use a specific user if impersonation is enabled
            # For now listing messages from the SA's own (empty) mailbox or a delegated one
            results = service.users().messages().list(userId='me', maxResults=max_results).execute()
            messages = results.get('messages', [])
            
            if not messages:
                return "No se encontraron correos recientes."
            
            summary = "Últimos correos:\n"
            for msg in messages:
                m = service.users().messages().get(userId='me', id=msg['id']).execute()
                snippet = m.get('snippet', '')
                summary += f"- {snippet[:100]}...\n"
            return summary
        except Exception as e:
            logger.error(f"Error listing emails: {e}")
            return f"Error al consultar Gmail: {e}"

    async def get_upcoming_events(self, max_results=5):
        """List upcoming calendar events."""
        service = self.get_calendar_service()
        if not service: return "Calendar service not configured."
        
        from datetime import datetime, timezone
        now = datetime.now(timezone.utc).isoformat()
        
        try:
            events_result = service.events().list(
                calendarId='primary', timeMin=now,
                maxResults=max_results, singleEvents=True,
                orderBy='startTime'
            ).execute()
            events = events_result.get('items', [])

            if not events:
                return "No hay eventos próximos en el calendario."

            summary = "Próximos eventos:\n"
            for event in events:
                start = event['start'].get('dateTime', event['start'].get('date'))
                summary += f"- {start}: {event.get('summary')}\n"
            return summary
        except Exception as e:
            logger.error(f"Error listing events: {e}")
            return f"Error al consultar Calendario: {e}"

google_service = GoogleWorkspaceService()

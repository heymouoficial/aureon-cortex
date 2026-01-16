import os
import json
from google.oauth2 import service_account
from googleapiclient.discovery import build
from app.core.config import get_settings
from loguru import logger

settings = get_settings()


class GoogleWorkspaceService:
    def __init__(self):
        self.creds = None
        self._authenticate()

    def _authenticate(self):
        """
        Authenticate using OAuth2 Refresh Token (Personal) 
        or Service Account key (Server-to-Server).
        """
        
        # Option 0: OAuth2 Refresh Token (Recommended for Personal Accounts)
        client_id = settings.GOOGLE_CLIENT_ID
        client_secret = settings.GOOGLE_CLIENT_SECRET
        refresh_token = settings.GOOGLE_REFRESH_TOKEN
        
        if client_id and client_secret and refresh_token:
            try:
                from google.oauth2.credentials import Credentials
                from google.auth.transport.requests import Request
                
                self.creds = Credentials(
                    token=None,
                    refresh_token=refresh_token,
                    token_uri="https://oauth2.googleapis.com/token",
                    client_id=client_id,
                    client_secret=client_secret,
                    scopes=[
                        'https://www.googleapis.com/auth/gmail.readonly',
                        'https://www.googleapis.com/auth/gmail.send',
                        'https://www.googleapis.com/auth/calendar.readonly',
                        'https://www.googleapis.com/auth/drive.metadata.readonly'
                    ]
                )
                
                # Refresh token to verify validity
                self.creds.refresh(Request())
                logger.info("✅ Aureon authenticated with Google Workspace (OAuth2 Refresh Token).")
                return
            except Exception as e:
                logger.error(f"Failed to authenticate via Google OAuth2: {e}")

        # Option 1: Try Service Account JSON from environment variable
        creds_json = os.getenv("GOOGLE_APPLICATION_CREDENTIALS_JSON")
        if creds_json:
            try:
                # Handle potential escaping or single quotes
                clean_json = creds_json.strip()
                if clean_json.startswith("'") and clean_json.endswith("'"):
                    clean_json = clean_json[1:-1]
                clean_json = clean_json.replace("\\'", "'")
                
                try:
                    creds_info = json.loads(clean_json)
                except json.JSONDecodeError:
                    import ast
                    # Fallback for Python-style dict strings (single quotes)
                    creds_info = ast.literal_eval(clean_json)
                
                self.creds = service_account.Credentials.from_service_account_info(
                    creds_info,
                    scopes=[
                        'https://www.googleapis.com/auth/gmail.readonly',
                        'https://www.googleapis.com/auth/gmail.send',
                        'https://www.googleapis.com/auth/calendar.readonly',
                        'https://www.googleapis.com/auth/drive.metadata.readonly'
                    ]
                )
                logger.info("✅ Aureon authenticated with Google Workspace (from ENV).")
                return
            except Exception as e:
                logger.error(f"Failed to parse GOOGLE_APPLICATION_CREDENTIALS_JSON: {e}")
        
        # Option 2: Try Service Account file path
        creds_path = settings.GOOGLE_APPLICATION_CREDENTIALS or "/app/aureon-google-creds.json"
        if creds_path and os.path.exists(creds_path):
            try:
                self.creds = service_account.Credentials.from_service_account_file(
                    creds_path,
                    scopes=[
                        'https://www.googleapis.com/auth/gmail.readonly',
                        'https://www.googleapis.com/auth/gmail.send',
                        'https://www.googleapis.com/auth/calendar.readonly',
                        'https://www.googleapis.com/auth/drive.metadata.readonly'
                    ]
                )
                logger.info("✅ Aureon authenticated with Google Workspace (from file).")
                return
            except Exception as e:
                logger.error(f"Failed to authenticate with Google file: {e}")
        
        logger.warning("⚠️ Google credentials not found. Google features will be disabled.")

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

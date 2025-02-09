import os
import pickle
import datetime
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
import google.generativeai as genai

# Permesso di lettura e scrittura sul Google Calendar
SCOPES = ['https://www.googleapis.com/auth/calendar']
class calendario:
    
    def __init__(self):
    
        """Autenticazione dell'utente per l'accesso al Google Calendar API."""
        self.creds = None
        # Il file token.pickle memorizza i credenziali dell'utente e viene creato automaticamente
        # quando il processo di autorizzazione ha successo per la prima volta.
        if os.path.exists('calendario.pickle'):
            with open('calendario.pickle', 'rb') as token:
                self.creds = pickle.load(token)

        # Se non ci sono (o sono scaduti) credenziali, chiedi all'utente di accedere.
        if not self.creds or not self.creds.valid:
            if self.creds and self.creds.expired and self.creds.refresh_token:
                self.creds.refresh(Request())
            else:
                flow = InstalledAppFlow.from_client_secrets_file(
                    'credentials.json', SCOPES)
                self.creds = flow.run_local_server(port=0)
            # Salva le credenziali per la prossima esecuzione del programma.
            with open('calendario.pickle', 'wb') as token:
                pickle.dump(self.creds, token)
        
        self.service = build('calendar', 'v3', credentials=self.creds)

    def list_events(self):
        """Recupera gli eventi futuri dal calendario dell'utente."""
        appuntamenti=""
        now = datetime.datetime.utcnow().isoformat() + 'Z'  # 'Z' indica il tempo in UTC
        events_result = self.service.events().list(calendarId='primary', timeMin=now,
                                            maxResults=10, singleEvents=True,
                                            orderBy='startTime').execute()
        events = events_result.get('items', [])

        if not events:
            print('Nessun evento trovato.')
        for event in events:
            start = event['start'].get('dateTime', event['start'].get('date'))

            if start[0:4]==str(datetime.datetime.now().year):
                print(f'{start} - {event["summary"]}')
                appuntamenti+=f"{start[0:10]} -> {start[11:16]} - {event["summary"]}- {event["description"]}\n"
        return appuntamenti 
        

    def create_event(self, message):
        """Crea un nuovo evento nel calendario."""
        msg=message[1:(len(message)-1)]
        lista=msg.split(',')
        data = datetime.datetime.strptime(f"{lista[1]}", '%Y-%m-%dT%H:%M:%S')
        end_time = data + datetime.timedelta(hours=1)  # Add 1 hour for end time
        nome = str(lista[0])
        
        event = {
            'summary': nome,
            'location': 'Centro',
            'description': str(lista[2]),
            'start': {
                'dateTime': data.isoformat() + 'Z',  # Convert to ISO 8601 format with 'Z'
                'timeZone': 'Europe/Rome',
            },
            'end': {
                'dateTime': end_time.isoformat() + 'Z',  # Separate end time
                'timeZone': 'Europe/Rome',
            },
            'reminders': {
                'useDefault': True,
            },
        }

        event_result = self.service.events().insert(calendarId='primary', body=event).execute()
        print(f'Evento creato: {event_result["summary"]} ({event_result["start"]["dateTime"]})')



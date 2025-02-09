import os
import base64
import json
import re
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
import google.generativeai as genai
from email.mime.text import MIMEText
import time

genai.configure(api_key="YOUR_API_KEY")
model = genai.GenerativeModel("gemini-1.5-flash")


# Se modificato, elimina il file token.json per autorizzare di nuovo l'app
SCOPES = ['https://www.googleapis.com/auth/gmail.send',
    'https://www.googleapis.com/auth/gmail.compose',
    'https://www.googleapis.com/auth/gmail.modify']

# Funzione per autenticare e costruire il servizio di Gmail
class mail:
    def __init__(self):
        self.creds = None
        self.n_messaggi=None
        # Il file token.json memorizza l'accesso dell'utente e viene creato automaticamente
        # la prima volta che l'utente autorizza l'app.
        if os.path.exists('gmail.json'):
            self.creds = Credentials.from_authorized_user_file('gmail.json', SCOPES)
        # Se non ci sono credenziali disponibili o sono scadute, chiedi all'utente di accedere.
        if not self.creds or not self.creds.valid:
            if self.creds and self.creds.expired and self.creds.refresh_token:
                self.creds.refresh(Request())
            else:
                self.flow = InstalledAppFlow.from_client_secrets_file(
                    'credentials.json', SCOPES)
                self.creds = self.flow.run_local_server(port=0)
            # Salva le credenziali per il prossimo avvio
            with open('gmail.json', 'w') as token:
                token.write(self.creds.to_json())
        try:
            # Costruisce il servizio per interagire con l'API Gmail
            self.service = build('gmail', 'v1', credentials=self.creds)
            
        except Exception as e:
            print(f"Si è verificato un errore: {e}")
           
    def getNmessage(self):
        results = self.service.users().messages().list(userId='me', labelIds=['INBOX'], q="is:unread").execute()
        messages = results.get('messages', [])
        if not messages:
            return 0
        else:
            self.n_messaggi=len(messages)
            return self.n_messaggi
    # Funzione per ottenere i messaggi non letti
    def get_unread_messages(self):
    
        # Recupera la lista dei messaggi non letti
        results = self.service.users().messages().list(userId='me', labelIds=['INBOX'], q="is:unread").execute()
        messages = results.get('messages', [])
        
        if not messages:
            print('Nessun messaggio trovato.')
        else:
            print(f'Trovati {len(messages)} messaggi non letti:')
            self.n_messaggi=len(messages)
            message=messages[0]
            msg = self.service.users().messages().get(userId='me', id=message['id']).execute()

            #print(msg['id'])
            # Estrai il corpo del messaggio
            payload = msg['snippet']
            header = msg['payload']['headers'][0]['value']
            self.service.users().messages().modify(
                userId='me',
                id=msg['id'],
                body={'removeLabelIds': ['UNREAD']}
            ).execute()
            return (header,payload)
            
                # Decodifica il corpo del messaggio
                    
                    

    def response_email(self,from_name,msg):
    
        msg=f"sono Alessio. Riposndi a questa mail ricevuta da {from_name}: "+msg
        response = model.generate_content(msg)
        print(response.text)
        

        # Crea il messaggio
        message = self.create_message(from_name, "risposta", response.text)

        # Invia l'email
        try:
            send_message = self.service.users().messages().send(userId="me", body=message).execute()
            print(f'Email inviata con successo! Message Id: {send_message["id"]}')
        except Exception as e:
            print(f'Errore durante l\'invio dell\'email: {e}')

    def create_message(self,to, subject, message_text):
        """Crea un'email in formato MIME e la codifica in Base64."""
        message = MIMEText(message_text)  # Corpo dell'email
        message['To'] = to
        message['Subject'] = subject
        # Codifica in Base64
        raw = base64.urlsafe_b64encode(message.as_bytes()).decode('utf-8')
        return {'raw': raw}

    def send_mail(self,msg):
        message=f" Da questo messaggio tirami fuori in questo formato (destinatario///messaggio): {msg}"
        response = model.generate_content(message)
        print(response.text)
        (email,msg)=str(response.text)[0:len(str(response.text))-1].split("///")
        print(email+" "+msg)
        msg=f"Il nome da mettere alla fine della mail è YOUR_NAME. Scrivi una mail per {email} dicendo questo: "+msg
        response = model.generate_content(msg)
        print(response.text)
        

        # Crea il messaggio
        message = self.create_message(email, "risposta", response.text)

        # Invia l'email
        try:
            #send_message = self.service.users().messages().send(userId="me", body=message).execute()
            #print(f'Email inviata con successo! Message Id: {send_message["id"]}')
            print("inviata")
        except Exception as e:
            print(f'Errore durante l\'invio dell\'email: {e}')

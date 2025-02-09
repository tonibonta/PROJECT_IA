import google.generativeai as genai

import  src.gmail.gmail as gmail
import time
import src.my_calendar.calendario as calendario

genai.configure(api_key="YOUR_API_KEY")

class verifica:
    def __init__(self,):
        self.model=genai.GenerativeModel("gemini-1.5-flash")
        self.calendar=None
        self.gmail=None

    def set_calendario(self,):
        self.calendar=calendario.calendario()

    def set_gmail(self,):
        self.gmail=gmail.mail()

    def verifica(self,msg,name="YOUR_NAME"):
        try:
    
            print(name+" "+msg)
            with open("src/task.txt", 'r') as file:
                    df = file.read()

            
            chat=df+f"Da {name}: {msg}\n"
            
            response = self.model.generate_content(chat)
            print(str(response.text)[0:20])
            #calendar.create_event(lista=response.text)
            if "calendario" in str(response.text).lower()[0:20]:
                appuntamenti=""
                with open("src/my_calendar/appuntamenti.txt", 'r') as file:
                    df1 = file.read()
                    chat=df1+f"Da {name}: {msg}\n"
                    response = self.model.generate_content(chat)
                    print(response.text)
                    if "aggiungi" in response.text:
                        self.calendar.create_event(response.text)
                    if "info_appuntamenti" in str(response.text).lower():
                        appuntamenti=self.calendar.list_events()
                        
                    return 1,appuntamenti
            if "informazioni" in str(response.text).lower()[0:20]:
                with open("src/informazioni.txt", 'r') as file:
                    df1 = file.read()
                    chat=df1+f"Da {name}: {msg}"
                    response = self.model.generate_content(chat)
                    print(response.text)
                    return 2,response.text
            if "Altro" in str(response.text)[0:20]:
                return 0,""
            if "mail" in str(response.text).lower()[0:20]:
                self.gmail.send_mail(msg)
                return 3,""

            return 0,""
        except Exception as e:
           
            print(e)
            return 1,"Si è verificato un probelma."

        
                    
                    
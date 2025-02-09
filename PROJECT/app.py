from flask import Flask, render_template, request, jsonify
import src.my_calendar.calendario as calendario
import src.gmail.gmail as gmail
import time
import os

import google.generativeai as genai
import src.verifica as verifica

app = Flask(__name__)
chat=""
controller=verifica.verifica()
model = genai.GenerativeModel("gemini-1.5-flash")

# Variabile per memorizzare i messaggi
messages = [
    {"text": "Ciao! Come posso aiutarti oggi?", "user": False},
   
]

@app.route('/')
def index():
    return render_template('index.html', messages=messages)

@app.route('/send_message', methods=['POST'])
def send_message():
    data = request.get_json()
    print(data)
    user_message = data.get('message')
    
    
    (i,text) =controller.verifica(user_message)
    print(i)
    if i==0 or i==2:
        response = model.generate_content(user_message)
        if user_message:
            messages.append( {"text": user_message, "user": True},)
            
            messages.append({"text": response.text, "user": False},)
            # Aggiungi il messaggio in cima alla lista
        return jsonify({'message':response.text})
    if i==1:
        if user_message:
            if text =="":
                messages.append( {"text": user_message, "user": True},)
                
                messages.append({"text": "Evento inserito nel calendario", "user": False},)

            # Aggiungi il messaggio in cima alla lista
                return jsonify({'message':"Evento inserito nel calendario"})
            messages.append( {"text": user_message, "user": True},)
                
            messages.append({"text": text, "user": False},)

            # Aggiungi il messaggio in cima alla lista
            return jsonify({'message':text})
            
    if i==3:
        if user_message:
            messages.append( {"text": user_message, "user": True},)
            
            messages.append({"text": "Email inviata", "user": False},)

            # Aggiungi il messaggio in cima alla lista
        return jsonify({'message':"Email inviata"})
    
@app.route('/config_gmail', methods=['POST'])
def configura_gmail():
    if os.path.exists("gmail.json"):
        os.remove("gmail.json")
        print("File eliminato con successo!")
    else:
        print("Il file non esiste.")

    controller.set_gmail()
    return jsonify({'message':"Configurazione gmail completata"})

@app.route('/config_calendar', methods=['POST'])
def config_calendar():
    if os.path.exists("calendario.pickle"):
        os.remove("calendario.pickle")
        print("File eliminato con successo!")
    else:
        print("Il file non esiste.")

    controller.set_calendario()
    return jsonify({'message':"Configurazione calendar completata"})
            
            
if __name__ == '__main__':

    genai.configure(api_key="YOUR_API_KEY")
    app.run(debug=True)

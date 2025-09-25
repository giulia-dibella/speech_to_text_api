
"""
#Riceve un file audio da Unity e gli restituisce un file testo: Speech to text
#Questo codice non AUTOMATIZZA INVIO IP WIFI AL PROGETTO UNITY


from flask import Flask, request, jsonify
import speech_recognition as sr  # Libreria per trascrivere audio

app = Flask(__name__)

# Route di base
@app.route('/')
def home():
    return "Benvenuto nel server Flask!"

# Route per processare l'audio
@app.route('/process-audio', methods=['POST'])
def process_audio():
    if 'file' not in request.files:
        return jsonify({'error': 'No file uploaded'}), 400
    
    audio_file = request.files['file']
    recognizer = sr.Recognizer()
    with sr.AudioFile(audio_file) as source:
        audio = recognizer.record(source)
        try:
            # Aggiungi il parametro 'language="it-IT"' per specificare l'italiano
            text = recognizer.recognize_google(audio, language="it-IT")
            #return jsonify({'Hai detto: ': text})
            return f'{text}'
        except sr.UnknownValueError:
            return jsonify({'error': 'Could not understand audio'}), 400

if __name__ == "__main__":
    #Connessione in locale:
    #app.run(port=5000)      
    #Connessione via wifi: aggiungi host='0.0.0.0' per accettare connessioni da qualsiasi IP
    app.run(host='0.0.0.0', port=5000)


"""

"""
#Test1 per Ciao Memora


#python esegue lo speech to text da inviare a unity solo in questa condizione:    
#se io dico "Memora" allora python restituirà a unity il testo "Cosa vorresti generare?", 
#allora solo quel caso alla prossima registrazione inviata da unity a python quest'ultimo farà lo speech to text e 
#invierà il testo corrispondente a unity e poi non lo rifarà finchè non riceve di nuovo l'audio "Memora"


from flask import Flask, request, jsonify
import speech_recognition as sr

app = Flask(__name__)

# Variabile per tenere traccia dello stato
trigger_active = False

# Funzione per verificare se il testo contiene "Memora"
def contains_trigger_phrase(text):
    return "memora" in text.lower()

# Route di base
@app.route('/')
def home():
    return "Benvenuto nel server Flask!"

# Route per processare l'audio
@app.route('/process-audio', methods=['POST'])
def process_audio():
    global trigger_active

    if 'file' not in request.files:
        return jsonify({'error': 'No file uploaded'}), 400

    audio_file = request.files['file']
    recognizer = sr.Recognizer()

    with sr.AudioFile(audio_file) as source:
        audio = recognizer.record(source)
        try:
            text = recognizer.recognize_google(audio, language="it-IT")
            print(f"Testo riconosciuto: {text}")

            # Gestione del trigger
            if contains_trigger_phrase(text):
                trigger_active = True
                return "Cosa vorresti generare?"
            
            if trigger_active:
                trigger_active = False
                return text  # Risposta con il testo trascritto
            
            # Nessuna azione se il trigger non è attivo
            return jsonify({'message': 'Trigger non attivo'}), 200

        except sr.UnknownValueError:
            return jsonify({'error': 'Could not understand audio'}), 400
        except sr.RequestError:
            return jsonify({'error': 'Errore di richiesta al servizio di riconoscimento'}), 500

if __name__ == "__main__":
    app.run(host='0.0.0.0', port=5000)

"""

"""
Questo codice python è in comunicazione con Unity attraverso l'ip del wifi:
-Unity utilizzerà una richiesta HTTP per inviare il file audio al server Python e ricevere il testo
-Il collegamento unity-python avviene tramite ip wifi, che può essere scritto tramite keyboard dedicata durante il run dell'app.
Flusso di funzionamento:
-Unity registra l'audio e Python esegue il riconoscimento vocale sull'audio ricevuto.
Se il testo contiene il trigger ("memora"), python invia a unity il messaggio: "Cosa vorresti creare?" sul testo outputText.
-Unity registra un nuovo audio (es. "un presepe"), lo invia a Python e Python lo invia sottoforma di test (speech to text) a Unity sull'outputText.
-Python invia a unity sull'outputText2 il messaggio "Caricare o Generare?".
Unity registra un nuovo audio (es. "Generare") e lo invia a Python che ne reinvia a unity lo speechtotext sull'outputText2.
--Quindi ci saranno due testi finali: l'oggetto da visualizzare sull'outputText e la modalità di importazione sull'outputtext2 (carica se è già salvato o genera altrimenti).
--A questo punto agisce lo script "click_button_carica_genera_tramite_audio" che clicca il button genera o carica in base a quanto vede scritto sull'outputtext2
"""



"""
from flask import Flask, request, jsonify
import speech_recognition as sr

app = Flask(__name__)

# Stati della logica
STATE_WAITING_FOR_TRIGGER = 0
STATE_PROCESS_SPEECH = 1
STATE_WAITING_FOR_COMMAND = 2

state = STATE_WAITING_FOR_TRIGGER

# Funzione per verificare se il testo contiene "Memora"
def contains_trigger_phrase(text):
    return "memora" in text.lower()

@app.route('/process-audio', methods=['POST'])
def process_audio():
    global state

    if 'file' not in request.files:
        return jsonify({'error': 'No file uploaded'}), 400

    audio_file = request.files['file']
    recognizer = sr.Recognizer()

    with sr.AudioFile(audio_file) as source:
        audio = recognizer.record(source)
        try:
            text = recognizer.recognize_google(audio, language="it-IT")
            print(f"Testo riconosciuto: {text}")

            # Gestione degli stati
            if state == STATE_WAITING_FOR_TRIGGER:
                if contains_trigger_phrase(text):
                    state = STATE_PROCESS_SPEECH
                    return jsonify({"text": "Cosa vorresti creare?"})
                else:
                    return jsonify({"text": ""})  # Ignora l'audio non rilevante

            elif state == STATE_PROCESS_SPEECH:
                state = STATE_WAITING_FOR_COMMAND
                return jsonify({"text": text, "next_message": "Caricare o Generare?"})  # Invio messaggio successivo

            elif state == STATE_WAITING_FOR_COMMAND:
                state = STATE_WAITING_FOR_TRIGGER  # Ritorna allo stato iniziale
                return jsonify({"text": text})  # Ritorna il comando ricevuto ("Caricare" o "Generare")

        except sr.UnknownValueError:
            return "", 204  # Audio non comprensibile
        except sr.RequestError:
            return "", 500  # Errore del servizio di riconoscimento

if __name__ == "__main__":
    app.run(host='0.0.0.0', port=5000)


"""


#Uguale al codice precedente ma questo approccio consente di riavviare il flusso in qualsiasi momento pronunciando "Ricomincia".

from flask import Flask, request, jsonify
import speech_recognition as sr

app = Flask(__name__)

# Stati della logica
STATE_WAITING_FOR_TRIGGER = 0
STATE_PROCESS_SPEECH = 1
STATE_WAITING_FOR_COMMAND = 2

state = STATE_WAITING_FOR_TRIGGER

# Funzione per verificare se il testo contiene "Memora"
def contains_trigger_phrase(text):
    return "memora" in text.lower()

# Funzione per verificare se il testo contiene "Ricomincia"
def is_restart_command(text):
    return "ricomincia" in text.lower()

@app.route('/process-audio', methods=['POST'])
def process_audio():
    global state

    if 'file' not in request.files:
        return jsonify({'error': 'No file uploaded'}), 400

    audio_file = request.files['file']
    recognizer = sr.Recognizer()

    with sr.AudioFile(audio_file) as source:
        audio = recognizer.record(source)
        try:
            text = recognizer.recognize_google(audio, language="it-IT")
            print(f"Testo riconosciuto: {text}")

            # Gestione degli stati
            if is_restart_command(text):  # Comando "Ricomincia"
                state = STATE_WAITING_FOR_TRIGGER
                return jsonify({"text": "Dì 'Memora' per iniziare."})

            if state == STATE_WAITING_FOR_TRIGGER:
                if contains_trigger_phrase(text):
                    state = STATE_PROCESS_SPEECH
                    return jsonify({"text": "Cosa vorresti creare?"})
                else:
                    return jsonify({"text": ""})  # Ignora l'audio non rilevante - Non mostra nulla se la parola "Memora" non è detta 
                    #return jsonify({"text": "Dì 'Memora' per iniziare."})  # Messaggio iniziale

            elif state == STATE_PROCESS_SPEECH:
                state = STATE_WAITING_FOR_COMMAND
                return jsonify({"text": text, "next_message": "Caricare o Generare?"})

            elif state == STATE_WAITING_FOR_COMMAND:
                state = STATE_WAITING_FOR_TRIGGER  # Ritorna allo stato iniziale
                return jsonify({"text": text})

        except sr.UnknownValueError:
            return "", 204  # Audio non comprensibile
        except sr.RequestError:
            return "", 500  # Errore del servizio di riconoscimento 

if __name__ == "__main__":
    app.run(host='0.0.0.0', port=5000)



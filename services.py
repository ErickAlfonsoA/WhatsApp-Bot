import requests
import sett
import json
import time
import sys
import datetime as dt
from datetime import timedelta
import calendario
from pathlib import Path

calendar = calendario.GoogleCalendarManager()

def obtener_Mensaje_whatsapp(message):
    if 'type' not in message :
        text = 'mensaje no reconocido'
        return text

    typeMessage = message['type']
    if typeMessage == 'text':
        text = message['text']['body']
    elif typeMessage == 'button':
        text = message['button']['text']
    elif typeMessage == 'interactive' and message['interactive']['type'] == 'list_reply':
        text = message['interactive']['list_reply']['title']
    elif typeMessage == 'interactive' and message['interactive']['type'] == 'button_reply':
        text = message['interactive']['button_reply']['title']
    else:
        text = 'mensaje no procesado'
    
    
    return text

def enviar_Mensaje_whatsapp(data):
    try:
        whatsapp_token = sett.whatsapp_token
        whatsapp_url = sett.whatsapp_url
        headers = {'Content-Type': 'application/json',
                   'Authorization': 'Bearer ' + whatsapp_token}
        print("se envia ", data)
        response = requests.post(whatsapp_url, 
                                 headers=headers, 
                                 data=data)
        
        if response.status_code == 200:
            return 'mensaje enviado', 200
        else:
            return 'error al enviar mensaje', response.status_code
    except Exception as e:
        return e,403
    
def text_Message(number,text):
    data = json.dumps(
            {
                "messaging_product": "whatsapp",    
                "recipient_type": "individual",
                "to": number,
                "type": "text",
                "text": {
                    "body": text
                }
            }
    )
    return data

def buttonReply_Message(number, options, body, footer, sedd,messageId):
    buttons = []
    for i, option in enumerate(options):
        buttons.append(
            {
                "type": "reply",
                "reply": {
                    "id": sedd + "_btn_" + str(i+1),
                    "title": option
                }
            }
        )

    data = json.dumps(
        {
            "messaging_product": "whatsapp",
            "recipient_type": "individual",
            "to": number,
            "type": "interactive",
            "interactive": {
                "type": "button",
                "body": {
                    "text": body
                },
                "footer": {
                    "text": footer
                },
                "action": {
                    "buttons": buttons
                }
            }
        }
    )
    return data

def listReply_Message(number, options, body, footer, sedd,messageId):
    rows = []
    for i, option in enumerate(options):
        rows.append(
            {
                "id": sedd + "_row_" + str(i+1),
                "title": option,
                "description": ""
            }
        )

    data = json.dumps(
        {
            "messaging_product": "whatsapp",
            "recipient_type": "individual",
            "to": number,
            "type": "interactive",
            "interactive": {
                "type": "list",
                "body": {
                    "text": body
                },
                "footer": {
                    "text": footer
                },
                "action": {
                    "button": "Ver Opciones",
                    "sections": [
                        {
                            "title": "Secciones",
                            "rows": rows
                        }
                    ]
                }
            }
        }
    )
    return data

def document_Message(number, url, caption, filename):
    data = json.dumps(
        {
            "messaging_product": "whatsapp",
            "recipient_type": "individual",
            "to": number,
            "type": "document",
            "document": {
                "link": url,
                "caption": caption,
                "filename": filename
            }
        }
    )
    return data

def sticker_Message(number, sticker_id):
    data = json.dumps(
        {
            "messaging_product": "whatsapp",
            "recipient_type": "individual",
            "to": number,
            "type": "sticker",
            "sticker": {
                "id": sticker_id
            }
        }
    )
    return data

def get_media_id(media_name , media_type):
    media_id = ""
    if media_type == "sticker":
        media_id = sett.stickers.get(media_name, None)
    #elif media_type == "image":
    #    media_id = sett.images.get(media_name, None)
    #elif media_type == "video":
    #    media_id = sett.videos.get(media_name, None)
    #elif media_type == "audio":
    #    media_id = sett.audio.get(media_name, None)
    return media_id

def replyReaction_Message(number, messageId, emoji):
    data = json.dumps(
        {
            "messaging_product": "whatsapp",
            "recipient_type": "individual",
            "to": number,
            "type": "reaction",
            "reaction": {
                "message_id": messageId,
                "emoji": emoji
            }
        }
    )
    return data

def replyText_Message(number, messageId, text):
    data = json.dumps(
        {
            "messaging_product": "whatsapp",
            "recipient_type": "individual",
            "to": number,
            "context": { "message_id": messageId },
            "type": "text",
            "text": {
                "body": text
            }
        }
    )
    return data

def markRead_Message(messageId):
    data = json.dumps(
        {
            "messaging_product": "whatsapp",
            "status": "read",
            "message_id":  messageId
        }
    )
    return data

def administrar_chatbot(text,number, messageId, name):
    text = text.lower() #mensaje que envio el usuario
    list = []
    options2 = []
    print("mensaje del usuario: ",text, messageId)
    
    markRead = markRead_Message(messageId)
    list.append(markRead)
    time.sleep(2)
    
    data = 'data2.json' # Comprobar que exista el json
    salF = Path('.') / data
    if not salF.exists:
        print("No existe el archivo de entrada")
        sys.exit()

    jdata = None
    with salF.open(encoding="utf-8") as fjson: # Abrir el json y cargarlo en la variable jdata
        jdata = json.load(fjson)
        
    for jda in jdata["Analisis"]:
        options2 += [jda[0].lower()]
              
    if not hasattr(administrar_chatbot, "opciones"):
        setattr(administrar_chatbot, "opciones", options2)
        setattr(administrar_chatbot, "contador", 0)
        
    horarios = ["07:00", "07:30", "08:00", "08:30", "09:00", "09:30", "10:00", "10:30", "11:00", "11:30", "12:00", "12:30", "13:00", "13:30", "14:00"]
    hola = ["hola", "ola", "oli", "alo", "buenas tardes", "hola, buenas tardes", "hola buenas tardes", "holi", 
           "buenas noches", "buenos dias", "hola, buenas noches", "hola, buenos dias", "hola buenas noches", "hola buenos dias"]
    
    if text in hola:
        body = "¡Hola! 👋 Bienvenido a Clinica San Juan. ¿Cómo podemos ayudarte hoy?"
        footer = "Laboratorios San Juan"
        options = ["📑 Cotizar Analisis", "📅 Agendar cita", "🖐 Terminar"]

        replyButtonData = buttonReply_Message(number, options, body, footer, "sed1",messageId)
        replyReaction = replyReaction_Message(number, messageId, "🫡")
        list.append(replyReaction)
        list.append(replyButtonData)
    elif "📑 cotizar analisis" == text:
        body = "Tenemos varios analisis a elegir. ¿Cuál de estos analisis te gustaría cotizar? ✨\n📱 Para atencion personalizada puede llamar al 427 274 9664\n💬 o mandar whatsapp al 427 121 0690"
        footer = "Laboratorios San Juan"
        options = []
        
        #cont = administrar_chatbot.contador
        cont = 0
        for jda in jdata["Analisis"]:
            cont += 1
            options += [jda[0].lower()]
            if cont == 8:
                break
              
        setattr(administrar_chatbot, "contador", 8)
        options += ["⏮ Anterior pagina"]
        options += ["⏭ siguiente pagina"]
        print(options, "\n")

        print(administrar_chatbot.opciones)
        #Limite de caracteres en 24, solo caben 10 en una lista
        #options = ["Biometria Hematica", "Migración Cloud", "Inteligencia de Negocio"]

        listReplyData = listReply_Message(number, options, body, footer, "sed2",messageId)
        sticker = sticker_Message(number, get_media_id("perro_traje", "sticker"))

        list.append(listReplyData)
        list.append(sticker)
    elif "⏭ siguiente pagina" == text:
        cont = administrar_chatbot.contador
        if cont + 8 > len(jdata['Analisis']):
            cont = 0
        body = "🎉 Mostrando siguiente pagina 🎉\n📖 "+str(cont+8)+" - "+str(len(jdata['Analisis']))+"\n📱 Para atencion personalizada puede llamar al 427 274 9664\n💬 o mandar whatsapp al 427 121 0690"
        footer = "Laboratorios San Juan"
        options = []
        
        for ra in range(cont, cont+8):
            options += [jdata['Analisis'][ra][0].lower()]
              
        setattr(administrar_chatbot, "contador", cont + 8)
        options += ["⏮ Anterior pagina"]
        options += ["⏭ Siguiente pagina"]
        print(options, "\n")

        print(getattr(administrar_chatbot, "contador"))
        print(administrar_chatbot.contador)
        #Limite de caracteres en 24, solo caben 10 en una lista
        #options = ["Biometria Hematica", "Migración Cloud", "Inteligencia de Negocio"]

        listReplyData = listReply_Message(number, options, body, footer, "sed3",messageId)
        sticker = sticker_Message(number, get_media_id("perro_traje", "sticker"))

        list.append(listReplyData)
        list.append(sticker)
    elif "⏮ anterior pagina" == text:
        cont = administrar_chatbot.contador - 8
        if cont <= 0 :
            cont = len(jdata['Analisis'])
        body = "🎉 Mostrando pagina anterior 🎉\n📖 "+str(cont)+" - "+str(len(jdata['Analisis']))+"\n📱 Para atencion personalizada puede llamar al 427 274 9664\n💬 o mandar whatsapp al 427 121 0690"
        footer = "Laboratorios San Juan"
        options = []
        
        for ra in range(cont-8, cont):
            options += [jdata['Analisis'][ra][0].lower()]
              
        setattr(administrar_chatbot, "contador", cont)
        options += ["⏮ Anterior pagina"]
        options += ["⏭ Siguiente pagina"]
        print(options, "\n")

        print(getattr(administrar_chatbot, "contador"))
        print(administrar_chatbot.contador)
        #Limite de caracteres en 24, solo caben 10 en una lista
        #options = ["Biometria Hematica", "Migración Cloud", "Inteligencia de Negocio"]

        listReplyData = listReply_Message(number, options, body, footer, "sed4",messageId)
        sticker = sticker_Message(number, get_media_id("perro_traje", "sticker"))

        list.append(listReplyData)
        list.append(sticker)
    elif text in administrar_chatbot.opciones:
        for jda in jdata['Analisis']:
          if text.lower() == jda[0].lower():
            body = "🧪 "+text+"\n 💰 costo: "+str(jda[1])+"\n 📑 requisitos: "+jda[5]+"\n ⏲ tiempo de entrega: "+jda[6]
        footer = "Laboratorios San Juan"
        options = ["📑 Cotizar Analisis", "📅 Agendar cita", "🖐 Terminar"]
        
        replyButtonData = buttonReply_Message(number, options, body, footer, "sed5",messageId)
        list.append(replyButtonData)
    #Seccion para las citas
    elif "📅 agendar cita" == text:
        users = []
        citas = calendar.list_upcoming_events()
        for ci in citas:
            users += [ci['summary']]
            
        if number in users:
            body = "Lo siento, usted ya tiene una cita agendada 😖\n¿Desea cancelar la cita ya agendada? 🤭"
            footer = "Laboratorios San Juan"
            options = ["❌ Cancelarla", "🔄 Cambiarla", "🛑 Conservarla"]
            
            replyButtonData = buttonReply_Message(number, options, body, footer, "sed6",messageId)
            list.append(replyButtonData)

        else:
            sticker = sticker_Message(number, get_media_id("pelfet", "sticker"))
            textMessage = text_Message(number,"Genial, por favor espera un momento.")

            setattr(administrar_chatbot, "contador", 0)

            enviar_Mensaje_whatsapp(sticker)
            #enviar_Mensaje_whatsapp(textMessage)
            #time.sleep(3)

            day = dt.datetime.now()
            tomorrow = day + timedelta(days=1)#1
            tomorrow2 = day + timedelta(days=2)#2
            tomorrow3 = day + timedelta(days=3)#3
            tomorrow4 = day + timedelta(days=4)#4

            if tomorrow.strftime("%A") == "Sunday":
                tomorrow = tomorrow + timedelta(days=1)
                tomorrow2 = tomorrow2 + timedelta(days=1)
                tomorrow3 = tomorrow3 + timedelta(days=1)
                tomorrow4 = tomorrow4 + timedelta(days=1)
            elif tomorrow2.strftime("%A") == "Sunday":
                tomorrow2 = tomorrow2 + timedelta(days=1)
                tomorrow3 = tomorrow3 + timedelta(days=1)
                tomorrow4 = tomorrow4 + timedelta(days=1)
            elif tomorrow3.strftime("%A") == "Sunday":
                tomorrow3 = tomorrow3 + timedelta(days=1)
                tomorrow4 = tomorrow4 + timedelta(days=1)
            elif tomorrow4.strftime("%A") == "Sunday":
                tomorrow4 = tomorrow4 + timedelta(days=1)
            else:
                pass

            body = "¿Para que dia quisiera agendar cita? 📅🙆‍♀️"
            footer = "Laboratorios San Juan"
            options = [tomorrow.strftime("%A %d. %B %Y").lower(), tomorrow2.strftime("%A %d. %B %Y").lower(), tomorrow3.strftime("%A %d. %B %Y").lower(), tomorrow4.strftime("%A %d. %B %Y").lower()]

            #calendar.create_event("Hola youtube","2024-03-01T16:00:00+02:00","2024-03-01T17:00:00+02:00","Europe/Madrid",["gumikhe@gmail.com"])

            if not hasattr(administrar_chatbot, "days"):
                setattr(administrar_chatbot, "days", options)

            print(administrar_chatbot.days)
            listReplyData = listReply_Message(number, options, body, footer, "sed7",messageId)
            list.append(listReplyData)
    elif "❌ cancelarla" == text:
        citas = calendar.list_upcoming_events()
        date = []
        for ci in citas:
            date += [[ci['summary'], ci['start']['dateTime'], ci['id']]]

        for da in date:
            if number == da[0]:
                d = dt.datetime.strptime(da[1][0:10], "%Y-%m-%d")
                body = "Su cita que era para el "+str(d.strftime("%A %d. %B %Y"))+" a las "+da[1][11:19]+" fue cancelada"
                footer = "Laboratorios San Juan"
                options = ["📑 Cotizar Analisis", "📅 Agendar cita"]
                
                calendar.delete_event(da[2])
                
        replyButtonData = buttonReply_Message(number, options, body, footer, "sed8",messageId)
        list.append(replyButtonData)
    elif "🛑 conservarla" == text:
        citas = calendar.list_upcoming_events()
        date = []
        for ci in citas:
            date += [[ci['summary'], ci['start']['dateTime'], ci['id']]]

        for da in date:
            if number == da[0]:
                d = dt.datetime.strptime(da[1][0:10], "%Y-%m-%d")
                body = "Ok!! conservaremos su cita para el "+str(d.strftime("%A %d. %B %Y"))+" a las "+da[1][11:19]
                footer = "Laboratorios San Juan"
                options = ["📑 Cotizar Analisis", "🖐 Terminar"]
                
        replyButtonData = buttonReply_Message(number, options, body, footer, "sed9",messageId)
        list.append(replyButtonData)
    elif "🔄 cambiarla" == text:
        citas = calendar.list_upcoming_events()
        date = []
        for ci in citas:
            date += [[ci['summary'], ci['start']['dateTime'], ci['id']]]

        for da in date:
            if number == da[0]:
                calendar.delete_event(da[2])

        setattr(administrar_chatbot, "contador", 0)

        day = dt.datetime.now()
        tomorrow = day + timedelta(days=1)#1
        tomorrow2 = day + timedelta(days=2)#2
        tomorrow3 = day + timedelta(days=3)#3
        tomorrow4 = day + timedelta(days=4)#4

        if tomorrow.strftime("%A") == "Sunday":
            tomorrow = tomorrow + timedelta(days=1)
            tomorrow2 = tomorrow2 + timedelta(days=1)
            tomorrow3 = tomorrow3 + timedelta(days=1)
            tomorrow4 = tomorrow4 + timedelta(days=1)
        elif tomorrow2.strftime("%A") == "Sunday":
            tomorrow2 = tomorrow2 + timedelta(days=1)
            tomorrow3 = tomorrow3 + timedelta(days=1)
            tomorrow4 = tomorrow4 + timedelta(days=1)
        elif tomorrow3.strftime("%A") == "Sunday":
            tomorrow3 = tomorrow3 + timedelta(days=1)
            tomorrow4 = tomorrow4 + timedelta(days=1)
        elif tomorrow4.strftime("%A") == "Sunday":
            tomorrow4 = tomorrow4 + timedelta(days=1)
        else:
            pass

        body = "¿Para que dia quisiera agendar cita? 📅🙆‍♀️"
        footer = "Laboratorios San Juan"
        options = [tomorrow.strftime("%A %d. %B %Y").lower(), tomorrow2.strftime("%A %d. %B %Y").lower(), tomorrow3.strftime("%A %d. %B %Y").lower(), tomorrow4.strftime("%A %d. %B %Y").lower()]

        #calendar.create_event("Hola youtube","2024-03-01T16:00:00+02:00","2024-03-01T17:00:00+02:00","Europe/Madrid",["gumikhe@gmail.com"])

        if not hasattr(administrar_chatbot, "days"):
            setattr(administrar_chatbot, "days", options)

        print(administrar_chatbot.days)
        listReplyData = listReply_Message(number, options, body, footer, "sed10",messageId)
        list.append(listReplyData)
    
    elif "🖐 terminar" == text:
        textMessage = text_Message(number,"Perfecto! No dudes en contactarnos si tiens dudas 🎃\n📱 Para atencion personalizada puede llamar al 427 274 9664\n💬 o mandar whatsapp al 427 121 0690")
        list.append(textMessage)
    elif text in administrar_chatbot.days:
        setattr(administrar_chatbot, "dia", text)
        body = "Genial!! por favor ahora seleccione un horario ✨"
        footer = "Laboratorios San Juan"
        options = []
        a = []
        dia2 = str(dt.datetime.strptime(administrar_chatbot.dia, "%A %d. %B %Y"))
        
        citas = calendar.list_upcoming_events()
        date = []
        for ci in citas:
            date += [[ci['summary'], ci['start']['dateTime'], ci['id']]]
            
        for da in date:
            if da[1][8:10] == dia2[8:10]:
                for h in horarios:
                    if da[1][11:16] == h:
                        a += [h]  #Horarios que no se ocupan
                        
        b = [] #Horarios sin los que estan ocupados
        for h in horarios:
            if h in a:
                pass
            else:
                b += [h]
              
        for h in b:
            options += [h]
            if len(options) == 5:
                break
        
        setattr(administrar_chatbot, "contador", 5)
        setattr(administrar_chatbot, "auxi", b)
        print(b)
        options += ["⏮ Anteriores horarios"]
        options += ["⏭ Siguientes horarios"]
        print(options, "\n")
        
        listReply = listReply_Message(number, options, body, footer, "sed10",messageId)
        list.append(listReply)
    elif "⏭ siguientes horarios" == text:
        body = "🎉 Mostrando siguientes horarios 🎉"
        footer = "Laboratorios San Juan"
        options = []

        cont = administrar_chatbot.contador
        if cont + 5 > 15:
            cont = 0
        #for h in range(cont, cont+5, 1):
        #    options += [horarios[h]]
        
        aux = administrar_chatbot.auxi   
                        
        for au in range(cont, cont+5, 1):
            try:
                options += [aux[au]]
            except IndexError:
                break

        print(aux)
             
        setattr(administrar_chatbot, "contador", cont + 5)
        options += ["⏮ Anteriores horarios"]
        options += ["⏭ Siguientes horarios"]
        print(options, "\n")
        
        listReply = listReply_Message(number, options, body, footer, "sed11",messageId)
        list.append(listReply)
    elif "⏮ anteriores horarios" == text:
        body = "🎉 Mostrando anteriores horarios 🎉"
        footer = "Laboratorios San Juan"
        options = []

        cont = administrar_chatbot.contador - 5
        if cont <= 0:
            cont = 15
        #for h in range(cont-5, cont, 1):
        #    options += [horarios[h]]
         
                        
        aux = administrar_chatbot.auxi   
        
        for au in range(cont-5, cont, 1):
            try:
                options += [aux[au]]
            except IndexError:
                break

        print(aux)
        
          
        setattr(administrar_chatbot, "contador", cont)
        options += ["⏮ Anteriores horarios"]
        options += ["⏭ Siguientes horarios"]
        print(options, "\n")
        
        listReply = listReply_Message(number, options, body, footer, "sed12",messageId)
        list.append(listReply)
    elif text in horarios:
        setattr(administrar_chatbot, "contador", 0)
        setattr(administrar_chatbot, "hora", text)
        
        dia = administrar_chatbot.dia
        hora = administrar_chatbot.hora
        
        body = "Excelente, has seleccionado el día "+dia+" a las "+hora+". ¿Necesitas algo mas? ✨"
        footer = "Laboratorios San Juan"
        options = ["📑 Cotizar Analisis ", "❌ No, gracias."]
        
        dia = dt.datetime.strptime(dia, "%A %d. %B %Y")
        if hora[3:5] == "30":
            h1 = dia + timedelta(hours=int(hora[0:2]), minutes=int(hora[3:5]))
            h2 = dia + timedelta(hours=int(hora[0:2]) + 1, minutes=int(hora[3:5]))
        else:    
            h1 = dia + timedelta(hours=int(hora[0:2]), minutes=int(hora[3:5]))  
            h2 = dia + timedelta(hours=int(hora[0:2]), minutes=int(hora[3:5]) + 30)
        
        calendar.create_event(number, h1.isoformat(), h2.isoformat(),"America/Mexico_City",["gumikhe@gmail.com"])
        
        buttonReply = buttonReply_Message(number, options, body, footer, "sed13",messageId)
        list.append(buttonReply)
    elif "no, gracias." in text:
        textMessage = text_Message(number,"Perfecto! No dudes en contactarnos si tiens dudas 🎃\n📱 Para atencion personalizada puede llamar al 427 274 9664\n💬 o mandar whatsapp al 427 121 0690")
        list.append(textMessage)
    else:
        print(text)
        print(administrar_chatbot.opciones)
        data = text_Message(number,"Lo siento, no entendí lo que dijiste 😖. Si quieres comenzar una conversacion conmigo Lab-Bot🧪 escribe: hola\n📱 Para atencion personalizada puede llamar al 427 274 9664\n💬 o mandar whatsapp al 427 121 0690")
        list.append(data)

    for item in list:
        enviar_Mensaje_whatsapp(item)

#al parecer para mexico, whatsapp agrega 521 como prefijo en lugar de 52,
# este codigo soluciona ese inconveniente.
def replace_start(s):
    number = s[3:]
    if s.startswith("521"):
        return "52" + number
    elif s.startswith("549"):
        return "54" + number
    else:
        return s
        


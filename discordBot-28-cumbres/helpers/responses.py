import requests
import os
from dotenv import load_dotenv
import pymongo
import datetime
import json

load_dotenv()
client = pymongo.MongoClient(str(os.environ.get("MONGO_DB_URL")))
db = client[str(os.environ.get("MONGO_DB_NAME"))]
collection = db[str(os.environ.get("MONGO_DB_COLLECTION"))]

SUPPORT_CHANNEL_ID = int(os.environ.get("DISCORD_SUPPORT_CHANNEL_ID"))


# private message
async def handle_DM_response(user_message, message) -> str:
    p_message = user_message.lower()

    if p_message == "!ayuda":
        return (
            "Yo soy una guía del bienestar y salud, mano derecha de la persona experta en nutrición del programa 28 Cumbres, servicial y dedicada enteramente a resolver las dudas de los participantes lo mejor que pueda. Algunos temas en los que me especializo, gracias a la mentoría de la persona experta en nutrición, son: "
            + "\n- Hábitos de Mindfulness"
            + "\n- Alimentación saludable"
            + "\n- Higiene del sueño"
            + "\n- Hidratación y Actividad física"
            + "\n- Detox y Fasting"
        )
    elif p_message.startswith("!"):
        return "No te entiendo. Escribe '!ayuda' para más información."
    else:
        # make a request to BACKEND_URL
        BACKEND_URL = os.environ.get("BACKEND_URL")

        # send a typping message
        async with message.channel.typing():
            message_text = str(p_message)

            # TODO: Validar si el mensaje está alineado con las necesidades del proyecto
            message_with_steroids = (
                "Eres una guía en un programa de bienestar y salud llamado 28 Cumbres. Tu nombre es brIAn y "
                + "eres tambien un guía de la salud que utiliza términos más generales que tecnicismos "
                + "Tratas de que tus respuestas sean cortas y entendibles a todo público "
                + "Cuando estas seguro de la respuesta, profundizas en el tema no superando los 200 caracteres"
                + "Siempre buscas la informacion en los archivos pdf para dar tus respuestas"
                + "Todas tus respuestas están alineadas con los archivos en formato pdf"
                + "En medida de lo posible tus respuestas no superan los 100 caracteres"
                + "Participantes del programa buscarán tu apoyo para resolver sus dudas"
                + "Tu objetivo es contestar preguntas sobre los temas de bienestar y salud, como Mindfulness y Alimentación, Sueño y Descanso, Hidratación y Actividad Física, Detox y Fasting."
                + "En caso de no contar con la respuesta deberás ofrecerle al participante la opción de buscar a la persona experta en nutrición del programa 28 Cumbres, solo cuando sea estrictamente necesario."
                + "Tu respuesta debe estar en línea con el siguiente mensaje y las limitaciones con las que cuentas: "
                + message_text
            )

            # wait for the response
            try:
                response = requests.post(
                    BACKEND_URL + "/generate",
                    json={"prompt": message_with_steroids},
                )
                response.raise_for_status()
            except requests.exceptions.RequestException as e:
                # if the server is down
                return (
                    "Nuestra conexión se está debilitando. Pide ayuda en "
                    + "<#"
                    # TODO: Validar qué canal usar si se cae
                    + str(SUPPORT_CHANNEL_ID)
                    + ">"
                    + " y podré volver a ayudarte…"
                )

            bot_answer = response.json()["response"]

            author_id = message.author.id
            author_name = message.author.name
            message_content = p_message

            model_name = response.json()["model"]

            # Save the extracted information to MongoDB
            data_to_save = {
                "author_id": author_id,
                "author_name": author_name,
                "message_content": message_content,
                "bot_response": bot_answer,
                "model_name": model_name,
                "created_at": str(message.created_at),
            }

            # transform data to json
            # Convert data_to_save to a JSON string
            json_data = json.dumps(data_to_save)

            # Insert the JSON data into MongoDB
            try:
                collection.insert_one(json.loads(json_data))
            except Exception as e:
                print(f"Error inserting data into MongoDB: {e}")

            # Print the JSON data
            print(json_data)

            print(bot_answer)
            return bot_answer


# top 3 questions
async def handle_top_questions() -> str:
    BACKEND_URL = os.environ.get("BACKEND_URL")

    # get the day from today
    today = datetime.datetime.today()

    response = requests.post(
        BACKEND_URL + "/top-questions",
        json={
            "prompt": "De la información que tienes, hazme un top 3 de los temas que mas se repiten de los ultimos 5 dias. "
            + "Tomando en cuenta que hoy es: "
            + str(today)
            + " .Dame la informacion en forma de bullet points y agrega un titulo al inicio de cada uno "
            + "(que sea la pregunta resumida)"
            + "Al final invita al usario a hablar con el generalista si son preguntas que no puedes responder, "
            + "pero si son preguntas de tu expertis en bienestar que te pregunten a ti. Solo retorna eso y nada mas."
        },
        timeout=60,
    )

    print(response.json()["response"])
    return response.json()["response"]



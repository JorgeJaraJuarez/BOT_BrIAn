import os
import logging
import sys
import pymongo
import json
from bson import json_util, ObjectId

from llama_index import SummaryIndex, SimpleMongoReader

from dotenv import load_dotenv

load_dotenv()

logging.basicConfig(stream=sys.stdout, level=logging.INFO)
logging.getLogger().addHandler(logging.StreamHandler(stream=sys.stdout))

# get OPENAI_API_KEY from the .env
os.environ["OPENAI_API_KEY"] = os.getenv("OPENAI_API_KEY")

# mongo db
MONGO_DB_URL = str(os.getenv("MONGO_DB_URL"))
MONGO_DB_PORT = int(os.getenv("MONGO_DB_PORT"))

MONGO_DB_NAME = str(os.getenv("MONGO_DB_NAME"))
MONGO_DB_COLLECTION = str(os.getenv("MONGO_DB_COLLECTION"))


def load_db():
    query_dict = {}
    # change according to your needs

    # for the querying it takes 43 seconds
    # field_names = ["message_content", "bot_response"]

    # for the querying it takes 4 seconds
    field_names = ["message_content", "created_at"]
    reader = SimpleMongoReader(MONGO_DB_URL, MONGO_DB_PORT)

    documents = reader.load_data(
        MONGO_DB_NAME, MONGO_DB_COLLECTION, field_names, query_dict=query_dict
    )

    print(f"Loaded {len(documents)} documents from mongo")

    index = SummaryIndex.from_documents(documents)

    index.storage_context.persist(persist_dir="mongo_index")

    return index


def get_all_messages():
    client = pymongo.MongoClient(MONGO_DB_URL, MONGO_DB_PORT)

    db = client[MONGO_DB_NAME]
    collection = db[MONGO_DB_COLLECTION]

    # get all the messages
    messages = list(collection.find({}))

    client.close()

    # Convert the documents to JSON
    # and print out the results
    json_messages = json.dumps(messages, indent=2, default=json_util.default)

    # turn the json into a python object
    json_messages = json.loads(json_messages)
    return json_messages


def get_all_questions():
    client = pymongo.MongoClient(MONGO_DB_URL, MONGO_DB_PORT)

    db = client[MONGO_DB_NAME]
    collection = db[MONGO_DB_COLLECTION]

    projection = {"bot_response": 0}

    # get all the questions, the attribute "message_content" is the question
    messages = list(collection.find({"message_content": {"$exists": True}}, projection))

    client.close()

    # Convert the documents to JSON
    # and print out the results
    json_messages = json.dumps(messages, indent=2, default=json_util.default)

    # turn the json into a python object
    json_messages = json.loads(json_messages)
    return json_messages


def delete_message_by_id(id):
    client = pymongo.MongoClient(MONGO_DB_URL, MONGO_DB_PORT)

    db = client[MONGO_DB_NAME]
    collection = db[MONGO_DB_COLLECTION]

    # check if the message exists
    try:
        collection.find_one({"_id": ObjectId(id)})
    except:
        client.close()
        return {"error": "Message not found or not updated"}

    collection.delete_one({"_id": ObjectId(id)})

    client.close()
    return True


def update_message_by_id(id, new_message=None, new_bot_response=None):
    client = pymongo.MongoClient(MONGO_DB_URL, MONGO_DB_PORT)

    db = client[MONGO_DB_NAME]
    collection = db[MONGO_DB_COLLECTION]

    # Check if the message exists
    try:
        collection.find_one({"_id": ObjectId(id)})
    except:
        client.close()
        return {"error": "Message not found or not updated"}

    # Prepare the update query
    update_query = {"$set": {}}

    if new_message is not None:
        update_query["$set"]["message_content"] = new_message

    if new_bot_response is not None:
        update_query["$set"]["bot_response"] = new_bot_response

    # Perform the update
    collection.update_one({"_id": ObjectId(id)}, update_query)

    # Convert the results to a dictionary object
    result = {
        "success": True,
        "message": "Record successfully updated",
        "updated_result": json.loads(
            json_util.dumps(collection.find_one({"_id": ObjectId(id)}))
        ),
    }

    return result

# 28 Cumbres
from dotenv import load_dotenv
from flask import Flask, request, jsonify
from flask_cors import CORS
import os

load_dotenv()

# get OPENAI_API_KEY from the .env
os.environ["OPENAI_API_KEY"] = os.getenv("OPENAI_API_KEY")

from llama_index import (
    SimpleDirectoryReader,
    VectorStoreIndex,
    LLMPredictor,
    ServiceContext,
    PromptHelper,
    StorageContext,
    load_index_from_storage,
)
from langchain.chat_models import ChatOpenAI

# mongo
import helpers.mongo_questions

app = Flask(__name__)
CORS(app)


# pdfs
def init_index(directory_path):
    # model params
    # max_input_size: maximum size of input text for the model.
    # num_outputs: number of output tokens to generate.
    # max_chunk_overlap: maximum overlap allowed between text chunks.
    # chunk_size_limit: limit on the size of each text chunk.
    # max_input_size = 4096
    # max_input_size = 5096
    # num_outputs = 1024
    # num_outputs = 4096
    # max_chunk_overlap = 20
    # max_chunk_overlap = 100
    # chunk_size_limit = 600
    # chunk_size_limit = 1000

    context_window = 3900
    num_output = 256
    chunk_overlap_ratio = 0.1
    chunk_size_limit = None
    separator = " "

    # llm predictor with langchain ChatOpenAI
    # ChatOpenAI model is a part of the LangChain library and is used to interact with the GPT-3.5-turbo model provided by OpenAI
    prompt_helper = PromptHelper(
        context_window=context_window,
        num_output=num_output,
        chunk_overlap_ratio=chunk_overlap_ratio,
        chunk_size_limit=chunk_size_limit,
        separator=separator,
    )

    llm_predictor = LLMPredictor(
        llm=ChatOpenAI(
            temperature=0.7,
            model_name="gpt-3.5-turbo",
            max_tokens=num_output,
            # temperature=0.7,
            # model_name="gpt-4",
            # max_tokens=num_outputs,
        )
    )

    # read documents from docs folder
    documents = SimpleDirectoryReader(directory_path).load_data()

    # init index with documents data
    # This index is created using the LlamaIndex library. It processes the document content and constructs the index to facilitate efficient querying
    service_context = ServiceContext.from_defaults(
        llm_predictor=llm_predictor, prompt_helper=prompt_helper
    )
    index = VectorStoreIndex.from_documents(documents, service_context=service_context)

    # save the created index
    index.storage_context.persist(persist_dir="index")

    # load mongo info
    helpers.mongo_questions.load_db()

    return index


# say hello to see if the server is running
@app.route("/")
def hello():
    return "Hello, World!"


# Chatbot API endpoint
@app.route("/generate", methods=["POST"])
def generate():
    input_text = request.json.get("prompt")

    storage_context = StorageContext.from_defaults(persist_dir="index")

    # load index
    index = load_index_from_storage(storage_context)

    # get response for the question
    query_engine = index.as_query_engine()
    response = query_engine.query(input_text)
    model = index.service_context.llm.model

    return jsonify({"response": response.response, "model": model})


# Top 3 questions asked
@app.route("/top-questions", methods=["POST"])
def top_questions():
    num_output = 256
    # update mongo db index
    helpers.mongo_questions.load_db()

    input_text = request.json.get("prompt")

    storage_context = StorageContext.from_defaults(persist_dir="mongo_index")

    # load index
    index = load_index_from_storage(storage_context)

    gpt_35_context = ServiceContext.from_defaults(
        llm=ChatOpenAI(model="gpt-3.5-turbo", temperature=0.7, max_tokens=num_output),
    )

    # get response for the question
    query_engine = index.as_query_engine(service_context=gpt_35_context)
    response = query_engine.query(input_text)
    model = index.service_context.llm.model

    print("MODEL:")
    print(model)

    print(response.response)

    return jsonify({"response": response.response, "model": model})


# get all the messages
@app.route("/messages", methods=["GET"])
def get_all_messages():
    return jsonify({"messages": helpers.mongo_questions.get_all_messages()})


# get all the questions
@app.route("/questions", methods=["GET"])
def get_all_questions():
    return jsonify({"questions": helpers.mongo_questions.get_all_questions()})


# delete message by id
@app.route("/messages/<id>", methods=["DELETE"])
def delete_message_by_id(id):
    return jsonify({"result": helpers.mongo_questions.delete_message_by_id(id)})


# update message by id
@app.route("/messages/<id>", methods=["PUT"])
def update_message_by_id(id):
    new_message = request.json.get("message_content")
    new_bot_response = request.json.get("bot_response")
    return jsonify(
        {
            "result": helpers.mongo_questions.update_message_by_id(
                id, new_message, new_bot_response
            )
        }
    )


if __name__ == "__main__":
    init_index("docs")
    app.run(host="0.0.0.0", port=5000)

## What it is

This is an API that uses Langchain and Llama Index with OpenAI's GPT-3.5-turbo to generate text based on a given prompt. It can read information from a MongoDB database and use it to generate text.

## How to use

### Setup

1. Clone this repository
2. Install the dependencies with `pip install -r requirements.txt`
3. Create a .env file with the following variables:

```
OPENAI_API_KEY=<your OpenAI API key>
MONGO_DB_URL=<your MongoDB URI>
MONGO_DB_PORT==<your MongoDB PORT>

MONGB_DB_NAME==<your MongoDB DB Name>
MONGO_DB_COLLECTION=<your MongoDB DB Collection>
```

4. Upload the PDFs files to "/docs".

### Usage

1. Run the server with `python model.py`

2. Send a POST request to `http://localhost:5000/generate` with the following JSON body:

It will return any information specified in the prompt. It will respond with the knowledge base information of the PDFs.

```json
{
  "prompt": "This is a test prompt"
}
```

3. Send a POST request to `http://localhost:5000/top-questions` with the following JSON body:

It will return any information specified in the prompt. It will respond with the knowledge base information of the MongoDB database.

```json
{
  "prompt": "This is a test prompt"
}
```

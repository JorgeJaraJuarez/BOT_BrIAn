## What it is

This is a Discord bot that can be used to respond to messages that is configured in a .env file. And it asks to another API to get the data.

## How to use

### Setup

1. Clone this repository
2. Install the dependencies with `pip install -r requirements.txt`
3. Create a .env file with the variables listed below

```
   DISCORD_BOT_TOKEN = <token>
   DISCORD_APP_ID = <id>
   DISCORD_CATEGORY_CHANNEL_ID = <id of category channel>
   DISCORD_SUPPORT_CHANNEL_ID = <id of support channel>

   BACKEND_URL = <url of external API>

   MONGO_DB_URL = <url of mongoDB>
   MONGO_DB_NAME = <name database mongoDB>
   MONGO_DB_COLLECTION = <name collection mongoDB>

   # cron job del top questions
   TOP_Q_CRON_DAY_OF_WEEK = <str day of the week, mon - sun>
   TOP_Q_CRON_HOUR = <str hour 00 - 24>
   TOP_Q_CRON_MINUTE = <str minute 00 - 60>

   # cron job introducing texts
   INTRO_T_CRON_DAY_OF_WEEK = <str day of the week, mon - sun>
   INTRO_T_CRON_HOUR = <str hour 00 - 24>
   INTRO_T_CRON_MINUTE = <str minute 00 - 60>
```

### Usage

1. Run the bot with `python main.py`

### Things to know

- The bot will only respond to messages in channels called by a slash command `/sofia` and then it will send a DM to that user. The help guide is `!ayuda`.
- The bot will then only answer to messages in DMs.
- The third party API is a LLM with Langchain, Llama index and it makes requests to the API OpenAI.

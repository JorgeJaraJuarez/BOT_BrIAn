import discord
from discord.ext import commands
from dotenv import load_dotenv
import os
import helpers.responses as responses

import json
import random

from apscheduler.schedulers.asyncio import AsyncIOScheduler

# from apscheduler.schedulers.blocking import BlockingScheduler

load_dotenv()

# Define the bot's intents
intents = discord.Intents.default()
intents.message_content = True
intents.guilds = True
intents.integrations = True

bot = commands.Bot(command_prefix="!", intents=intents)

# CRON JOB TIME
TOP_Q_CRON_DAY_OF_WEEK = str(os.getenv("TOP_Q_CRON_DAY_OF_WEEK"))
TOP_Q_CRON_HOUR = str(os.getenv("TOP_Q_CRON_HOUR"))
TOP_Q_CRON_MINUTE = str(os.getenv("TOP_Q_CRON_MINUTE"))


INTRO_T_CRON_DAY_OF_WEEK = str(os.getenv("INTRO_T_CRON_DAY_OF_WEEK"))
INTRO_T_CRON_HOUR = str(os.getenv("INTRO_T_CRON_HOUR"))
INTRO_T_CRON_MINUTE = str(os.getenv("INTRO_T_CRON_MINUTE"))


@bot.event
async def on_ready():
    print(f"{bot.user} has connected to Discord!")
    # Initialize the scheduler
    # scheduler = AsyncIOScheduler()

    # test cron job
    # scheduler.add_job(schedule_top_questions, "interval", minutes=1)

    # Send top 3 questions every week
    # scheduler.add_job(
    #     schedule_top_questions,
    #     "cron",
    #     day_of_week=TOP_Q_CRON_DAY_OF_WEEK,
    #     hour=TOP_Q_CRON_HOUR,
    #     minute=TOP_Q_CRON_MINUTE,
    # )

    # Send introducing messages every week
    # scheduler.add_job(
    #     send_introducing_message,
    #     "cron",
    #     day_of_week=INTRO_T_CRON_DAY_OF_WEEK,
    #     hour=INTRO_T_CRON_HOUR,
    #     minute=INTRO_T_CRON_MINUTE,
    # )
    # scheduler.start()  # Start the scheduler

    # print("Scheduler started...")
    await bot.tree.sync()


@bot.event
async def on_message(message):
    if message.author == bot.user:
        return

    if message.guild is None:  # Check if the message is in a DM
        username = str(message.author)
        user_message = str(message.content)

        print(f"{username} said: {user_message} in {message.channel}")
        await send_message(message, user_message, is_private=True)


async def send_message(message=None, user_message=None, is_private=False):
    try:
        if is_private:
            # DM
            response = await responses.handle_DM_response(
                user_message=user_message, message=message
            )
            await message.channel.send(response)
        else:
            # is for the event top 3 questions
            response = await responses.handle_top_questions()
            return response

    except Exception as e:
        print(e)
        await message.channel.send("Algo salió mal. Inténtalo más tarde. :)")


# async def schedule_top_questions():
#     print("Scheduled job executed Top questions")
#     response = await send_message(is_private=False)

#     # Find the text channel within the category
#     category_id = int(os.environ.get("DISCORD_CATEGORY_CHANNEL_ID"))
#     # get the category channe
#     category = bot.get_channel(category_id)

#     print("CATEGORIA")
#     print(category)
#     print(
#         "There are "
#         + str(len(category.channels))
#         + " channels in the category: "
#         + category.name
#     )

    # Check if the category exists
    # if category:
    #     # Iterate through all text channels in the category
    #     for channel in category.channels:
    #         if isinstance(channel, discord.TextChannel):
    #             await channel.send(
    #                 "Estos son los top 3 temas de la semana: \n" + response
    #             )
    # else:
    #     print("Category channel not found.")


# Load introducing messages from the JSON file
# def get_introducing_messages():
#     with open("introducing_texts.json", "r") as file:
#         messages = json.load(file)
#     return messages


# Function to send a random introducing message to all users with the specified role
# async def send_introducing_message():
#     print("Scheduled job executed Introducing Messages")

#     # Find the text channel within the category
#     category_id = int(os.environ.get("DISCORD_CATEGORY_CHANNEL_ID"))
#     # get the category channe
#     category = bot.get_channel(category_id)

#     print("CATEGORIA")
#     print(category)
#     print(
#         "There are "
#         + str(len(category.channels))
#         + " channels in the category: "
#         + category.name
#     )

#     # Check if the category exists
#     if category:
#         # Get the list of messages
#         messages = get_introducing_messages()
#         random_message = random.choice(messages)
#         # Iterate through all text channels in the category
#         for channel in category.channels:
#             if isinstance(channel, discord.TextChannel):
#                 await channel.send(random_message["text"])
#     else:
#         print("Category channel not found.")


@bot.tree.command(
    name="brian",
    description="Solicita apoyo del bot brIAn para dudas de 28 cumbres",
)
@commands.guild_only()
async def slash_command(interaction: discord.Interaction):
    # send private message using the function
    channel = await bot.create_dm(interaction.user)
    # get the user's id
    user_id = interaction.user.id

    await channel.send(
        "Hola,"
        + "<@"
        + str(user_id)
        + ">"  # mention the user
        + ". Puedes preguntarme lo que desees saber. Si quieres saber cómo te puedo apoyar, escribe ayuda."
    )
    await interaction.response.send_message(
        "Hola, "
        + "<@"
        + str(user_id)
        + ">"
        + ". Te enviaré un mensaje privado para iniciar nuestra conversación, (recuerda que está en la barra de lado izquierdo)."
    )


# @bot.tree.command(name="top-3", description="Top 3 preguntas chidas ")
# @commands.guild_only()
# async def slash_command(interaction: discord.Interaction):
#   await interaction.response.defer()
#  response = await send_message(is_private=False)

# await interaction.followup.send(
#    "Estos son los top 3 temas de la semana: \n" + response
# )


TOKEN = os.environ.get("DISCORD_BOT_TOKEN")
bot.run(TOKEN)

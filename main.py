import discord
import os
from dotenv import load_dotenv
import requests
import json
import random
from replit import db
from keep_alive import keep_alive

# Load environment variables from .env file
load_dotenv()

# Define the intents
intents = discord.Intents.default()
intents.messages = True  # Enable message events
intents.message_content = True  # Enable reading message content

client = discord.Client(intents=intents)

# Define sad words and starter encouragements
sad_words = ["sad", "depressed", "unhappy", "angry", "miserable"]
starter_encouragements = ["Cheer up!", "Hang in there!", "Get over it lmao."]

if "responding" not in db.keys():
    db["responding"] = True

def get_quote():
    try:
        response = requests.get("https://zenquotes.io/api/random")
        json_data = json.loads(response.text)
        quote = json_data[0]['q'] + " - " + json_data[0]['a']
        return quote
    except Exception as e:
        print(f"Error fetching quote: {e}")
        return "Sorry, I couldn't fetch a quote at the moment."

def update_encouragements(encouraging_message):
    # Check if "encouragements" exists in the database
    if "encouragements" in db.keys():
        encouragements = list(db["encouragements"])  # Convert to list before modifying
        encouragements.append(encouraging_message)
        db["encouragements"] = encouragements
    else:
        db["encouragements"] = [encouraging_message]

def delete_encouragement(index):
    encouragements = list(db["encouragements"])  # Convert to list before modifying
    if len(encouragements) > index:
        del encouragements[index]
        db["encouragements"] = encouragements


@client.event
async def on_ready():
    print('We have logged in as {0.user}'.format(client))

@client.event
async def on_message(message):
    if message.author == client.user:
        return

    msg = message.content

    print(f"Received message: {message.content}")


    if db["responding"]: 
        options = starter_encouragements
        if "encouragements" in db.keys():
            options = options + list(db["encouragements"])  

        if any(word in msg.lower() for word in sad_words):  # Check for sad words
            await message.channel.send(random.choice(options))

    if msg.startswith("!new"):
        encouraging_message = msg.split("!new ", 1)[1]
        update_encouragements(encouraging_message)
        await message.channel.send("New encouraging message added.")

    if msg.startswith("!del"):
        if "encouragements" in db.keys():
            try:
                index = int(msg.split("!del ", 1)[1].strip())  
                delete_encouragement(index)
                encouragements = list(db["encouragements"])  
                await message.channel.send(f"Encouraging message deleted. Current list: {encouragements}")
            except (ValueError, IndexError):
                await message.channel.send("Invalid index for deletion.")

    if msg.startswith('!inspire'):  # Command for quotes
        quote = get_quote()
        await message.channel.send(quote)

    elif msg.startswith('!lol'):  
        await message.channel.send("420 blz it")

    elif msg.lower() == 'am i a programmer?':  # Command for the question
        await message.channel.send("Hell no.")

    elif msg.lower() == '!help':
        await message.channel.send("No one is going to help you.")

        

    # Handling !list command
    if msg.startswith("!list"):
        encouragements = []
        if "encouragements" in db.keys():
            encouragements = db["encouragements"]
        await message.channel.send(encouragements)

    # Handling !responding command
    if msg.startswith("!responding"):
        value = msg.split("!responding ", 1)[1]

        if value.lower() == "true":
            db["responding"] = True
            await message.channel.send("Responding is on.")
        else:
            db["responding"] = False
            await message.channel.send("Responding is off.")

keep_alive()
token = os.getenv('TOKEN')

if token is None:
    print("Error: TOKEN is not set in the environment variables.")
else:
    client.run(token)


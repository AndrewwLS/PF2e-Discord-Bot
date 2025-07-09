import logging
import requests
import json as js
import os
from dotenv import load_dotenv
import discord as ds
from discord.ext import commands 


HEADERS = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
                    "(KHTML, like Gecko) Chrome/114.0.0.0 Safari/537.36"
        }

def sheet_auth(user_id, json_code) :
    files = os.listdir("./charactersheets")

    for f in files :
        if json_code in f:
            parts = f.split('_')
            file_id = str(parts[1])
            file_json_code = str(parts[2])
            if file_id != str(user_id) and json_code == str(file_json_code) :
                return False
    else :
        return True

def pb_importer(pblink, savelink) :
    response = requests.get(pblink, headers=HEADERS)

    if response.status_code == 200 :                       
        with open(savelink, "w") as f :
            js.dump(response.json(), f)
        return True                 
    else :
        return False

def connect_handler() :
    # Importa toneken da .env
    load_dotenv()
    token = os.getenv('DISCORD_TOKEN')

    # Login handler
    handler = logging.FileHandler(filename = './log/discord.log', encoding = 'utf-8', mode = 'w')

    # Intenti
    intents = ds.Intents.default()
    intents.message_content = True
    intents.members = True

    # Prefisso
    bot = commands.Bot(command_prefix = '!', intents=intents)

    return token, handler, intents, bot, logging.DEBUG

def get_sheet(user_id) :
    files = os.listdir("./charactersheets")

    for f in files :
        if f.startswith(f"sheet_{user_id}_") :
            parts = f.split('_')
            with open(f"./charactersheets/sheet_{user_id}_{parts[2]}", "r") as f1: 
                data = js.load(f1)
                return data



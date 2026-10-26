import discord
import dotenv
from discord.ext import commands
import os


bot = commands.Bot()
dotenv.load_dotenv()
TOKEN = str(os.getenv("TOKEN"))

@bot.event
async def on_ready():
    print(f"{bot.user} is ready and online!")

bot.load_extension('cogs.debug')
bot.load_extension('cogs.musical')


bot.run(TOKEN)
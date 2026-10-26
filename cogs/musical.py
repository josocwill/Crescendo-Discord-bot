import discord
from discord.ext import commands
from gensound import Sine, Triangle, Sawtooth
from os import remove

songid = 0

def create_tune(songid, tune:str, bpm):
    res = Sine(tune, 0.5e3)
    res.export("tempmusic\\" + str(songid) + ".wav")

class Musical(commands.Cog):

    def __init__(self, bot):
        self.bot = bot

    @discord.slash_command(
        name="tune",
        description="Create a tune."
    )
    async def tune(self, ctx, tune, bpm="0.5e"):
        global songid
        songid += 1
        currentid = songid
        await ctx.respond(f"Generating tune...")
        create_tune(currentid, tune, bpm)
        await ctx.send(f"Here is your tune!", file=discord.File(f"tempmusic\\{currentid}.wav", "result.wav", description="This awesome tune was generated using crescendo bot by WillEnd."))
        remove(f"tempmusic\\{currentid}.wav")


def setup(bot):
    bot.add_cog(Musical(bot))
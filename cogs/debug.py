import discord
from discord.ext import commands

class Debug(commands.Cog):

    def __init__(self, bot):
        self.bot = bot

    @discord.slash_command(
        name="ping",
        description="Sends the bot's latency."
    )
    async def ping(self, ctx):
        await ctx.respond(f"Pong! Latency is {self.bot.latency} s")


def setup(bot):
    bot.add_cog(Debug(bot))
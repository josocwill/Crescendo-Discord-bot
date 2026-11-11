import discord
import dotenv
from discord.ext import commands
import os
import datetime


bot = commands.Bot()
dotenv.load_dotenv()
TOKEN = str(os.getenv("TOKEN"))

@bot.event
async def on_ready():
    print(f"{bot.user} is ready and online!")


bot.remove_command("help")

@bot.slash_command(
    name="help",
    description="A page with the basic help to start using crescendo!"
)
async def main(ctx:discord.Interaction):
    embed = discord.Embed(color=discord.Color.blurple(), title="Help page", description="This page explains how to use Crescendo!", footer=discord.EmbedFooter("Created with 🎶💖 by WillEnd"), thumbnail="https://cdn.discordapp.com/avatars/1564361193970212895/fb03cbd6997b44c0581137a8f16648d7.webp?size=4096", timestamp=datetime.datetime(2026, 11, 11))
    embed.add_field(name="Introduction", value="Crescendo is a discord bot that generates sound files using notes indicated in your message. The two main commands are **`/tune`** (which gets input directly from the message) and **`/filetune`** (which gets input from an attached text file, for longer texts).", inline=False)
    embed.add_field(name="Basic syntax", value="To create a tune you can input notes separated by spaces: `C D E F G A' B' C'`. You can also use sharps and flats: `C# Cb`. Crescendo is case sensitive!", inline=False)
    embed.add_field(name="Tempo syntax", value="You can also set the duration of notes in beats by specifying the duration before the note. Fractions and decimal numbers are allowed `2C 1/3C 0.5C`")
    embed.add_field(name="Rests", value="Rests can be added with the letter `R`. `C 2R C`")
    embed.add_field(name="Other help pages", value="`/modhelp` `/mischelp` [↪ Github wiki](https://github.com/josocwill/Crescendo-Discord-bot/wiki)")
    await ctx.respond(embed=embed)

@bot.slash_command(
    name="modhelp",
    description="How to use note modifiers"
)
async def mod(ctx:discord.Interaction):
    embed = discord.Embed(color=discord.Color.blurple(), title="Modifier help", description="How to use note modifiers", footer=discord.EmbedFooter("Created with 🧑‍💻💝 for Hack Club Crescent (go check it out!)"), thumbnail="https://cdn.discordapp.com/avatars/1564361193970212895/fb03cbd6997b44c0581137a8f16648d7.webp?size=4096", timestamp=datetime.datetime(2026, 11, 11))
    embed.add_field(name="Introduction", value="Modifiers are added after a note to modify its behavior. If added by themselves, they will modify all notes following. They can be stacked.")
    embed.add_field(name="Gain", value="The gain (or volume). Accepts decimal values and fractions. `Cg0.5` or `g0.5 C ...`. **Defaults to __1__**")
    embed.add_field(name="Wave", value="The wave type: can be any of `ws` for sine, `wq` for square, `wt` for triangle or `wh` for sawtooth. If no number is specified following the wave type, all waves will be muted except for the selected one, which will be set to volume **1**. If a number is specified, only the volume of that wave is going to be set to the desired number, this can be used to combine wave types.\n`Cwq` `Cwq0.5wt0.3` `wq0.5 wt0.3 C`", inline=False)
    embed.add_field(name="Tempo", value="The tempo from this moment on, set with `t`. This can't modify a single note. `t200 ...`")
    embed.add_field(name="Comment", value="Ignores EVERYTHING following it until the next space, including newlines, which can help make the score readable.\n> C D E FcBar1\n> G A' B' C'cBar2", inline=False)
    await ctx.respond(embed=embed)

@bot.slash_command(
    name="mischelp",
    description="Other features of the bot"
)
async def mischelp(ctx:discord.Interaction):
    embed = discord.Embed(color=discord.Color.blurple(), title="Misc help", description="Other features of the bot", footer=discord.EmbedFooter("Created while listening to some 🎶 I 💓"), thumbnail="https://cdn.discordapp.com/avatars/1564361193970212895/fb03cbd6997b44c0581137a8f16648d7.webp?size=4096", timestamp=datetime.datetime(2026, 11, 11))
    embed.add_field(name="Frequency", value="You can play an exact frequency instead of a note by writing `f123`, replacing `123` with the desired frequency. Accepts fractions and decimal values.")
    embed.add_field(name="Polyphony", value="Multiple notes can be played simultaneously by writing a `|` between them. `C | E | G`")
    embed.add_field(name="Polyrhythms", value="Notes can be grouped when played together by enclosing them in parentheses (`(` and `)`). This will treat whatever is in parentheses like a single note. Modifiers can't be applied DIRECTLY to the parentheses, they should be applied INSIDE the parentheses:\n```diff\n- (C D E F)g0.5\n+ (g0.5 C D E F)\n```\nThe main utility of grouping notes is to play multiple melodies at once. If melodies of different lengths are merged, the song will continue playing after the lengthier one has finished. `(C D E F G) | (E F G A' B')`", inline=False)
    await ctx.respond(embed=embed)

bot.load_extension('cogs.debug')
bot.load_extension('cogs.musical')


bot.run(TOKEN)
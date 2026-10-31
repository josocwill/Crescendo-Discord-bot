import discord
from discord.ext import commands
from gensound import Sine, Triangle, Sawtooth, Square, Silence, Signal
from os import remove
from random import choice
from typing import Literal
from time import time

songid = 0

QUOTES = open("assets/creation.txt", "r").readlines()
ERRORLINES = open("assets/errorlines.txt", "r").readlines()

def getnum(num:str) -> float:

    if "/" in num:
        if num.count("/") > 1:
            return -2.0
        return getnum(num.split("/")[0]) / getnum(num.split("/")[1])
    if num.count(".") > 1:
        return -1.0
    return float(num)

def formaterr(err:str):
    global ERRORLINES
    quote = choice(ERRORLINES)
    end = quote.index("|")
    if quote[end+1] == "+":
        return quote.replace("|+", "__" + err[0].capitalize() + err[1:] + "__")
    else:
        return quote.replace("|", "__" + err + "__")

class Musical(commands.Cog):

    def __init__(self, bot):
        self.bot = bot

    @discord.slash_command(
        name="tune",
        description="Create a tune."
    )
    async def tune(self, ctx, tune, bpm="120"):
        global songid, queue
        songid += 1
        currentid = songid
        
        t = time()
        await ctx.respond(f"""# {tune}
~~--------------------~~
-# BPM: **{bpm}**
-# Tunes generated since last offline: **{songid-1}**
-# Generation time: **`----- ms`**

## *{choice(QUOTES)[:-1]}*""")

        res = generate(tune, bpm)
        t = time() - t

        if res[0] == False:
            await ctx.edit(content=f"""# {tune}
~~--------------------~~
-# BPM: **{bpm}**
-# Tunes generated since last offline: **{songid-1}**
-# Generation time: **`{round(t*1000)} ms`**
{res[1]}
```diff
 {tune}
-{'~'*res[2]}^```""")
            
        else:
            res[1].export(f"tempmusic\\{currentid}.wav")
            await ctx.edit(content=f"""# {tune}
~~--------------------~~
-# BPM: **{bpm}**
-# Tunes generated since last offline: **{songid-1}**
-# Generation time: **`{round(t*1000)} ms`**""", file=discord.File(f"tempmusic\\{currentid}.wav", "result.wav", description="This awesome tune was generated using crescendo bot by WillEnd."))
            remove(f"tempmusic\\{currentid}.wav")


def setup(bot):
    bot.add_cog(Musical(bot))

def generate(tune:str, bpm:str, g=1.0, w=[1.0, 0.0, 0.0, 0.0]):
    try:
        # -> BPM number check

        try:
            resbpm = float(bpm)

        except ValueError:
            return (False, f"## {formaterr('''the tempo can't be __{} BPM__'''.format(bpm))}", -1) # ERROR! Invalid tempo error

        if resbpm <= 0:
            return (False, f"## {formaterr('''the tempo must be positive, not __{} BPM__'''.format(bpm))}", -1) # ERROR! Non-positive tempo error
        
        modifiers = {"freq":0, "duration":1.0, "w":w, "t":resbpm, "g":g}
        song = []
        currentnote = modifiers.copy()
        currentnum = ""
        merge = False
        """
        for c in range(len(tune)):

            if status == "GettingFrequency":
                if tune[c] in "234567890./":
                    currentnum += tune[c]
                else:
                    try:
                        if "/" in currentnum:
                            currentnote["freq"] = float(currentnum[:currentnum.index("/")])/float(currentnum[currentnum.index("/")+1:])
                        else:
                            currentnote["freq"] = float(currentnum)
                    except ValueError:
                        return (False, f"## {formaterr('''the frequency can't be __{} Hz__'''.format(currentnum))}", c) # ERROR! Invalid duration error
                    if currentnote["freq"] < 0:
                        return (False, f"## {formaterr('''the frequency can't be __{} Hz__'''.format(currentnum))}", c) # ERROR! Negative duration error

            if status == "GettingGroup":
                if tune[c] == "(":
                    parentheses += 1
                    continue
                if tune[c] == ")":
                    parentheses -= 1
                    if parentheses == 0:
                        grresult = generate(group, modifiers["t"], modifiers["g"], modifiers["w"])
                        if grresult[0]:
                            song += [grresult[1]]
                            continue
                        else:
                            return(False, grresult[1], grresult[2] + gstart) # ERROR! In a group
                group += tune[c]

            if status == "GettingGeneralGain":
                if tune[c] in "1234567890./":
                    currentnum += tune[c]
                else:
                    try:
                        if "/" in currentnum:
                            modifiers["g"] = float(currentnum[:currentnum.index("/")])/float(currentnum[currentnum.index("/")+1:])
                        else:
                            modifiers["g"] = float(currentnum)
                    except ValueError:
                        return (False, f"## {formaterr('''the tempo can't be __{} bpm__'''.format(currentnum))}", c) # ERROR! Invalid duration error
                    if modifiers["g"] < 0:
                        return (False, f"## {formaterr('''the tempo can't be __{} bpm__'''.format(currentnum))}", c)

            if status == "GettingGeneralWave":
                if tune[c] == "s":
                    status = "GettingGeneralSine"
                    continue

                if tune[c] == "h":
                    status = "GettingGeneralSawtooth"
                    continue

                if tune[c] == "q":
                    status = "GettingGeneralSquare"
                    continue

                if tune[c] == "t":
                    status = "GettingGeneralTriangle"
                    continue

                return (False, f"## {formaterr('''there is an unknown wave type **{}**, and it should be `s`, `h`, `q` or `t`'''.format(tune[c]))}", c) # ERROR! Invalid sine volume error

            if status == "GettingGeneralSine":
                if tune[c] in "1234567890./":
                    currentnote += tune[c]
                else:
                    try:
                        if "/" in currentnum:
                            modifiers["w"][0] = float(currentnum[:currentnum.index("/")])/float(currentnum[currentnum.index("/")+1:])
                        else:
                            modifiers["w"][0] = float(currentnum)
                    except ValueError:
                        return (False, f"## {formaterr('''the sine volume can't be __{}__x'''.format(currentnum))}", c) # ERROR! Invalid sine volume error
                    if modifiers["w"][0] < 0:
                        return (False, f"## {formaterr('''the sine volume can't be __{}__x'''.format(currentnum))}", c) # ERROR! Negative sine volume error
                continue

            if status == "GettingGeneralSawtooth":
                if tune[c] in "1234567890./":
                    currentnote += tune[c]
                else:
                    try:
                        if "/" in currentnum:
                            modifiers["w"][1] = float(currentnum[:currentnum.index("/")])/float(currentnum[currentnum.index("/")+1:])
                        else:
                            modifiers["w"][1] = float(currentnum)
                    except ValueError:
                        return (False, f"## {formaterr('''the sawtooth volume can't be __{}__x'''.format(currentnum))}", c) # ERROR! Invalid sawtooth volume error
                    if modifiers["w"][1] < 0:
                        return (False, f"## {formaterr('''the sawtooth volume can't be __{}__x'''.format(currentnum))}", c) # ERROR! Negative sawtooth volume error
                continue

            if status == "GettingGeneralSquare":
                if tune[c] in "1234567890./":
                    currentnote += tune[c]
                else:
                    try:
                        if "/" in currentnum:
                            modifiers["w"][2] = float(currentnum[:currentnum.index("/")])/float(currentnum[currentnum.index("/")+1:])
                        else:
                            modifiers["w"][2] = float(currentnum)
                    except ValueError:
                        return (False, f"## {formaterr('''the square volume can't be __{}__x'''.format(currentnum))}", c) # ERROR! Invalid square volume error
                    if modifiers["w"][2] < 0:
                        return (False, f"## {formaterr('''the square volume can't be __{}__x'''.format(currentnum))}", c) # ERROR! Negative square volume error
                continue

            if status == "GettingGeneralTriangle":
                if tune[c] in "1234567890./":
                    currentnote += tune[c]
                else:
                    try:
                        if "/" in currentnum:
                            modifiers["w"][3] = float(currentnum[:currentnum.index("/")])/float(currentnum[currentnum.index("/")+1:])
                        else:
                            modifiers["w"][3] = float(currentnum)
                    except ValueError:
                        return (False, f"## {formaterr('''the triangle volume can't be __{}__x'''.format(currentnum))}", c) # ERROR! Invalid triangle volume error
                    if modifiers["w"][1] < 0:
                        return (False, f"## {formaterr('''the triangle volume can't be __{}__x'''.format(currentnum))}", c) # ERROR! Negative triangle volume error
                continue

            if status == "GettingNoteGain":
                if tune[c] in "1234567890./":
                    currentnum += tune[c]
                else:
                    try:
                        if "/" in currentnum:
                            currentnote["g"] = float(currentnum[:currentnum.index("/")])/float(currentnum[currentnum.index("/")+1:])
                        else:
                            currentnote["g"] = float(currentnum)
                    except ValueError:
                        return (False, f"## {formaterr('''the tempo can't be __{} bpm__'''.format(currentnum))}", c) # ERROR! Invalid duration error
                    if currentnote["g"] < 0:
                        return (False, f"## {formaterr('''the tempo can't be __{} bpm__'''.format(currentnum))}", c)

            if status == "GettingNoteWave":
                if tune[c] == "s":
                    status = "GettingNoteSine"
                    continue

                if tune[c] == "h":
                    status = "GettingNoteSawtooth"
                    continue

                if tune[c] == "q":
                    status = "GettingNoteSquare"
                    continue

                if tune[c] == "t":
                    status = "GettingNoteTriangle"
                    continue

                return (False, f"## {formaterr('''there is an unknown wave type **{}**, and it should be `s`, `h`, `q` or `t`'''.format(tune[c]))}", c) # ERROR! Invalid sine volume error

            if status == "GettingNoteSine":
                if tune[c] in "1234567890./":
                    currentnote += tune[c]
                    continue
                else:
                    try:
                        if "/" in currentnum:
                            currentnote["w"][0] = float(currentnum[:currentnum.index("/")])/float(currentnum[currentnum.index("/")+1:])
                        else:
                            currentnote["w"][0] = float(currentnum)
                    except ValueError:
                        return (False, f"## {formaterr('''the sine volume can't be __{}__x'''.format(currentnum))}", c) # ERROR! Invalid sine volume error
                    if currentnote["w"][0] < 0:
                        return (False, f"## {formaterr('''the sine volume can't be __{}__x'''.format(currentnum))}", c) # ERROR! Negative sine volume error

            if status == "GettingNoteSawtooth":
                if tune[c] in "1234567890./":
                    currentnote += tune[c]
                    continue
                else:
                    try:
                        if "/" in currentnum:
                            currentnote["w"][1] = float(currentnum[:currentnum.index("/")])/float(currentnum[currentnum.index("/")+1:])
                        else:
                            currentnote["w"][1] = float(currentnum)
                    except ValueError:
                        return (False, f"## {formaterr('''the sawtooth volume can't be __{}__x'''.format(currentnum))}", c) # ERROR! Invalid sawtooth volume error
                    if currentnote["w"][1] < 0:
                        return (False, f"## {formaterr('''the sawtooth volume can't be __{}__x'''.format(currentnum))}", c) # ERROR! Negative sawtooth volume error

            if status == "GettingNoteSquare":
                if tune[c] in "1234567890./":
                    currentnote += tune[c]
                    continue
                else:
                    try:
                        if "/" in currentnum:
                            currentnote["w"][2] = float(currentnum[:currentnum.index("/")])/float(currentnum[currentnum.index("/")+1:])
                        else:
                            currentnote["w"][2] = float(currentnum)
                    except ValueError:
                        return (False, f"## {formaterr('''the square volume can't be __{}__x'''.format(currentnum))}", c) # ERROR! Invalid square volume error
                    if currentnote["w"][2] < 0:
                        return (False, f"## {formaterr('''the square volume can't be __{}__x'''.format(currentnum))}", c) # ERROR! Negative square volume error

            if status == "GettingNoteTriangle":
                if tune[c] in "1234567890./":
                    currentnote += tune[c]
                    continue
                else:
                    try:
                        if "/" in currentnum:
                            currentnote["w"][3] = float(currentnum[:currentnum.index("/")])/float(currentnum[currentnum.index("/")+1:])
                        else:
                            currentnote["w"][3] = float(currentnum)
                    except ValueError:
                        return (False, f"## {formaterr('''the triangle volume can't be __{}__x'''.format(currentnum))}", c) # ERROR! Invalid triangle volume error
                    if currentnote["w"][1] < 0:
                        return (False, f"## {formaterr('''the triangle volume can't be __{}__x'''.format(currentnum))}", c) # ERROR! Negative triangle volume error
            
            if status == "None":
                if tune[c] in "1234567890./": # Is a duration!
                    if currentnote["freq"] == 0:
                        currentnum += tune[c]
                    else:
                        return (False, f"## {formaterr('''there was an unexpected number''')}", c) # ERROR! Unexpected number

                if tune[c] == " ": # Is a new note!
                    try:
                        song += [currentnote["g"]*(currentnote["w"][0]*Sine(currentnote["freq"], currentnote["duration"]*60000/currentnote["t"]) +
                                currentnote["w"][1]*Sawtooth(currentnote["freq"], currentnote["duration"]*60000/currentnote["t"]) +
                                currentnote["w"][2]*Square(currentnote["freq"], currentnote["duration"]*60000/currentnote["t"]) +
                                currentnote["w"][3]*Triangle(currentnote["freq"], currentnote["duration"]*60000/currentnote["t"]))]
                    except:
                        return (False, f"## {formaterr('''an unknown error happened''')}", c) # UNKNOWN ERROR!!
                    currentnote = {"freq":0, "duration":1, "w":modifiers["w"], "t":modifiers["t"], "g":modifiers["g"]}
                    continue

                if tune[c] in "ABCDEFG": # Is a note!
                    currentnote["freq"] = {"A":440.0, "B":493.88, "C":523.25, "D":554.37, "E":659.26, "F":698.46, "G":783.99}[tune[c]]
                    if currentnum != "":
                        try:
                            if "/" in currentnum:
                                currentnote["duration"] = float(currentnum[:currentnum.index("/")])/float(currentnum[currentnum.index("/")+1:])
                            else:
                                currentnote["duration"] = float(currentnum)
                        except ValueError:
                            return (False, f"## {formaterr('''the duration can't be __{} beats__'''.format(currentnum))}", c) # ERROR! Invalid duration error
                        if currentnote["duration"] < 0:
                            return (False, f"## {formaterr('''the duration can't be __{} beats__'''.format(currentnum))}", c) # ERROR! Negative duration error
                    else:
                        currentnote["duration"] = 1.0
                    continue
                
                if tune[c] == "f": # Is a frequency!
                    status = "GettingFrequency"
                    if currentnum != "":
                        try:
                            if "/" in currentnum:
                                currentnote["duration"] = float(currentnum[:currentnum.index("/")])/float(currentnum[currentnum.index("/")+1:])
                            else:
                                currentnote["duration"] = float(currentnum)
                        except ValueError:
                            return (False, f"## {formaterr('''the duration can't be __{} beats__'''.format(currentnum))}", c) # ERROR! Invalid duration error
                        if currentnote["duration"] < 0:
                            return (False, f"## {formaterr('''the duration can't be __{} beats__'''.format(currentnum))}", c) # ERROR! Negative duration error
                    else:
                        currentnote["duration"] = 1.0
                    continue

                if tune[c] == "'": # Is a high octave!
                    currentnote["freq"] *= 2
                    continue

                if tune[c] == ",": # Is a low octave!
                    currentnote["freq"] /= 2
                    continue

                if tune[c] in ["s", "#"]: # Is a sharp!
                    currentnote["freq"] *= 2**(1/12)
                    continue

                if tune[c] in ["b"]: # Is a flat!
                    currentnote["freq"] /= 2**(1/12)
                    continue

                if tune[c] == "(": # Is a group start!
                    status = "GettingGroup"
                    parentheses = 1
                    group = ""
                    gstart = c
                    continue

                if tune[c] == "g":
                    currentnum = ""
                    if currentnote["freq"] == 0:
                        status = "GettingGeneralGain"
                    else:
                        status = "GettingNoteGain"
                    continue

                if tune[c] == "w":
                    currentnum = ""
                    if currentnote["freq"] == 0:
                        status = "GettingGeneralWave"
                    else:
                        status = "GettingNoteWave"
                    continue

                if tune[c] == "t":
                    currentnum = ""
                    if currentnote["freq"] == 0:
                        status = "GettingTempo"
                    else:
                        return (False, f"## {formaterr('''a tempo can't be assigned to a single note'''.format(currentnum))}") # ERROR! Tried to assign a tempo to a single note
                    continue
        
        note = 0
        splittune = tune.split(" ")
        group = 0
        merge = False
        song = []
        while note < len(splittune):
            phase = "duration"
            currentnum = ""
            currentnote = modifiers.copy()
            for c in splittune[note]:
                if phase == "generalgain":
                    if c in "1234567890./":
                        currentnum += c
                    else:
                        modifiers["g"] = getnum(currentnum)
                        if modifiers["g"] == -1.0:
                            return (False, "## " + formaterr("a number can't have two decimal points"), note) # ERROR! Multiple decimal points
                        elif modifiers["g"] == -2.0:
                            return (False, "## " + formaterr("a number can't be divided twice"), note) # ERROR! Multiple division
                        phase = "modifiers"

                elif phase == "generalgain":
                    if c in "1234567890./":
                        currentnum += c
                    else:
                        modifiers["g"] = getnum(currentnum)
                        if modifiers["g"] == -1.0:
                            return (False, "## " + formaterr("a number can't have two decimal points"), note) # ERROR! Multiple decimal points
                        elif modifiers["g"] == -2.0:
                            return (False, "## " + formaterr("a number can't be divided twice"), note) # ERROR! Multiple division
                        phase = "modifiers"      

                elif phase == "generalwave":
                    if c == "s":
                        phase = "generalsine"
                    elif c == "h":
                        phase = "generalsawtooth"
                    elif c == "q":
                        phase = "generalsquare"
                    elif c == "t":
                        phase = "generaltriangle"
                    else:
                        return (False, "## " + formaterr(f"{c} is an unknown wave type in note {note}"), note) # ERROR! Unknown wave type

                elif phase == "generalsine":
                    if c in "1234567890./":
                        currentnum += c
                    else:
                        modifiers["w"][0] = getnum(currentnum)
                        if modifiers["w"][0] == -1.0:
                            return (False, "## " + formaterr("a number can't have two decimal points"), note) # ERROR! Multiple decimal points
                        elif modifiers["w"][0] == -2.0:
                            return (False, "## " + formaterr("a number can't be divided twice"), note) # ERROR! Multiple division

                elif phase == "generalsawtooth":
                    if c in "1234567890./":
                        currentnum += c
                    else:
                        modifiers["w"][1] = getnum(currentnum)
                        if modifiers["w"][1] == -1.0:
                            return (False, "## " + formaterr("a number can't have two decimal points"), note) # ERROR! Multiple decimal points
                        elif modifiers["w"][1] == -2.0:
                            return (False, "## " + formaterr("a number can't be divided twice"), note) # ERROR! Multiple division

                elif phase == "generalsquare":
                    if c in "1234567890./":
                        currentnum += c
                    else:
                        modifiers["w"][2] = getnum(currentnum)
                        if modifiers["w"][2] == -1.0:
                            return (False, "## " + formaterr("a number can't have two decimal points"), note) # ERROR! Multiple decimal points
                        elif modifiers["w"][2] == -2.0:
                            return (False, "## " + formaterr("a number can't be divided twice"), note) # ERROR! Multiple division

                elif phase == "generaltriangle":
                    if c in "1234567890./":
                        currentnum += c
                    else:
                        modifiers["w"][3] = getnum(currentnum)
                        if modifiers["w"][3] == -1.0:
                            return (False, "## " + formaterr("a number can't have two decimal points"), note) # ERROR! Multiple decimal points
                        elif modifiers["w"][3] == -2.0:
                            return (False, "## " + formaterr("a number can't be divided twice"), note) # ERROR! Multiple division

                elif phase == "localsine":
                    if c in "1234567890./":
                        currentnum += c
                    else:
                        currentnote["w"][0] = getnum(currentnum)
                        if currentnote["w"][0] == -1.0:
                            return (False, "## " + formaterr("a number can't have two decimal points"), note) # ERROR! Multiple decimal points
                        elif currentnote["w"][0] == -2.0:
                            return (False, "## " + formaterr("a number can't be divided twice"), note) # ERROR! Multiple division
                        phase = "modifiers"

                elif phase == "localsawtooth":
                    if c in "1234567890./":
                        currentnum += c
                    else:
                        currentnote["w"][1] = getnum(currentnum)
                        if currentnote["w"][1] == -1.0:
                            return (False, "## " + formaterr("a number can't have two decimal points"), note) # ERROR! Multiple decimal points
                        elif currentnote["w"][1] == -2.0:
                            return (False, "## " + formaterr("a number can't be divided twice"), note) # ERROR! Multiple division
                        phase = "modifiers"

                elif phase == "localsquare":
                    if c in "1234567890./":
                        currentnum += c
                    else:
                        currentnote["w"][2] = getnum(currentnum)
                        if currentnote["w"][2] == -1.0:
                            return (False, "## " + formaterr("a number can't have two decimal points"), note) # ERROR! Multiple decimal points
                        elif currentnote["w"][2] == -2.0:
                            return (False, "## " + formaterr("a number can't be divided twice"), note) # ERROR! Multiple division
                        phase = "modifiers"

                elif phase == "localtriangle":
                    if c in "1234567890./":
                        currentnum += c
                    else:
                        currentnote["w"][3] = getnum(currentnum)
                        if currentnote["w"][3] == -1.0:
                            return (False, "## " + formaterr("a number can't have two decimal points"), note) # ERROR! Multiple decimal points
                        elif currentnote["w"][3] == -2.0:
                            return (False, "## " + formaterr("a number can't be divided twice"), note) # ERROR! Multiple division
                        phase = "modifiers"

                if phase == "duration":
                    if c in "1234567890./":
                        currentnum += c
                    elif c in "ACBDEFG":
                        if currentnum != "":
                            currentnote["duration"] = getnum(currentnum)
                            if currentnote["duration"] == -1.0:
                                return (False, "## " + formaterr("a number can't have two decimal points"), note) # ERROR! Multiple decimal points
                            elif currentnote["duration"] == -2.0:
                                return (False, "## " + formaterr("a number can't be divided twice"), note) # ERROR! Multiple division
                        currentnote["freq"] = {"A":440.0, "B":493.88, "C":523.25, "D":554.37, "E":659.26, "F":698.46, "G":783.99}[c]
                        currentnum = ""

                    elif c == "g":
                        currentnum = ""
                        phase = "generalgain"

                    elif c == "w":
                        currentnum = ""
                        phase = "generalwave"

                    elif c == "t":
                        currentnum = ""
                        phase = "tempo"

                    elif c == "|":
                        merge = True
                        phase = "comment"
                        
                    else:
                        return (False, "## " + formaterr(f"there is an unexpected character '**{c}**' in note {note+1}"), note) # ERROR! Unexpected character!

                elif phase == "modifiers":
                    
                    if c == ",":
                        currentnote["freq"] /= 2
                    
                    elif c == "'":
                        currentnote["freq"] *= 2

                    elif c == "b":
                        currentnote["freq"] /= 2**(1/12)

                    elif c in ["#", "s"]:
                        currentnote["freq"] *= 2**(1/12)

                    elif c == "g":
                        phase = "localgain"

                    elif c == "w":
                        phase = "localwave"

                    elif c == "c":
                        phase = "comment"

                    elif c == "(":
                        phase = "groupsearch"
                        break

                    else:
                        return (False, "## " + formaterr(f"there is an unexpected modifier '**{c}**' in note {note+1}"), note) # ERROR! Unexpected modifier!

                elif phase == "comment":
                    continue

            if phase == "groupsearch":
                
            
            song += [currentnote["w"][0]*currentnote["g"]*Sine(currentnote["freq"], currentnote["duration"]/currentnote["t"]*60000)+
                    currentnote["w"][1]*currentnote["g"]*Sawtooth(currentnote["freq"], currentnote["duration"]/currentnote["t"]*60000)+
                    currentnote["w"][2]*currentnote["g"]*Square(currentnote["freq"], currentnote["duration"]/currentnote["t"]*60000)+
                    currentnote["w"][3]*currentnote["g"]*Triangle(currentnote["freq"], currentnote["duration"]/currentnote["t"]*60000)]
            if merge:
                song[-2] += song.pop()"""
        c = 0
        phase = "duration"
        tune += " "
        while c < len(tune):
            if tune[c] == " " and phase == "modifiers": # New note
                currentnum = ""
                phase = "duration"

                if currentnote["freq"] > 0:
                    song += [currentnote["g"]*(currentnote["w"][0]*Sine(currentnote["freq"], currentnote["duration"]*60000/currentnote["t"])+ # type: ignore
                            currentnote["w"][1]*Sawtooth(currentnote["freq"], currentnote["duration"]*60000/currentnote["t"])+ # type: ignore
                            currentnote["w"][2]*Square(currentnote["freq"], currentnote["duration"]*60000/currentnote["t"])+ # type: ignore
                            currentnote["w"][3]*Triangle(currentnote["freq"], currentnote["duration"]*60000/currentnote["t"]))] # type: ignore

                if currentnote["freq"] != 0:
                    if merge:
                        if len(song) == 1:
                            return (False, "## " + formaterr("you can't merge nothing with something"), c)
                        song[-2] += song[-1]
                        song.pop()
                        merge = False 
                
                currentnote = modifiers.copy()

            elif phase == "duration":
                if tune[c] in "1234567890./":
                    currentnum += tune[c]

                elif tune[c] in "ABCDEFG":
                    currentnote["freq"] = {"A":440.0, "B":493.88, "C":523.25, "D":587.33, "E":659.26, "F":698.46, "G":783.99}[tune[c]]
                    phase = "modifiers"

                elif tune[c] == "R":
                    song += [Silence(currentnote["duration"]*60000/currentnote["t"])]
                    c += 1
                    if tune[c] != " ":
                        return (False, "## " + formaterr("a space was expected after a rest"), c) # ERROR! Unexpected character after rest
                    currentnum = ""
                    currentnote = modifiers.copy()
                    c += 1

                elif tune[c] == "f": phase = "freq"

                elif tune[c] == "g": phase = "globalgain"

                elif tune[c] == "t": phase = "temposet"

                elif tune[c:c+2] == "ws":
                    c += 1
                    phase = "globalsine"

                elif tune[c:c+2] == "wh":
                    c += 1
                    phase = "globalsawtooth"                

                elif tune[c:c+2] == "wq":
                    c += 1
                    phase = "globalsquare"

                elif tune[c:c+2] == "wt": 
                    c += 1
                    phase = "globaltriangle"

                elif tune[c] == "w":
                    return (False, "## " + formaterr("the wave type must be `ws`, `wh`, `wq` or `wt`, not **" + tune[c+1] + "**"), c) # ERROR! Unknown wave

                elif tune[c] == "c":
                    while tune[c] != " ":
                        c += 1
                    currentnum = ""

                elif tune[c] == "|":
                    merge = True
                    c += 2
                    continue

                elif tune[c] == "(":
                    parentheses = 1
                    group = ""
                    c += 1
                    start = c
                    while True:
                        if tune[c] == "(":
                            parentheses += 1
                        elif tune[c] == ")":
                            parentheses -= 1
                            if parentheses == 0:
                                break
                        group += tune[c]
                        c += 1

                    aux = generate(group, str(modifiers["t"]), modifiers["g"], modifiers["w"])
                    if aux[0] == True:
                        song += [aux[1]]
                        c += 1
                        currentnote["freq"] = -1.0
                        if tune[c] != " ":
                            return (False, "## " + formaterr("a space was expected after a group"), c) # ERROR! Unexpected non-space character after group
                        phase = "modifiers"
                        continue
                    else:
                        return (False, aux[1], start+aux[2])

                else: return (False, "## " + formaterr("there is an unexpected character (__`" + tune[c] + "`__)"), c) # ERROR! Unexpected character
                
                    
                if currentnum != "" and tune[c] not in "1234567890./":
                    currentnote["duration"] = getnum(currentnum)
                    if currentnote["duration"] == -1.0:
                        return (False, "## " + formaterr("a number can't have two decimal points"), c) # ERROR! Two decimal number
                    elif currentnote["duration"] == -2.0:
                        return (False, "## " + formaterr("a number can't have two fractions"), c) # ERROR! Two fraction number
                    currentnum = ""

            elif phase == "freq":
                if tune[c] in "0123456789./":
                    currentnum += tune[c]
                else:
                    currentnote["freq"] = getnum(currentnum)
                    if currentnote["freq"] == -1.0:
                        return (False, "## " + formaterr("a number can't have two decimal points"), c) # ERROR! Two decimal number
                    elif currentnote["freq"] == -2.0:
                        return (False, "## " + formaterr("a number can't have two fractions"), c) # ERROR! Two fraction number
                    phase = "modifiers"
                    continue

            elif phase == "globalgain":
                if tune[c] in "012345789./":
                    currentnum += tune[c]
                else:
                    modifiers["g"] = getnum(currentnum)
                    if modifiers["g"] == -1.0:
                        return (False, "## " + formaterr("a number can't have two decimal points"), c) # ERROR! Two decimal number
                    elif modifiers["g"] == -2.0:
                        return (False, "## " + formaterr("a number can't have two fractions"), c) # ERROR! Two fraction number
                    if tune[c] != " ":
                        return (False, "## " + formaterr("a space was expected after a global modifier, not **" + tune[c+1] + "**"), c) # ERROR! Unexpected non-space after global modifier
                    phase = "modifiers"
                    continue

            elif phase == "globalsine":
                if tune[c] in "012345789./":
                    currentnum += tune[c]
                elif currentnum != "":
                    modifiers["w"][0] = getnum(currentnum)
                    if modifiers["w"][0] == -1.0:
                        return (False, "## " + formaterr("a number can't have two decimal points"), c) # ERROR! Two decimal number
                    elif modifiers["w"][0] == -2.0:
                        return (False, "## " + formaterr("a number can't have two fractions"), c) # ERROR! Two fraction number
                    if tune[c] != " ":
                        return (False, "## " + formaterr("a space was expected after a global modifier, not **" + tune[c+1] + "**"), c) # ERROR! Unexpected non-space after global modifier
                    phase = "modifiers"
                    continue
                else:
                    modifiers["w"] = [1.0, 0.0, 0.0, 0.0]
                    if tune[c] != " ":
                        return (False, "## " + formaterr("a space was expected after a global modifier, not **" + tune[c+1] + "**"), c) # ERROR! Unexpected non-space after global modifier
                    phase = "modifiers"
                    continue

            elif phase == "globalsawtooth":
                if tune[c] in "012345789./":
                    currentnum += tune[c]
                elif currentnum != "":
                    modifiers["w"][1] = getnum(currentnum)
                    if modifiers["w"][1] == -1.0:
                        return (False, "## " + formaterr("a number can't have two decimal points"), c) # ERROR! Two decimal number
                    elif modifiers["w"][1] == -2.0:
                        return (False, "## " + formaterr("a number can't have two fractions"), c) # ERROR! Two fraction number
                    if tune[c] != " ":
                        return (False, "## " + formaterr("a space was expected after a global modifier, not **" + tune[c+1] + "**"), c) # ERROR! Unexpected non-space after global modifier
                    phase = "modifiers"
                    continue
                else:
                    modifiers["w"] = [0.0, 1.0, 0.0, 0.0]
                    if tune[c] != " ":
                        return (False, "## " + formaterr("a space was expected after a global modifier, not **" + tune[c+1] + "**"), c) # ERROR! Unexpected non-space after global modifier
                    phase = "modifiers"
                    continue

            elif phase == "globalsquare":
                if tune[c] in "012345789./":
                    currentnum += tune[c]
                elif currentnum != "":
                    modifiers["w"][2] = getnum(currentnum)
                    if modifiers["w"][2] == -1.0:
                        return (False, "## " + formaterr("a number can't have two decimal points"), c) # ERROR! Two decimal number
                    elif modifiers["w"][2] == -2.0:
                        return (False, "## " + formaterr("a number can't have two fractions"), c) # ERROR! Two fraction number
                    if tune[c] != " ":
                        return (False, "## " + formaterr("a space was expected after a global modifier, not **" + tune[c+1] + "**"), c) # ERROR! Unexpected non-space after global modifier
                    continue
                else:
                    modifiers["w"] = [0.0, 0.0, 1.0, 0.0]
                    if tune[c] != " ":
                        return (False, "## " + formaterr("a space was expected after a global modifier, not **" + tune[c+1] + "**"), c) # ERROR! Unexpected non-space after global modifier
                    phase = "modifiers"
                    continue

            elif phase == "globaltriangle":
                if tune[c] in "012345789./":
                    currentnum += tune[c]
                elif currentnum != "":
                    modifiers["w"][3] = getnum(currentnum)
                    if modifiers["w"][3] == -1.0:
                        return (False, "## " + formaterr("a number can't have two decimal points"), c) # ERROR! Two decimal number
                    elif modifiers["w"][3] == -2.0:
                        return (False, "## " + formaterr("a number can't have two fractions"), c) # ERROR! Two fraction number
                    if tune[c] != " ":
                        return (False, "## " + formaterr("a space was expected after a global modifier, not **" + tune[c+1] + "**"), c) # ERROR! Unexpected non-space after global modifier
                    continue
                else:
                    modifiers["w"] = [0.0, 0.0, 0.0, 1.0]
                    if tune[c] != " ":
                        return (False, "## " + formaterr("a space was expected after a global modifier, not **" + tune[c+1] + "**"), c) # ERROR! Unexpected non-space after global modifier
                    phase = "modifiers"
                    continue

            elif phase == "temposet":
                if tune[c] in "012345789./":
                    currentnum += tune[c]
                else:
                    modifiers["t"] = getnum(currentnum)
                    if modifiers["t"] == -1.0:
                        return (False, "## " + formaterr("a number can't have two decimal points"), c) # ERROR! Two decimal number
                    elif modifiers["t"] == -2.0:
                        return (False, "## " + formaterr("a number can't have two fractions"), c) # ERROR! Two fraction number
                    elif modifiers["t"] == 0.0:
                        return (False, "## " + formaterr("the tempo can't be set to 0 BPM"), c) # ERROR! Tempo set to zero
                    if tune[c] != " ":
                        return (False, "## " + formaterr("a space was expected after a global modifier, not **" + tune[c+1] + "**"), c) # ERROR! Unexpected non-space after global modifier
                    phase = "modifiers"
                    continue

            elif phase == "modifiers":
                if tune[c] == "g":
                    c += 1
                    phase = "localgain"
                elif tune[c:c+2] == "ws":
                    c += 2
                    phase = "localsine"
                elif tune[c:c+2] == "wh":
                    c += 2
                    phase = "localsawtooth"
                elif tune[c:c+2] == "wq":
                    c += 2
                    phase = "localsquare"
                elif tune[c:c+2] == "wt":
                    c += 2
                    phase = "localtriangle"
                elif tune[c] == "'": currentnote["freq"] *= 2
                elif tune[c] == ",": currentnote["freq"] /= 2
                elif tune[c] in "#s": currentnote["freq"] *= 2**(1/12)
                elif tune[c] == "b": currentnote["freq"] /= 2**(1/12)
                elif tune[c] == "w":
                    return (False, "## " + formaterr("the wave type must be `ws`, `wh`, `wq` or `wt`, not **" + tune[c+1] + "**"), c) # ERROR! Unknown wave
                elif tune[c] == "t":
                    return (False, "## " + formaterr("the tempo of a single note can't be set"), c) # ERROR! Attempted to set local tempo

            if phase == "localgain":
                if tune[c] in "012345789./":
                    currentnum += tune[c]
                else:
                    currentnote["g"] = getnum(currentnum)
                    if currentnote["g"] == -1.0:
                        return (False, "## " + formaterr("a number can't have two decimal points"), c) # ERROR! Two decimal number
                    elif currentnote["g"] == -2.0:
                        return (False, "## " + formaterr("a number can't have two fractions"), c) # ERROR! Two fraction number

                    phase = "modifiers"
                    continue

            elif phase == "localsine":
                if tune[c] in "012345789./":
                    currentnum += tune[c]
                elif currentnum != "":
                    currentnote["w"][0] = getnum(currentnum)
                    if currentnote["w"][0] == -1.0:
                        return (False, "## " + formaterr("a number can't have two decimal points"), c) # ERROR! Two decimal number
                    elif currentnote["w"][0] == -2.0:
                        return (False, "## " + formaterr("a number can't have two fractions"), c) # ERROR! Two fraction number
                    phase = "modifiers"
                    continue

                else:
                    currentnote["w"] = [1.0, 0.0, 0.0, 0.0]
                    phase = "modifiers"
                    continue

            elif phase == "localsawtooth":
                if tune[c] in "012345789./":
                    currentnum += tune[c]
                elif currentnum != "":
                    currentnote["w"][1] = getnum(currentnum)
                    if currentnote["w"][1] == -1.0:
                        return (False, "## " + formaterr("a number can't have two decimal points"), c) # ERROR! Two decimal number
                    elif currentnote["w"][1] == -2.0:
                        return (False, "## " + formaterr("a number can't have two fractions"), c) # ERROR! Two fraction number
                    phase = "modifiers"
                    continue
            
                else:
                    currentnote["w"] = [0.0, 1.0, 0.0, 0.0]
                    phase = "modifiers"
                    continue

            elif phase == "localsquare":
                if tune[c] in "012345789./":
                    currentnum += tune[c]
                elif currentnum != "":
                    currentnote["w"][2] = getnum(currentnum)
                    if currentnote["w"][2] == -1.0:
                        return (False, "## " + formaterr("a number can't have two decimal points"), c) # ERROR! Two decimal number
                    elif currentnote["w"][2] == -2.0:
                        return (False, "## " + formaterr("a number can't have two fractions"), c) # ERROR! Two fraction number
                    phase = "modifiers"
                    continue

                else:
                    currentnote["w"] = [0.0, 0.0, 1.0, 0.0]
                    phase = "modifiers"
                    continue

            elif phase == "localtriangle":
                if tune[c] in "012345789./":
                    currentnum += tune[c]
                elif currentnum != "":
                    currentnote["w"][3] = getnum(currentnum)
                    if currentnote["w"][3] == -1.0:
                        return (False, "## " + formaterr("a number can't have two decimal points"), c) # ERROR! Two decimal number
                    elif currentnote["w"][3] == -2.0:
                        return (False, "## " + formaterr("a number can't have two fractions"), c) # ERROR! Two fraction number
                    phase = "modifiers"
                    continue

                else:
                    currentnote["w"] = [0.0, 0.0, 0.0, 3.0]
                    phase = "modifiers"
                    continue
            c += 1
        result = song[0]
        for i in song[1:]:
            result |= i

        return (True, 0.5*result)
    except Exception as e:
        return(False, "## " + formaterr("an unexpected exception happened"), c) # ERROR! Unexpected
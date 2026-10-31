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
    if num == "": return 1
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
                    song += [Silence(getnum(currentnum)*60000/currentnote["t"])]
                    c += 1
                    if tune[c] != " ":
                        return (False, "## " + formaterr("a space was expected after a rest"), c) # ERROR! Unexpected character after rest
                    currentnum = ""
                    currentnote = modifiers.copy()

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
                if tune[c] in "0123456789./":
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
                if tune[c] in "0123456789./":
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
                if tune[c] in "0123456789./":
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
                if tune[c] in "0123456789./":
                    currentnum += tune[c]
                elif currentnum != "":
                    modifiers["w"][2] = getnum(currentnum)
                    if modifiers["w"][2] == -1.0:
                        return (False, "## " + formaterr("a number can't have two decimal points"), c) # ERROR! Two decimal number
                    elif modifiers["w"][2] == -2.0:
                        return (False, "## " + formaterr("a number can't have two fractions"), c) # ERROR! Two fraction number
                    if tune[c] != " ":
                        return (False, "## " + formaterr("a space was expected after a global modifier, not **" + tune[c+1] + "**"), c) # ERROR! Unexpected non-space after global modifier
                    phase = "modifiers"
                    continue
                else:
                    modifiers["w"] = [0.0, 0.0, 1.0, 0.0]
                    if tune[c] != " ":
                        return (False, "## " + formaterr("a space was expected after a global modifier, not **" + tune[c+1] + "**"), c) # ERROR! Unexpected non-space after global modifier
                    phase = "modifiers"
                    continue

            elif phase == "globaltriangle":
                if tune[c] in "0123456789./":
                    currentnum += tune[c]
                elif currentnum != "":
                    modifiers["w"][3] = getnum(currentnum)
                    if modifiers["w"][3] == -1.0:
                        return (False, "## " + formaterr("a number can't have two decimal points"), c) # ERROR! Two decimal number
                    elif modifiers["w"][3] == -2.0:
                        return (False, "## " + formaterr("a number can't have two fractions"), c) # ERROR! Two fraction number
                    if tune[c] != " ":
                        return (False, "## " + formaterr("a space was expected after a global modifier, not **" + tune[c+1] + "**"), c) # ERROR! Unexpected non-space after global modifier
                    phase = "modifiers"
                    continue
                else:
                    modifiers["w"] = [0.0, 0.0, 0.0, 1.0]
                    if tune[c] != " ":
                        return (False, "## " + formaterr("a space was expected after a global modifier, not **" + tune[c+1] + "**"), c) # ERROR! Unexpected non-space after global modifier
                    phase = "modifiers"
                    continue

            elif phase == "temposet":
                if tune[c] in "0123456789./":
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
                if tune[c] in "0123456789./":
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
                if tune[c] in "0123456789./":
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
                if tune[c] in "0123456789./":
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
                if tune[c] in "0123456789./":
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
                if tune[c] in "0123456789./":
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
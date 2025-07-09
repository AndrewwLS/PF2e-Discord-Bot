import asyncio
import utils.sheets_util as sus
import utils.dice_util as dus
import discord as ds

EMBED_FOOTER = "Pf2e - Helper ver 0.1 PreBeta"
STANDARD_FIELD = {
    "name": "Come iniziare",
    "value": "Scrivi `!help`",
    "inline": False
}

token, handler, intents, bot, log_level = sus.connect_handler() # Connect Handler

@bot.event
async def on_ready() :
    print(f"====== {bot.user.name} ======")
    print("Bot for Pf2e integration")
    print("on discord")
    print("Created By: Andrea Leone")
    print("Version 0.2-prebeta")
    print("=========================")

@bot.event
async def on_message(message) :
    """
    Manda un messaggio di risposta a chi mette ciao
    """
    # Ignores bot message
    if message.author == bot.user :
        return

    if "ciao" in message.content.lower() :
        await message.channel.send  (f"Sapevo che avresti scritto ciao" 
                                    "{message.author.mention}, adesso procederò"
                                    "a tagliarti lo scroto")

    await bot.process_commands(message) # Overrides message

@bot.command()
async def links(ctx) :
    """

    """
    await ctx.message.delete()
    await ctx.channel.send(f"Link mandati in DM! {ctx.author.mention}")
    embed = ds.Embed (
        title = "Link Utili ",
        description =   "Manuale completo pf2e:\n"
                        "https://2e.aonprd.com/?AspxAutoDetectCookieSupport=1\n\n"
                        "Dove fare la scheda personaggio:\n"
                        "https://pathbuilder2e.com/app.html?v=95a\n\n",
        color = ds.Color.dark_gold()
    )
    embed.set_footer(text=EMBED_FOOTER)
    embed.add_field(name="Come iniziare", value="Scrivi `!help`", inline=False)
    await ctx.author.send(embed = embed)

@bot.command()
async def importsheet(ctx, *, json_code: str) :
    """
    Comando per importare la scheda da pathbuilder
    Utilizza il comando !importsheet seguito dal codice
    json della tua scheda per ricevere aggiornare una scheda
    esistente o salvarne una nuova. 
    Per informazioni aggiuntive segui la guida a [link]
    """
    if len(json_code) != 6 :
        await ctx.author.send (f"Il codice Json è un codice di esattamente 6 caratteri!\n"
                                "il Json da te inserito è {json_code}\n"
                                "Prova a cercare un codice di questo tipo:")
        await ctx.author.send(file = ds.File("./images/json_example.png"))
        return
    else :
        # Confirmation
        json_confirm = await ctx.send(f"Il tuo codice json è {json_code}, confermi?")

        await json_confirm.add_reaction("✅")
        await json_confirm.add_reaction("❌")

        def check(reaction, user):
            return user == ctx.author and str(reaction.emoji) in ["✅", "❌"] and reaction.message.id == json_confirm.id
    
        try :
            reaction, user = await bot.wait_for('reaction_add', timeout = 30.0, check = check)

            if str(reaction.emoji) == "✅" :
                await json_confirm.delete()
                sheet_path = f"./charactersheets/sheet_{ctx.author.id}_{json_code}"

                # await ctx.send(link)
                progress = await ctx.channel.send   (content=". . . Autenticazione . . .\n"
                                                    "[==-       ] 25%")
                if sus.sheet_auth(ctx.author.id, json_code) :
                    await progress.edit (content=". . . Salvataggio file dump . . .\n"
                                        "[=====     ] 50%")
                    if sus.pb_importer(f"https://pathbuilder2e.com/json.php?id={json_code}", sheet_path) :
                        await progress.edit (content=". . . Finalizzazione . . .\n"
                                            "[=======-  ] 75%")
                        data = sus.get_sheet(ctx.author.id)
                        if data != None :
                            await progress.edit (content=f"{data["build"]["name"]} è stato creato/aggiornato\n"
                                            "[==========] 100%")
                            await asyncio.wait(5)
                            await progress.delete()
                    else :
                        await progress.edit (content="Errore nell'importazione")
                        await asyncio.wait(5)
                        await progress.delete()
                else : 
                    await progress.edit (content="Errore di Autenticazione, contatta uno "
                                        "staffer se credi sia stato uno sbaglio")
                    await asyncio.wait(5)
                    await progress.delete()
                    
            elif str(reaction.emoji) == "❌" :
                await json_confirm.delete()
                await ctx.channel.send("Procedura annullata")
                await asyncio.sleep(5)
                await ctx.delete()

        except asyncio.TimeoutError :
            await ctx.author.send("Hai impiegato troppo tempo a rispondere")
        # end of confermation

@bot.command()
async def sheet(ctx) :
    data = sus.get_sheet(ctx.author.id)
    if data != None :
        embed = ds.Embed (
            title = f"LV: {data["build"]["level"]} - {data["build"]["name"]} - {data["build"]["class"]}",
            description =   "=== Statistiche ===\n"
                            f"Forza: {data["build"]["abilities"]["str"]}\n"
                            f"Destrezza: {data["build"]["abilities"]["dex"]}\n"
                            f"Costituzione: {data["build"]["abilities"]["con"]}\n"
                            f"Intelligenza: {data["build"]["abilities"]["int"]}\n"
                            f"Saggezza: {data["build"]["abilities"]["wis"]}\n"
                            f"Carisma: {data["build"]["abilities"]["cha"]}\n"
                            "==================",
        )
        embed.set_author(name = f"Scheda di: {ctx.author}")
        embed.set_footer(text = EMBED_FOOTER)
        embed.add_field(**STANDARD_FIELD)
        await ctx.send(embed = embed)
    else :
        error = await ctx.channel.send("Scheda non trovata")
        await asyncio.sleep(5)
        await error.delete()

@bot.command()
async def roll(ctx, ability: str, hidden : str = "") :
    data = sus.get_sheet(ctx.author.id) # Recupero Scheda
    await ctx.message.delete()

    if data != None:
        base_ability, total_mod = dus.get_ext_mod(ability) # Divisione tra Modificatori e Abilità
        result, dice, modifier, other_mods,  = dus.ability_roll(base_ability, data, total_mod)
        
        # Controllo errore
        if "errore" in result.lower() :
            error = await ctx.channel.send(result)
            await asyncio.sleep(5)
            await error.delete()
            return
        
        # Set colore embed su critici
        if dice == "**1**" :
            color = ds.Color.red()
        elif dice == "**20**" :
            color = ds.Color.green()
        else :
            color = ds.Color.blue()

        #Creazione embed
        embed = ds.Embed (
            title = f"Prova di {base_ability.capitalize()} di {data["build"]["name"]} = {result}",
            description = f"Dado ( {dice} ) + Modificatore ( {modifier} ) + Altro ( {other_mods} )",
            color = color
        )

        if (hidden == "-h") :
            await ctx.author.send(embed = embed)
        else :
            await ctx.channel.send(embed = embed)
    
    else :
        error = await ctx.channel.send("Scheda non trovata")
        await asyncio.sleep(5)
        await error.delete()

@bot.command()
async def level(ctx) :
    await ctx.send("Gay")

bot.run(token, log_handler = handler, log_level = log_level)

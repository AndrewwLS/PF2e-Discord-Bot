import random as rn
import re

def get_stat_value(data, ability) :
    
    ability = ability.lower()
    level = int(data["build"]["level"])
    unt_imp = 0

    # Ricerca di Untrained Improvisation
    target = "Untrained Improvisation"
    for feat in data["build"]["feats"] :
        if target in feat :
            if level < 4 :
                unt_imp = level-2
            elif level < 6 :
                unt_imp = level-1
            else :
                unt_imp = level
            break

    if ability.startswith("lore") :
        split = ability.split(" ")
        for lore in data["build"]["lores"] :
            if lore[0].lower() == split[1] :
                ability = int(lore[1])+int((data["build"]["abilities"]["int"]-10)//2)+level
    try :         
        if int(data["build"]["proficiencies"][ability]) == 0 :
            level = 0
        else :
            unt_imp = 0
    except :
        error = "Errore: abilità inserita inesistente"
        return error


    mappa_stats = {
        # Mappatura Forza
        "athletics" :   (int(data["build"]["proficiencies"]["athletics"])+
                        int((data["build"]["abilities"]["str"]-10)//2)),
        
        # Mappatura Destrezza
        "reflex" : (int(data["build"]["proficiencies"]["reflex"])+
                        int((data["build"]["abilities"]["dex"]-10)//2)),

        "acrobatics" : (int(data["build"]["proficiencies"]["acrobatics"])+
                        int((data["build"]["abilities"]["dex"]-10)//2)),

        "stealth" : (int(data["build"]["proficiencies"]["stealth"])+
                    int((data["build"]["abilities"]["dex"]-10)//2)),

        "thievery" : (int(data["build"]["proficiencies"]["thievery"])+
                    int((data["build"]["abilities"]["dex"]-10)//2)),

        # Mappatura Costituzione
        "fortitude" : (int(data["build"]["proficiencies"]["fortitude"])+
                    int((data["build"]["abilities"]["con"]-10)//2)),

        # Mappatura Intelligenza
        "arcana" : (int(data["build"]["proficiencies"]["arcana"])+
                    int((data["build"]["abilities"]["int"]-10)//2)),
        
        "crafting" : (int(data["build"]["proficiencies"]["crafting"])+
                    int((data["build"]["abilities"]["int"]-10)//2)),
        
        "occultism" : (int(data["build"]["proficiencies"]["occultism"])+
                    int((data["build"]["abilities"]["int"]-10)//2)),
        
        "society" : (int(data["build"]["proficiencies"]["society"])+
                    int((data["build"]["abilities"]["int"]-10)//2)),

        # Sezione Saggezza
        "will" : (int(data["build"]["proficiencies"]["will"])+
                    int((data["build"]["abilities"]["wis"]-10)//2)),

        "perception" : (int(data["build"]["proficiencies"]["perception"])+
                    int((data["build"]["abilities"]["wis"]-10)//2)),

        "medicine" : (int(data["build"]["proficiencies"]["medicine"])+
                    int((data["build"]["abilities"]["wis"]-10)//2)),
        
        "nature" : (int(data["build"]["proficiencies"]["nature"])+
                    int((data["build"]["abilities"]["wis"]-10)//2)),

        "religion" : (int(data["build"]["proficiencies"]["religion"])+
                    int((data["build"]["abilities"]["wis"]-10)//2)),

        "survival" : (int(data["build"]["proficiencies"]["survival"])+
                    int((data["build"]["abilities"]["wis"]-10)//2)),

        # Sezione Carisma
        "deception" : (int(data["build"]["proficiencies"]["deception"])+
                    int((data["build"]["abilities"]["cha"]-10)//2)),

        "diplomacy" : (int(data["build"]["proficiencies"]["diplomacy"])+
                    int((data["build"]["abilities"]["cha"]-10)//2)),
        
        "intimidation" : (int(data["build"]["proficiencies"]["intimidation"])+
                    int((data["build"]["abilities"]["cha"]-10)//2)),

        "performance" : (int(data["build"]["proficiencies"]["performance"])+
                    int((data["build"]["abilities"]["cha"]-10)//2)),
    }

    return mappa_stats.get(ability, 0) + level + unt_imp 

def get_ext_mod(ability) :
    # Estrazione parte letterale
    base_match = re.match(r"[a-zA-Z]+", ability)
    base_ability = base_match.group(0).lower() if base_match else ability.lower()

    # Trova tutti i modificatori sulla stringa originale (non su base_ability)
    mods = re.findall(r"[+-]\d+", ability)

    # Somma tutti i modificatori
    total_mod = sum(int(m) for m in mods)

    return base_ability, total_mod

def ability_roll(ability, data, other_mods) :
    ability = ability.lower() # Rende ability tutto minuscolo
    dice = rn.randint(1, 20) # Tiro di dado
    bold = "" # Var di supporto
    
    # Check per il critico
    if dice == 1 or dice == 20 :
        bold = "**"

    
    modifier = get_stat_value(data, ability)
    if isinstance(modifier, str):
        return modifier

    other_mods = int(other_mods) # Mod aggiuntivi esterni

    if other_mods != 0 : # Tiro senza mod esterni
        result = int(dice+modifier+other_mods)
        dice = f"{bold}{str(dice)}{bold}"
        modifier = f"{str(modifier)}"
        other_mods = f"{str(other_mods)}"   
    else : # Tiro con mod esterni
        result = int(dice+modifier+other_mods)
        dice = f"{bold}{str(dice)}{bold}"
        modifier = f"{str(modifier)}"
        other_mods = f"{str(other_mods)}" 

    return str(f"[{result}]"), str(dice), str(modifier), str(other_mods)



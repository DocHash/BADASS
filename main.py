from pathlib import Path
import json


import logging                                                                                              #DEBUG
logging.basicConfig(level=logging.DEBUG)                                                                    #DEBUG


ROOT_DIR = Path(__file__).parent
MODS_MANAGER_ROOT_DIR = ROOT_DIR.parent
SPID_EXTENSION = "_DISTR.ini"
FILES = ["AA_keywords", "items", "perks", "spells"]
SUPPORTED_MODS = ["Apocalypse - Magic of Skyrim.esp", "Arcanum.esp", "Astral.esl", "StormCalling.esl"]
SPID_SKILLS = ["OneHanded", "TwoHanded", "Marksman", "Block", "Smithing", "HeavyArmor", "LightArmor", "Pickpocket", "Lockpicking", "Sneak", "Alchemy", "Speechcraft", "Alteration", "Conjuration", "Destruction", "Illusion", "Restoration", "Enchanting"]
ALL_RANKS = ["novice", "apprentice", "adept", "expert", "master"]
DISTRIBUTION_CHANCE = {"spells": {"for_required_rank": 40, "per_higher_rank": 10}}


user_modpath_list = []
output_DISTR = []



for file in FILES:

    filename = (ROOT_DIR / f"{file}{SPID_EXTENSION}")
    version = 0

    while (filename).exists():
        logging.debug(f"{filename} existe ==> VERSION DE FICHIER SPID + 1")                                 #DEBUG
        version += 1
        filename = (ROOT_DIR / f"{file}v{version}{SPID_EXTENSION}")

    logging.debug(f"{filename} n'existe pas ==> CREER FICHIER SPID CORRESPONDANT")                          #DEBUG



print(" ")                                                                                                  #DEBUG


# 1. parser les dossiers de ROOT_DIR pour chercher les mods ajoutant du contenu a injecter via SPID :

for mod in SUPPORTED_MODS:

    for found_modpath in MODS_MANAGER_ROOT_DIR.rglob(mod):

        logging.debug(f"Chemin identifié : {found_modpath}")                                                #DEBUG

        if found_modpath.parent.parent == MODS_MANAGER_ROOT_DIR:
            user_modpath_list.append(found_modpath)
            logging.debug(f"Chemin valide pour le mod {mod} : {found_modpath}. Ajout à user_modlist")       #DEBUG

        else:                                                                                               #DEBUG
            logging.debug(f"Chemin non valide pour le mod {mod} : {found_modpath}. Non ajouté")             #DEBUG

        print(" ")                                                                                          #DEBUG


# SOLUTIONS ALTERNATIVES :

# for mod_dir in ROOT_DIR.iterdir():
    # mods_found = [mod for mod in MODS if (ROOT_DIR / mod_dir / mod).exists()]

# for mod in MODS:
#     mod_path = [file for file in ROOT_DIR.rglob(mod) if file.name == mod and file.parent.parent == ROOT_DIR]



logging.debug(f"Modlist détectée pour l'utilisateur : {user_modpath_list}")                                 #DEBUG
print(" ")                                                                                                  #DEBUG



# 2. updater les fichiers JSON avec la liste de spells ajoutés par des mods injectables via SPID et le nombre de spells par palier :

with open((ROOT_DIR / "archetypes_test.json"), "r") as user_archetypes:                 # Chargement des données des fichiers archetypes.json et spells.json
    ARCHETYPES = json.load(user_archetypes)

with open((ROOT_DIR / "spells_test.json"), "r") as user_spells:
    SPELLS = json.load(user_spells)


for archetype in ARCHETYPES:

    for rank in ARCHETYPES[archetype]["spells_by_rank"]:
        ARCHETYPES[archetype]["spells_by_rank"][rank] = 0                               # Remise à zéro de tous les paliers pour chaque archétype dans archetypes.json
        logging.debug(f"Rang {rank} remis à zéro pour l'archétype {archetype}.")                            #DEBUG

    print(" ")                                                                                              #DEBUG

    # for spell in ARCHETYPES[archetype].get("spells"):
    for spell in ARCHETYPES[archetype]["spells"]:

        rank = SPELLS[spell]["rank"]
        mod = SPELLS[spell]["mod"]

        if archetype not in SPELLS[spell]["archetypes"]:
            SPELLS[spell]["archetypes"].append(archetype)                               # Update des archétypes pour chaque spell dans spells.json
            logging.debug(f"Archétype {archetype} ajouté au sort {spell}.")                                 #DEBUG


        if mod in [user_mod.name for user_mod in user_modpath_list]:
            ARCHETYPES[archetype]["spells_by_rank"][rank] += 1                          # Update du nombre de spells par palier pour chaque archétype dans archetypes.json si spell venant d'un mod dans la user_modlist
            logging.debug(f"{spell} : Palier {rank} incrémenté de 1 pour l'archétype {archetype}.")         #DEBUG

        else:                                                                           # Pas d'incrémentation du nombre de spells si spell venant d'un mod pas dans la user_modlist détectée
            logging.debug(f"{mod} pas dans user_modlist. Palier {rank} non incrémenté pour {archetype}.")   #DEBUG

    print(" ")                                                                                              #DEBUG


with open((ROOT_DIR / "archetypes_test.json"), "w") as user_archetypes:                 # Sauvegarde des updates dans les fichiers archetypes.json et spells.json
    json.dump(ARCHETYPES, user_archetypes, indent=4)

with open((ROOT_DIR / "spells_test.json"), "w") as user_spells:
    json.dump(SPELLS, user_spells, indent=4)

# CHANGER LES NOMS DE FICHIERS xxx_TEST.JSON EN xxx.JSON POUR SPELLS/ARCHETYPES (VOIRE LES GROUPER DANS UN SEUL FICHIER PARAMETRES OU USER SETTINGS) +/- CREER UNE LISTE DE FICHIERS COMME POUR CONSTANTE FILES ?
# PREVOIR UNE OPTION POUR REMETTRE LES LISTES DE SPELLS DE SPELLS.JSON A ZERO ( SPELLS[spell]["archetypes"] = [] )



# 3. récupère le contenu updaté des fichiers JSON et adapte les % d'injection par archétype selon niveau (Lv), niveau du skill (LvSk), nombre de spells dispos par palier pour l'archetype

for spell in SPELLS:                                                                    # Processus réalisé pour chaque spell enregistré dans le fichier spells.json

    mod = SPELLS[spell]["mod"]

    if mod in [user_mod.name for user_mod in user_modpath_list]:                        # On vérifie que le spell appartient à un mod supporté et dans la modlist de l'utilisateur

        form_id = SPELLS[spell]["form_id"]                                              # Récupération des paramètres utiles enregistrés dans le fichier spells.json
        archetypes = SPELLS[spell]["archetypes"]
        school = SPELLS[spell]["school"]
        rank = SPELLS[spell]["rank"]
        description = SPELLS[spell]["description"]
                                                                                        # Entete avec les infos de chaque spell pour classer output par spell
        output_DISTR.append(f";==================== {spell.upper()} ({mod}) [{school.capitalize()} - {rank}] ====================\n;DESCRIPTION: {description}\n")
                                                                                        # Transformation des paramètres textuels en valeurs comprises par SPID (NB : alternativement school_value pourrait etre récupérée par l'index dans la variable globale SPID_SKILLS (= liste comprenant tous les skills avec index = leur numéro correspondant dans SPID))
        school_value = 12 if school == "alteration" else 13 if school == "conjuration" else 14 if school == "destruction" else 15 if school == "illusion" else 16 if school == "restoration" else ""
        required_level = 35 if rank == "master" else 25 if rank == "expert" else 16 if rank == "adept" else 8 if rank == "apprentice" else 1

        # for archetype in SPELLS[spell]["archetypes"]:                                                                 SOLUTION ALTERNATIVE
        for archetype in archetypes:                                                    # Processus réalisé pour chaque archétype (pour chaque spell) enregistré dans spells.json
                                                                                        # Calcul des probabilités de distribution de base (global = 40%) + incrémentation par palier (+10%/palier) en fonction du nombre de spells de chaque palier et pour chaque archétype
            rank_value = 90 if rank == "master" else 65 if rank == "expert" else 40 if rank == "adept" else 15 if rank == "apprentice" else 0
            spell_by_rank = ARCHETYPES[archetype]["spells_by_rank"][rank]
            distribution_chance = round((DISTRIBUTION_CHANCE["spells"]["for_required_rank"] / spell_by_rank), 1) if spell_by_rank !=0 else 0
            incremental_distribution_chance = round((DISTRIBUTION_CHANCE["spells"]["per_higher_rank"] / spell_by_rank), 1) if spell_by_rank !=0 else 0
            increment_cycles = len(ALL_RANKS) - ALL_RANKS.index(rank) - 1               # Calcul du nombre de cycles d'incrémentation pour la distribution

            while increment_cycles >= 0:                                                # Cycles de distribution = fait apparaitre le spell a partir d'un certain level + skill level dans l'école correspondante, et sa probabilité augmente ensuite avec le skill level uniquement
                max_rank = rank_value + 24 if rank_value > 0 else rank_value + 14       # Permet d'afficher les bornes supérieures de chaque palier sauf quand on arrive au niveau master de distribution (cf ligne infra)
                output_DISTR.append(f"Spell = {form_id}~{mod}|{archetype}|NONE|{required_level},{school_value}({rank_value}{f'/{max_rank}' if rank_value < 90 else ''})|NONE|NONE|{distribution_chance}")
                rank_value = (rank_value + 25) if rank_value > 0 else (rank_value + 15)
                distribution_chance += incremental_distribution_chance                  # On incrémente d'un cycle, en augmentant la probabilité de distribution par palier (rank_value) croissant
                increment_cycles -= 1

    
        output_DISTR.append("\n")
    

    else:                                                                                                   #DEBUG
        logging.debug(f"{spell} : non ajouté car mod {mod} pas dans user_modlist.")                         #DEBUG



print(" ")                                                                                                  #DEBUG



# TEST = (ROOT_DIR / "archetypes_test.json").read_text()

# Chargement de la liste au démarrage
# if os.path.exists(CUR_DIR + "/liste.json") :
#     with open(CUR_DIR + "/liste.json", "r") as saved_list :
#         LISTE = json.load(saved_list)
# else :
#     with open(CUR_DIR + "/liste.json", "w") as saved_list :
#         json.dump(LISTE, saved_list, indent=4)




# 3. creer une fonction qui va aller chercher le contenu des fichiers JSON et adapter les % d'injection avec des variables
        # % dependent :                                                                                                                         OK
                # - du niveau (Lv)                                                                                                              OK
                # - du niveau de skill (LvSk)                                                                                                   OK
                # - de l'archetype                                                                                                              OK
                # - du nombre de spells dispos dans la meme categorie (niveau de skill, archetype) / au meme palier                             OK
        # parametrer les paliers (proposer un fichier de configuration ?): 
                # - Lv necessaire [incl] (default = 1, 8, 16, 25, 35) +/- Lv max ou 999             --> 1/7, 8/15, 16/24, 25/34, 35/999
                # - LvSk necessaire [incl] (default = 0, 15, 40, 65, 90)                            --> 0/14, 15/39, 40/64, 65/89, 90
                # - %global pour le palier (default = 40%)
                # - %incremente par palier (default = 10%)
        # ATTENTION, si % de chance pour un spell < 1% ==> le passer a 1% ????? (AU FINAL FAIT AVEC ARRONDIS A 1 unité derrière la virgule)     OK
        # conditions de base :
                # ==> Novice        80% (global)    - 40% + 10%/palier      : Lv 1+ && LvSk 0+
                # ==> Apprentice    70% (global)    - 40% + 10%/palier      : Lv 10+ (ou 7+ ?) && LvSk 0+ (ou 15+ ?)
                # ==> Adept         60% (global)    - 40% + 10%/palier      : Lv 23+ (ou 15+ ou 20+ ?) && LvSk 40+
                # ==> Expert        50% (global)    - 40% + 10%/palier      : Lv 35+ (ou 23+ ou 30+ ?) && LvSk 65+
                # ==> Master        40% (global)    - 40% + 10%/palier      : Lv 1+ (ou 30+ ou 40+ ?) && LvSk 90+
        # modele JSON :
                # { ARCHETYPE01 =
                #   { NoviceSpells = 
                #       {0x124EC5~Apocalypse - Magic of Skyrim.esp,
                #        0xA561D3~Arcanum.esp,
                #        0x124F2A~StormCalling.esl
                #       },
                #     ApprenticeSpells = 
                #       {0x124EC5~Apocalypse - Magic of Skyrim.esp,
                #        0xA561D3~Arcanum.esp,
                #        0x124F2A~StormCalling.esl
                #       }
                #   },
                #   ARCHETYPE02 =
                #   { NoviceSpells = 
                #       {0x12321~Apocalypse - Magic of Skyrim.esp,
                #        0x124F2A~StormCalling.esl
                #       },
                #     ApprenticeSpells = 
                #       {0xA561D3~Arcanum.esp,
                #        0x144D3B~Astral.esl
                #       }
                #   }
                # }

    # MODELE DISTR : Spell = 0x12364~ModName.esp|TypeGeneric|NONE|13(50)|NONE|NONE|30
    #                                                            |                |%chance
	#                                                            |school(lv min/max)
	#                                                            |min/max level,skill(min/max)
    # Spell = formID~esp(OR)editorID|strings|formIDs(OR)editorIDs|min/max level,skill(min/max)|gender/unique/summonable|NONE|chance







# 4. creer une fonction qui va ecrire pour chaque filename le contenu (et creer) le fichier _DISTR.ini correspondant

OUTPUT = "\n".join(output_DISTR)                                                        # Formate le contenu de l'output pour ensuite créer le fichier _DISTR.ini avec toutes les données générées
(ROOT_DIR / f"output{SPID_EXTENSION}").write_text(OUTPUT)                               # Nom ("output") à changer (utiliser variable globale FILES ?) et raccorder premiers blocs d'instructions (for file in FILES etc) pour vérifier et adapter le nom de l'output ?






print(OUTPUT)                                                                                               # DEBUG


# Spells incertains : DES = Outdoors Apocalypse = Fingers of the Mountain (shock_mage), Flamestrike (fire_mage), Twister (frost_mage) ; ILU = Apocalypse = Ghostwalk, Blood for Blood
# Spells à voir pour ajouter ? : ILU = Arcanum apprentice = Shroud of Shadow / adept = Compelling Whispers / master = Mirror Entity, Wyrd, Tendrils of Agony
# Sorcier : Dragonborn.esm 04 020FC1 ; Talvas 017777
# Stormcalling = FormID ok ; Astral = FormID FE01xxxx, FormIDs à vérifier dans xEdit +/- enlever sap ?
# Astral Sap = pour Hogwart uniquement ? idem que Bite...


# nom : FAST (for) SPID (fast automated simple tool for SPID)

# test
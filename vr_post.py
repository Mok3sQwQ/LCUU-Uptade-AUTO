# ==========================================
# First import: Paste the entire column of Pokemon names here
# ==========================================
mons_input = """
Wattrel
Pawniard
Wingull
Tentacool
Crabrawler
Grookey
Dewpider
Meowth-Galar
Larvesta
Timburr
Drilbur
Sandshrew
Croagunk
Meowth
Doduo
Grimer-Alola
Voltorb
Axew
Hippopotas
Trapinch
Corphish
Larvitar
Numel
Salandit
Snubbull
Pikipek
Bramblin
Skrelp
Gimmighoul-Roaming
Greavard
Psyduck
Squirtle
Chespin
Cottonee
Houndour
Shroodle
Skiddo
Golett
Buizel
Horsea
Nymble
Slowpoke
Snover
Bagon
Venonat
Zorua
Bronzor
Cranidos
Froakie
Gible
Litten
Magnemite
Sandygast
Varoom
Barboach
Pineco
Riolu
Slowpoke-Galar
Chewtle
Rhyhorn
Sandile
Geodude-Alola
Fidough
Oddish
Quaxly
Scorbunny
Turtwig
Finizen
Fuecoco
Mankey
Wooper-Paldea
Chingling
Jangmo-o
Swablu
Treecko
Bulbasaur
Cetoddle
Charmander
Cufant
Ducklett
Joltik
Sprigatito
Bellsprout
Cyndaquil
Drowzee
Ekans
Exeggcute
Grimer
Hattena
Maschiff
Meowth-Alola
Nosepass
Solosis
Teddiursa
Blitzle
Cacnea
Chimchar
Clauncher
Duskull
Espurr
Finneon
Flabebe
Fletchling
Frigibax
Growlithe
Grubbin
Hoothoot
Inkay
Litleo
Litwick
Makuhita
Nacli
Piplup
Poltchageist
Seel
Shuppet
Silicobra
Sinistea
Slugma
Spoink
Starly
Surskit
Tadbulb
Wooper
"""

# ==========================================
# Second import: Paste the entire column of corresponding Tiers here
# ==========================================
tiers_input = """
S
A+
A+
A+
A
A
A
A
A
A
A-
A-
A-
A-
A-
A-
A-
B+
B+
B+
B+
B+
B+
B+
B+
B+
B
B
B
B
B
B
B
B
B
B
B
B
B-
B-
B-
B-
B-
B-
B-
B-
B-
B-
B-
B-
B-
B-
B-
B-
C+
C+
C+
C+
C+
C+
C+
C+
C
C
C
C
C
C
C
C
C
C
C
C
C
C
C
C
C
C
C
C
UR
UR
UR
UR
UR
UR
UR
UR
UR
UR
UR
UR
UR
UR
UR
UR
UR
UR
UR
UR
UR
UR
UR
UR
UR
UR
UR
UR
UR
UR
UR
UR
UR
UR
UR
UR
UR
UR
UR
UR
UR
UR"""

# ------------------------------------------
# Processing logic below
# ------------------------------------------

# 1. Preset official Smogon Tier colors and BBCode formats
tier_headers = {
    "S": "[COLOR=rgb(184, 49, 47)][B][SIZE=4]S[/SIZE][/B][/COLOR]",
    "A+": "[COLOR=rgb(251, 160, 38)][B]A+[/B][/COLOR]",
    "A": "[COLOR=rgb(247, 218, 100)][B]A[/B][/COLOR]",
    "A-": "[COLOR=rgb(97, 189, 109)][B]A-[/B][/COLOR]",
    "B+": "[COLOR=rgb(26, 188, 156)][B]B+[/B][/COLOR]",
    "B": "[COLOR=rgb(84, 172, 210)][B]B[/B][/COLOR]",
    "B-": "[COLOR=rgb(44, 130, 201)][B]B-[/B][/COLOR]",
    "C+": "[COLOR=rgb(147, 101, 184)][B]C+[/B][/COLOR]",
    "C": "[COLOR=rgb(85, 57, 130)][B]C[/B][/COLOR]",
    "UR": "[COLOR=rgb(71, 85, 119)][B]UR[/B][/COLOR]"
}

# 2. Clean up input data
mons_list = [mon.strip() for mon in mons_input.strip().split('\n') if mon.strip()]
tiers_list = [tier.strip().upper() for tier in tiers_input.strip().split('\n') if tier.strip()]

# 3. Safety check
if len(mons_list) != len(tiers_list):
    print(f" WARNING: The number of Pokemon ({len(mons_list)}) does not match the number of Tiers ({len(tiers_list)})!")
else:
    # 4. Create a dictionary using the standard Tier order
    ordered_tiers = ["S", "A+", "A", "A-", "B+", "B", "B-", "C+", "C", "UR"]
    tiered_dict = {t: [] for t in ordered_tiers}
    
    # Group Pokemon into their respective Tiers
    for mon, tier in zip(mons_list, tiers_list):
        if tier not in tiered_dict:
            tiered_dict[tier] = [] 
        tiered_dict[tier].append(mon)
        
    # 5. Function to format Pokemon names
    def format_pokemon_name(pokemon):
        formatted_name = pokemon.lower()
        return f":{formatted_name}: {pokemon}"

    # 6. Generate the final BBCode text
    for tier in ordered_tiers:
        mons = tiered_dict.get(tier, [])
        if mons:  # Only output Tiers that contain Pokemon
            # Output the colored Tier header
            header = tier_headers.get(tier, f"[B]{tier}[/B]") # Default to bold if an unknown tier is encountered
            print(header)
            
            # Output the Pokemon list (no indentation)
            for mon in mons:
                print(format_pokemon_name(mon))
            
            # Print a blank line as a separator
            print("")

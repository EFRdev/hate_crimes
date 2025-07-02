import pandas as pd
from thefuzz import process, fuzz

def find_best_match(name, choices, score_cutoff=80):
    """
    Finds the best match for a name from a list of choices using fuzzy matching.

    It uses token_set_ratio which is robust against extra words or different word order.

    Args:
        name (str): The name to correct (e.g., "Girona mal").
        choices (list): The list of official, correct names.
        score_cutoff (int): The minimum similarity score (0-100) to consider a match.

    Returns:
        str: The best matching name from the choices list if the score is high enough,
             otherwise returns the original name.
    """
    # process.extractOne returns a tuple of (best_match, score)
    best_match, score = process.extractOne(name, choices, scorer=fuzz.token_set_ratio)

    if score >= score_cutoff:
        print(f"Matched '{name}' -> '{best_match}' with score {score}")
        return best_match
    else:
        print(f"No good match for '{name}' (best score: {score}). Keeping original.")
        return name


# 1. --- Define the official lists (the source of truth) ---
# (This should be the complete, official list)
municipios_cat_oficial = [
    'barcelona', 'manresa', 'cabrils', 'premia de mar', 'mollet del valles', 'girona', 'tarragona', 'igualada',
    'calders', 'celra', 'reus', 'terrassa', 'palafrugell', 'vic', 'valls', 'sabadell', 'badalona', 'rubi', 'berga',
    'mataro', 'lleida', 'torredembarra', 'sant feliu de llobregat', 'lloret de mar', 'malgrat de mar', 'arenys de mar',
    'caldes de malavella', 'salou', 'granollers', 'cardedeu', 'la bisbal demporda', 'sitges', 'sant cugat del valles',
    'vilanova i la geltru', 'blanes', 'caldes de montbui', 'canovelles', 'calella', 'cadaques', 'vila seca',
    'el vendrell', 'viladecans', 'abrera', 'martorell', 'navarcles', 'gava', 'mollerussa', 'ripollet', 'castelldefels',
    'montornes del valles', 'calonge', 'bordils', 'tortosa', 'capellades', 'ripoll', 'roses', 'figueres',
    'canet de mar', 'castello dempuries', 'sant celoni', 'el bruc', 'cerdanyola del valles', 'sils', 'olot',
    'montmelo', 'sallent', 'argentona', 'suria', 'gurb', 'juneda', 'bellpuig', 'canyelles', 'llinars del valles',
    'sant boi de llobregat', 'bescano', 'calafell', 'alella', 'vilassar de mar', 'montcada i reixac', 'cornella de llobregat',
    'el prat de llobregat', 'santa perpetua de mogoda', 'parets del valles', 'esparreguera'
]

comarcas_cat_oficial = [
    'bages', 'anoia', 'osona', 'garraf', 'selva', 'bergueda', 'girones', 'moianes', 'valles occidental',
    'valles oriental', 'alt emporda', 'baix emporda', 'baix camp', 'alt camp', 'tarragones', 'segrià', 'urgell',
    'alta ribagorca', 'terra alta', 'montsia', 'ripolles', 'pla de lestany', 'conca de barbera', 'cerdanya',
    'pallars jussa', 'garrigues', 'alt urgell', 'noguera', 'baix ebre', 'solsones', 'segarra', 'ribera debre',
    'baix penedes', 'alt penedes', 'pla durgell', 'val daran'
]


# 2. --- Load your data ---
# This is a sample DataFrame. You would load your actual data here,
# for example from a CSV file: df = pd.read_csv('your_data.csv')
df = pd.read_csv('/Users/enrique/code/EFRdev/00 - Post-Bootcamp/Hate_Crimes/data/Catalunya_Hate_Crimes.csv')

print("--- Original DataFrame ---")
print(df)
print("\n--- Processing and Correcting Names ---\n")

# 3. --- Apply the correction function to the columns ---
# We use .apply() to run our find_best_match function on every name in the column.
# A lambda function is a concise way to pass the additional arguments.

df['Municipi_Clean'] = df['Municipi'].apply(
    lambda x: find_best_match(x, municipios_cat_oficial)
)

df['Comarca_Clean'] = df['Comarca'].apply(
    lambda x: find_best_match(x, comarcas_cat_oficial, score_cutoff=85) # Using a slightly higher threshold for comarcas
)


# 4. --- Display the final results ---
print("\n--- DataFrame with Corrected Names ---")
print(df[['Municipi', 'Municipi_Clean', 'Comarca', 'Comarca_Clean']])

# You can save the final result to a new file
# df.to_csv('corrected_data.csv', index=False)

import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import random
import requests

# Streamlit App Title
st.title("Pokemon Information Viewer")

# Load the Pokémon CSV
pokemon_data = pd.read_csv("pokemon.csv")

# Input for Pokemon Pokedex Number
pokemon_number = st.number_input("Enter Pokemon Number:", 
                                min_value=int(pokemon_data['pokedex_number'].min()), 
                                max_value=int(pokemon_data['pokedex_number'].max()), 
                                step=1)




# Define type-to-color mapping
type_colors = {
    "Fire": "red",
    "Water": "blue",
    "Grass": "green",
    "Electric": "gold",
    "Psychic": "purple",
    "Normal": "gray",
    "Fighting": "brown",
    "Flying": "skyblue",
    "Poison": "violet",
    "Ground": "peru",
    "Rock": "darkgoldenrod",
    "Bug": "limegreen",
    "Ghost": "indigo",
    "Steel": "silver",
    "Ice": "cyan",
    "Dragon": "orange",
    "Dark": "black",
    "Fairy": "pink",
}

# Function to format the type
def format_type(type_name):
    color = type_colors.get(type_name, "black")  # Default to black if type not in dictionary
    return f'<span style="color:white;background-color:{color};padding:5px 10px;border-radius:5px;">{type_name}</span>'

# Initialize a variable for name, to avoid undefined errors
name = None
height = None
weight = None

# Action when the button is clicked
#if st.button("Fetch Pokemon Data"):
    # Fetch Pokémon details
pokemon = pokemon_data[pokemon_data['pokedex_number'] == pokemon_number].iloc[0]
name = pokemon['name']
height = pokemon['height_m']
weight = pokemon['weight_kg']
type_1 = pokemon['type_1']
type_2 = pokemon['type_2'] if not pd.isna(pokemon['type_2']) else None
abilities = [pokemon['ability_1']]
if not pd.isna(pokemon['ability_2']):
    abilities.append(pokemon['ability_2'])
if not pd.isna(pokemon['ability_hidden']):
    abilities.append(f"Hidden: {pokemon['ability_hidden']}")
    

    

# Display Pokémon details
st.subheader(f"Details for {name}")
st.write(f"**Height:** {height} meters")
st.write(f"**Weight:** {weight} kilograms")

# Display types with formatted badges
type_1_badge = format_type(type_1)
if type_2:
    type_2_badge = format_type(type_2)
    st.markdown(f"**Types:** {type_1_badge} {type_2_badge}", unsafe_allow_html=True)
else:
    st.markdown(f"**Type 1:** {type_1_badge}", unsafe_allow_html=True)

# Display abilities
st.write(f"**Abilities:** {', '.join(abilities)}")

# Fetch Pokémon image from PokeAPI
url = f"https://pokeapi.co/api/v2/pokemon/{pokemon_number}"  # Use pokedex_number here
response = requests.get(url)
if response.status_code == 200:
    poke_api_data = response.json()
    sprite_url = poke_api_data["sprites"]["front_default"]
    st.image(sprite_url, caption=f"{name} Image", width=200)
else:
    st.error("Failed to fetch Pokemon image")
    
with st.sidebar:
    st.header("Evolution chain")
    st.caption(f"The pokemon {name} evolves from or to")
    response = requests.get(poke_api_data["species"]["url"])
    poke_species = response.json()
    response = requests.get(poke_species["evolution_chain"]["url"])
    evolution_chain = response.json()
    st.write(evolution_chain["chain"]["species"]["name"])
    response = requests.get(f"https://pokeapi.co/api/v2/pokemon/{evolution_chain["chain"]["species"]["name"]}")
    poke1 = response.json()
    st.image(poke1["sprites"]["front_default"], caption=f"{name} Image", width=200)
    st.write(f"To evolve: Level to {evolution_chain["chain"]["evolves_to"][0]["evolution_details"][0]["min_level"]}")
    if evolution_chain["chain"]["evolves_to"][0]:
        response = requests.get(f"https://pokeapi.co/api/v2/pokemon/{evolution_chain["chain"]["evolves_to"][0]["species"]["name"]}")
        poke2 = response.json()
        st.write(evolution_chain["chain"]["evolves_to"][0]["species"]["name"])
        
        st.image(poke2["sprites"]["front_default"], caption=f"{name} Image", width=200)
        
        if evolution_chain["chain"]["evolves_to"][0]["evolves_to"]:
            st.write(f"To evolve: Level to {evolution_chain["chain"]["evolves_to"][0]["evolves_to"][0]["evolution_details"][0]["min_level"]}")
            response = requests.get(f"https://pokeapi.co/api/v2/pokemon/{evolution_chain["chain"]["evolves_to"][0]["evolves_to"][0]["species"]["name"]}")
            poke3 = response.json()
            st.write(evolution_chain["chain"]["evolves_to"][0]["evolves_to"][0]["species"]["name"])
            st.image(poke3["sprites"]["front_default"], caption=f"{name} Image", width=200)
            

# Proceed with comparison only after button click
if name:
    st.subheader("Comparison with Other Pokemon")
    choice = st.selectbox(f"What would you like to compare {name} against?", ("Height", "Weight"))
    # Sampling random Pokémon for comparison
    random_pokemon = pokemon_data.sample(n=5)

    # Add the selected Pokémon to the comparison data
    comparison_data = pd.DataFrame([{
        "name": name,
        "height": height,
        "weight": weight
    }])
    comparison_data = pd.concat([comparison_data, random_pokemon[['name', 'height_m', 'weight_kg']].rename(columns={"height_m": "height", "weight_kg": "weight"})], ignore_index=True)
    bar_colour = type_colors.get(type_1, "gray") 
    fig, ax = plt.subplots(figsize=(8, 5))
    if choice == "height":
        comparison_data.plot(kind="bar", x="name", y="height", ax=ax, color=bar_colour)
        plt.ylabel("Height in m")
    else:
        comparison_data.plot(kind="bar", x="name", y="weight", ax=ax, color=bar_colour)
        plt.ylabel("Weight in kg")

    
    plt.title(f"{choice} Comparison")
    plt.xticks(rotation=45)
    st.pyplot(fig)

from GameEndings import show_endings
import streamlit as st
import helperfunctions

class Game:
    def __init__(self):
        self.current_location = "forest_clearing"
        self.inventory = []
        self.story_state = {
            "met_girl": False,
            "angry_with_girl": False,
            "nice_to_girl": False,
            "entity_following": False,
            "ending": None,
            "saw_light": False,            
            "girl_dialogue_phase": 0,      
            "girl_intro_done": False       
        }
        
        self.locations = {
            "forest_clearing": {
                "description": "You wake up in a forest clearing, panicked and confused.",
                "items": [],
                "connections": {"north": "path_to_girl"}
            },
            "path_to_girl": {
                "description": "You see a little girl wandering through the woods.",
                "items": [],
                "connections": {"south": "forest_clearing", "north": "girl_encounter"}
            },
            "girl_encounter": {
                "description": "The girl looks at you with strange eyes.", 
                "items": ["photo"],
                "connections": {"south": "path_to_girl", "north": "black_entity_area"}
            },
            "black_entity_area": {
                "description": "The girl transforms into a black entity that mirrors your movements.",
                "items": [],
                "connections": {"south": "girl_encounter", "east": "river", "west": "neverending_forest"}
            },
            "river": {
                "description": "You arrive at a river. You can try to drown the entity or swim across.",
                "items": [],
                "connections": {"west": "black_entity_area"}
            },
            "neverending_forest": {
                "description": "The forest seems to go on forever...",
                "items": [],
                "connections": {"east": "black_entity_area"}
            }
        }

    def move(self, direction):
        if direction in self.locations[self.current_location]["connections"]:
            self.current_location = self.locations[self.current_location]["connections"][direction]
            return f"You move {direction} to {self.current_location}. {self.locations[self.current_location]['description']}"
        else:
            return "You can't go that way."

    def look(self):
        if self.current_location == "forest_clearing" and not self.story_state["saw_light"]:
            return (
                "Your head is spinning. *What happened?* "
                "You try to remember, but nothing comes. "
                "The forest feels alive, pressing in on all sides.\n\n"
                "You look around and notice a faint light flickering between the trees."
            )
        
        loc = self.locations[self.current_location]
        desc = loc["description"]
        items = "You see: " + ", ".join(loc["items"]) if loc["items"] else ""
        exits = "Exits: " + ", ".join(loc["connections"].keys())
        return f"{desc}\n{items}\n{exits}"

    def pick_up(self, item):
        loc = self.locations[self.current_location]
        if item in loc["items"]:
            self.inventory.append(item)
            loc["items"].remove(item)
            return f"You picked up the {item}."
        else:
            return f"No {item} here."

    def show_inventory(self):
        return "Inventory: " + ", ".join(self.inventory) if self.inventory else "Your inventory is empty."


# --- Session State ---
if "game" not in st.session_state:
    st.session_state.game = Game()
if "started" not in st.session_state:
    st.session_state.started = False
if "continued" not in st.session_state:
    st.session_state.continued = False

game = st.session_state.game

# --- Styling ---
st.markdown(
    """
    <style>
    header, footer, [data-testid="stToolbar"], [data-testid="stDecoration"] {
        display: none !important;
    }
    [data-testid="stAppViewContainer"], 
    [data-testid="stMainContent"], 
    .block-container {
        height: 100vh !important;
        width: 100vw !important;
        padding: 0 !important;
        background: transparent !important;
    }
    body, .stApp {
        color: white !important;
    }
    .stButton>button {
        background-color: rgba(255, 255, 255, 0.15);
        color: white !important;
        border: 1px solid white;
        border-radius: 12px;
        padding: 0.5em 1em;
        font-weight: bold;
        transition: all 0.3s ease-in-out;
    }
    .stButton>button:hover {
        background-color: rgba(255, 255, 255, 0.3);
        border-color: #fff;
        transform: scale(1.05);
    }
    </style>
    """,
    unsafe_allow_html=True
)

# --- Game Flow ---
if not st.session_state.started:
    helperfunctions.set_background("https://images.unsplash.com/photo-1555063074-90bc1d260117?w=1600")
    st.markdown(
        "<h1 style='text-align: center; font-size: 60px; font-family: Franklin-Gothic; -webkit-text-stroke: 1px black;'>The Forest Interactive</h1>",
        unsafe_allow_html=True
    )
    if st.button("Start Game"):
        st.session_state.started = True
        st.rerun()

elif not st.session_state.continued:
    helperfunctions.set_background("https://raw.githubusercontent.com/Norodril/firstRepository/refs/heads/main/forest_photo.png")
    st.write("You wake up... *Where am I?*")
    st.write("You remember nothing about yourself.")
    if st.button("Continue"):
        st.session_state.continued = True
        st.rerun()

else:
    # Special intro
    if game.current_location == "forest_clearing" and not game.story_state["saw_light"]:
        helperfunctions.set_background("https://raw.githubusercontent.com/Norodril/firstRepository/refs/heads/main/forest_path.png")
        st.write(game.look())
        if st.button("Head towards the light"):
            game.story_state["saw_light"] = True
            st.session_state.light_phase = "girl_intro"
            st.rerun()

    elif getattr(st.session_state, "light_phase", "") == "girl_intro":
        helperfunctions.set_background("https://raw.githubusercontent.com/Norodril/firstRepository/refs/heads/main/girl_in_shadows.png")
        st.write("You follow the flickering light, and see the figure of a little girl in the distance.")
        if st.button("Head towards the girl"):
            game.current_location = "girl_encounter"
            st.session_state.light_phase = None
            st.rerun()

    elif game.current_location == "girl_encounter" and not game.story_state["girl_intro_done"]:
        helperfunctions.set_background("https://raw.githubusercontent.com/Norodril/firstRepository/refs/heads/main/girl_interaction.png")
        st.write("The girl looks at you with strange eyes.")
        if st.button("Interact"):
            game.story_state["girl_intro_done"] = True
            st.rerun()

    elif game.current_location == "girl_encounter" and game.story_state["girl_dialogue_phase"] < 3:
        helperfunctions.set_background("https://raw.githubusercontent.com/Norodril/firstRepository/refs/heads/main/girl_interaction.png")
        phase = game.story_state["girl_dialogue_phase"]
        if phase == 0:
            st.write("You see the girl staring at you silently.")
            if st.button("Say: Excuse me..."):
                game.story_state["girl_dialogue_phase"] = 1
                st.rerun()
        elif phase == 1:
            cols = st.columns(3)
            if cols[0].button("Ask: Where am I?"):
                st.write("Girl: 'This is my home. The forest keeps those who enter.'")
            if cols[1].button("Ask: What is this place?"):
                st.write("Girl: 'It is the forest. It has always been here.'")
            if cols[2].button("Ask: Do you know who I am?"):
                st.write("Girl: 'You don't remember anything about yourself?'")
            if st.button("Finish talking"):
                game.story_state["girl_dialogue_phase"] = 2
                game.current_location = "black_entity_area"
                st.rerun()
    elif game.current_location == "black_entity_area":
        helperfunctions.set_background("https://raw.githubusercontent.com/Norodril/firstRepository/refs/heads/main/shadow_figure.png")
        st.write("The girl transforms into a black entity that mirrors your movements.")
        show_endings(game)

    
    
    


import random
import streamlit as st

# Fixed internal list of team members - edit this to match your team
TEAM_MEMBERS = [
    "Alex",
    "Bonnie",
    "Charlie",
    "Diana",
    "Erik",
    "Freja",
    "Gustav",
]

NUM_PRODUCT_OWNERS = 2
NUM_SCRUM_MASTERS = 2

st.set_page_config(page_title="Scrum Role Draw", page_icon="🎲", layout="centered")

st.title("🎲 Scrum Role Draw")
st.write(
    f"Randomly assign roles to the team: "
    f"**{NUM_PRODUCT_OWNERS}** product owners, "
    f"**{NUM_SCRUM_MASTERS}** scrum masters, "
    f"and the rest as the development team."
)

with st.expander("Team members", expanded=False):
    st.write(", ".join(TEAM_MEMBERS))

# Validate team size
required = NUM_PRODUCT_OWNERS + NUM_SCRUM_MASTERS + 1
if len(TEAM_MEMBERS) < required:
    st.error(
        f"Need at least {required} team members to draw all roles. "
        f"Currently {len(TEAM_MEMBERS)}."
    )
    st.stop()

# Optional seed for reproducible draws
seed_input = st.text_input(
    "Seed (optional)",
    value="",
    help="Enter any text to make the draw reproducible. Leave empty for a random draw.",
)

if st.button("Draw roles", type="primary", use_container_width=True):
    rng = random.Random(seed_input) if seed_input else random.Random()
    shuffled = TEAM_MEMBERS.copy()
    rng.shuffle(shuffled)

    product_owners = shuffled[:NUM_PRODUCT_OWNERS]
    scrum_masters = shuffled[NUM_PRODUCT_OWNERS : NUM_PRODUCT_OWNERS + NUM_SCRUM_MASTERS]
    developers = shuffled[NUM_PRODUCT_OWNERS + NUM_SCRUM_MASTERS :]

    st.session_state["result"] = {
        "product_owners": product_owners,
        "scrum_masters": scrum_masters,
        "developers": developers,
    }

if "result" in st.session_state:
    r = st.session_state["result"]

    st.subheader("Product owners")
    for name in r["product_owners"]:
        st.markdown(f"- {name}")

    st.subheader("Scrum masters")
    for name in r["scrum_masters"]:
        st.markdown(f"- {name}")

    st.subheader("Development team")
    for name in r["developers"]:
        st.markdown(f"- {name}")

import random
from pathlib import Path

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
NONE_LABEL = "— none —"

st.set_page_config(page_title="Scrum Role Draw", page_icon="🎲", layout="centered")

# Show the B-team poster at the top of the page
_image_path = Path(__file__).parent / "b_team.png"
if _image_path.exists():
    st.image(str(_image_path), use_container_width=True)

st.title("🎲 Scrum Role Draw")
st.write(
    f"Randomly assign roles to the team: "
    f"**{NUM_PRODUCT_OWNERS}** product owners, "
    f"**{NUM_SCRUM_MASTERS}** scrum masters, "
    f"and the rest as the development team. "
    f"Previous product owners and scrum masters can't keep the same role two draws in a row."
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


def draw_roles(members, previous, rng, max_attempts=2000):
    """
    Shuffle members into roles such that nobody who was a product owner or
    scrum master in `previous` gets the same role again. Devs can repeat as devs.
    Returns (product_owners, scrum_masters, developers) or None if no valid
    assignment is found within max_attempts.
    """
    prev_po = set(previous.get("product_owners", [])) if previous else set()
    prev_sm = set(previous.get("scrum_masters", [])) if previous else set()

    for _ in range(max_attempts):
        shuffled = members.copy()
        rng.shuffle(shuffled)
        pos = shuffled[:NUM_PRODUCT_OWNERS]
        sms = shuffled[NUM_PRODUCT_OWNERS : NUM_PRODUCT_OWNERS + NUM_SCRUM_MASTERS]
        devs = shuffled[NUM_PRODUCT_OWNERS + NUM_SCRUM_MASTERS :]

        if any(p in prev_po for p in pos):
            continue
        if any(s in prev_sm for s in sms):
            continue
        return pos, sms, devs

    return None


# ---- Current roles input ---------------------------------------------------
st.subheader("Current roles")
st.caption(
    "Pick the people who currently hold each role. The draw will avoid giving them the same role again. "
    "Leave as “— none —” if there's no current assignment."
)

options = [NONE_LABEL] + TEAM_MEMBERS

# Pre-fill from the last result if available
last = st.session_state.get("result")
defaults = {
    "po1": last["product_owners"][0] if last else NONE_LABEL,
    "po2": last["product_owners"][1] if last else NONE_LABEL,
    "sm1": last["scrum_masters"][0] if last else NONE_LABEL,
    "sm2": last["scrum_masters"][1] if last else NONE_LABEL,
}

po_col1, po_col2 = st.columns(2)
with po_col1:
    cur_po1 = st.selectbox(
        "Product owner 1", options, index=options.index(defaults["po1"]), key="cur_po1"
    )
with po_col2:
    cur_po2 = st.selectbox(
        "Product owner 2", options, index=options.index(defaults["po2"]), key="cur_po2"
    )

sm_col1, sm_col2 = st.columns(2)
with sm_col1:
    cur_sm1 = st.selectbox(
        "Scrum master 1", options, index=options.index(defaults["sm1"]), key="cur_sm1"
    )
with sm_col2:
    cur_sm2 = st.selectbox(
        "Scrum master 2", options, index=options.index(defaults["sm2"]), key="cur_sm2"
    )

# Collect non-empty selections
current_pos = [n for n in [cur_po1, cur_po2] if n != NONE_LABEL]
current_sms = [n for n in [cur_sm1, cur_sm2] if n != NONE_LABEL]

# Validate dropdown selections
selection_errors = []
if len(set(current_pos)) != len(current_pos):
    selection_errors.append("The two product owners must be different people.")
if len(set(current_sms)) != len(current_sms):
    selection_errors.append("The two scrum masters must be different people.")
overlap = set(current_pos) & set(current_sms)
if overlap:
    selection_errors.append(
        f"A person can't be both PO and SM: {', '.join(sorted(overlap))}."
    )

for err in selection_errors:
    st.warning(err)

# ---- Draw controls ---------------------------------------------------------
seed_input = st.text_input(
    "Seed (optional)",
    value="",
    help="Enter any text to make the draw reproducible. Leave empty for a random draw.",
)

col1, col2 = st.columns([3, 1])
with col1:
    draw_clicked = st.button(
        "Draw roles",
        type="primary",
        use_container_width=True,
        disabled=bool(selection_errors),
    )
with col2:
    reset_clicked = st.button("Clear result", use_container_width=True)

if reset_clicked:
    st.session_state.pop("result", None)

if draw_clicked:
    rng = random.Random(seed_input) if seed_input else random.Random()
    previous = {"product_owners": current_pos, "scrum_masters": current_sms}
    result = draw_roles(TEAM_MEMBERS, previous, rng)

    if result is None:
        st.error(
            "Couldn't find a valid assignment that avoids the current roles. "
            "Try clearing some current-role dropdowns."
        )
    else:
        pos, sms, devs = result
        st.session_state["result"] = {
            "product_owners": pos,
            "scrum_masters": sms,
            "developers": devs,
        }

# ---- Results ---------------------------------------------------------------
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

    st.caption(
        "Tip: the dropdowns above are now pre-filled with this result, so the next draw "
        "will automatically avoid repeating these PO and SM assignments."
    )

import streamlit as st
import pandas as pd

# Load interleaving material cost data (simulating VLOOKUP)
@st.cache_data
def load_cost_data():
    return pd.read_csv("interleaving_cost.csv")

cost_data = load_cost_data()

# Title
st.title("Packing Costing App")

# Step 01 - Inputs
st.header("Step 01: User Inputs")

identification_no = st.text_input("Identification No.")

st.subheader("Profile Dimensions (mm)")
W = st.number_input("W (mm)", min_value=0.0, format="%.2f")
H = st.number_input("H (mm)", min_value=0.0, format="%.2f")
L = st.number_input("L (mm)", min_value=0.0, format="%.2f")

finish = st.selectbox(
    "Finish",
    options=["Mill Finished", "Anodized", "Powder Coated", "Wood Finished"]
)

fabricated = st.selectbox(
    "Fabricated",
    options=["Fabricated", "Just Cutting"]
)

eco_friendly = st.selectbox(
    "Eco-Friendly Packing",
    options=["Yes", "No"]
)

interleaving_required = st.selectbox(
    "Interleaving Required",
    options=["Yes", "No"]
)

bundling = st.selectbox(
    "Bundling",
    options=["Yes", "No"]
)

crate_pallet = st.selectbox(
    "Crate/ Palletizing",
    options=["Crate", "Pallet"]
)

# Outputs
st.header("Outputs")

# Interleaving Material logic
if eco_friendly == "Yes":
    interleaving_material = "Craft Paper"
else:
    interleaving_material = "McFoam"

st.write("**Interleaving Material:**", interleaving_material)

# Reject Check Message
if finish == "Mill Finished" and interleaving_material == "Craft Paper":
    message = "Okay"
else:
    message = "can cause rejects - go ahead with McFoam"

st.write("**Check:**", message)

# Surface Area (m2)
surface_area = (2 * ((W * L) + (H * L) + (W * H))) / (1000 ** 2)
st.write("**Surface Area (m²):**", round(surface_area, 4))

# Cost of Interleaving Material (simulate VLOOKUP)
cost_lookup = cost_data.set_index("Material").to_dict()["Cost"]
interleaving_cost = cost_lookup.get(interleaving_material, "Not Found")
st.write("**Cost of Interleaving Material (per unit):**", interleaving_cost)

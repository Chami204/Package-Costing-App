import streamlit as st
import pandas as pd

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

Protective Tape - Customer Specified = st.selectbox(
    "Yes/No",
    options = ["Yes","No"]
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
# Cost of Interleaving Material (Rs/m²)
if interleaving_material == "McFoam":
    interleaving_cost = 51.00
elif interleaving_material == "Craft Paper":
    interleaving_cost = 34.65
elif interleaving_material == "Protective Tape":
    interleaving_cost = 100.65
elif interleaving_material == "Stretchwrap":
    interleaving_cost = 14.38
else:
    interleaving_cost = "Unknown"

st.write("**Cost of Interleaving Material (Rs/m²):**", interleaving_cost)

#Interleaving Cost(Rs)
Interleaving Cost = Surface Area (m²) * Cost of Interleaving Material (Rs/m²)


if Protective Tape - Customer Specified == "No":
    if (fabricated == "Fabricated" and finish == "Mill Finish") or fabricated == "Just Cutting":
        protective_tape_advice = "OK"
    else:
        protective_tape_advice = "Protective tape required to avoid rejects"
else:
    protective_tape_advice = ""

st.write("**Protective Tape Advice:**", protective_tape_advice)

# Protective Tape (Rs/m²)
if interleaving_material == "McFoam":
    interleaving_cost = 51.00
elif interleaving_material == "Craft Paper":
    interleaving_cost = 34.65
elif interleaving_material == "Protective Tape":
    interleaving_cost = 100.65
elif interleaving_material == "Stretchwrap":
    interleaving_cost = 14.38
else:
    interleaving_cost = "Unknown"

st.write("**Protective Tape Cost (Rs/m²):**", protective_Tape_advice)

Protective Tape Cost = Surface Area (m²) * Protective Tape Cost (Rs/m²)

=IF(B13="Yes","Define Bundle Stack","Move to Crate/Pallet Packing Directly")

If Bundling == "Yes":
    print "Define Bundle Stack"
else:
    print "Move to Crate/Pallet Packing Directly"
    

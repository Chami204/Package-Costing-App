import streamlit as st

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
    options=["Mill Finish", "Anodized", "Powder Coated", "Wood Finished"]
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

protective_tape_customer_specified = st.selectbox(
    "Protective Tape - Customer Specified",
    options=["Yes", "No"]
)

bundling = st.selectbox("Bundling", ["Yes", "No"])

crate_pallet = st.selectbox("Crate/ Palletizing", ["Crate", "Pallet"])

# Outputs
st.header("Outputs")

# Interleaving Material logic
if eco_friendly == "Yes":
    interleaving_material = "Craft Paper"
else:
    interleaving_material = "McFoam"

st.write("**Interleaving Material:**", interleaving_material)

# Reject Check Message
if finish == "Mill Finish" and interleaving_material == "Craft Paper":
    message = "Okay"
else:
    message = "Can cause rejects - go ahead with McFoam"

st.write("**Check:**", message)

# Surface Area (m²)
surface_area = (2 * ((W * L) + (H * L) + (W * H))) / 1_000_000
st.write("**Surface Area (m²):**", round(surface_area, 4))

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
    interleaving_cost = 0.0

st.write("**Cost of Interleaving Material (Rs/m²):**", interleaving_cost)

# Interleaving Total Cost
interleaving_total_cost = surface_area * interleaving_cost
st.write("**Interleaving Cost (Rs):**", round(interleaving_total_cost, 2))

# Protective Tape Advice
if protective_tape_customer_specified == "No":
    if (fabricated == "Fabricated" and finish == "Mill Finish") or fabricated == "Just Cutting":
        protective_tape_advice = "OK"
    else:
        protective_tape_advice = "Protective tape required to avoid rejects"
else:
    protective_tape_advice = ""

st.write("**Protective Tape Advice:**", protective_tape_advice)

# Protective Tape Cost (Rs/m²)
protective_tape_rate = 100.65  # You may update this if dynamic

if "Protective Tape" in protective_tape_advice:
    protective_tape_cost = surface_area * protective_tape_rate
else:
    protective_tape_cost = 0.0

st.write("**Protective Tape Cost (Rs):**", round(protective_tape_cost, 2))

# Decision based on bundling
if bundling == "Yes":
    st.subheader("Define Bundle Stack")

    # Get user inputs
    num_rows = st.number_input("Number of Rows (Width direction)", min_value=1, step=1)
    num_layers = st.number_input("Number of Layers (Height direction)", min_value=1, step=1)

    # Use L as bundle length
    bundle_length = L

    # Choose profile dimension types
    profile_width_type = st.selectbox("Width Profile Type", ["W/mm", "H/mm"])
    profile_height_type = st.selectbox("Height Profile Type", ["H/mm", "W/mm"])

    # Simulate VLOOKUP-style mapping
    profile_dimensions = {
        "W/mm": W,
        "H/mm": H

    #choose Material for Bundle Wrap
    Material_for_bundle_wrap = st.selection("Material for Bundle Wrap",["Stretchwrap","Cardboard Wrapper","Cardboard Carton"])

    Complete_Wrap_OR_Only_Sections = st.selection("Complete wrap OR Only Sections", ["Complete","Only Sections"]
        
    }

    # Calculate bundle dimensions
    bundle_width = num_rows * profile_dimensions.get(profile_width_type, 0)
    bundle_height = num_layers * profile_dimensions.get(profile_height_type, 0)

    # Display dimensions
    st.subheader("Bundle Dimensions (mm):")
    st.write(f"**Bundle Width:** {bundle_width:.2f} mm")
    st.write(f"**Bundle Height:** {bundle_height:.2f} mm")
    st.write(f"**Bundle Length:** {bundle_length:.2f} mm")

else:
    st.subheader("Move to Crate/Pallet Packing Directly")

    Area Covered = =(2*((Bundle Width*Bundle Length)+(Bundle Height*Bundle Length)+(Bundle Width*Bundle Height)))/(1000^2)

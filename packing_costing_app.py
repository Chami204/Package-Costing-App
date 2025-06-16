import streamlit as st
import pandas as pd

# Set page icon and title
st.set_page_config(page_title="Targeted Packing Costing", page_icon="🎯💰")

st.title("🎯💰 Targeted Packing Costing App")

st.header("Step 01: Enter Packing Data Table")

# Default input table
default_data = {
    "Identification No.": ["ID001"],
    "W (mm)": [50.0],
    "H (mm)": [60.0],
    "L (mm)": [1000.0],
    "Finish": ["Mill Finish"],
    "Fabricated": ["Fabricated"],
    "Eco-Friendly Packing": ["Yes"],
    "Interleaving Required": ["Yes"],
    "Protective Tape - Customer Specified": ["No"],
    "Bundling": ["Yes"],
    "Crate/ Palletizing": ["Crate"]
}

input_df = st.data_editor(pd.DataFrame(default_data), use_container_width=True, key="main_input")

output_rows = []

for index, row in input_df.iterrows():
    W, H, L = row["W (mm)"], row["H (mm)"], row["L (mm)"]
    finish = row["Finish"]
    fabricated = row["Fabricated"]
    eco_friendly = row["Eco-Friendly Packing"]
    protective_tape_customer_specified = row["Protective Tape - Customer Specified"]

    # Interleaving
    interleaving_material = "Craft Paper" if eco_friendly == "Yes" else "McFoam"
    check_message = "Okay" if finish == "Mill Finish" and interleaving_material == "Craft Paper" else "Can cause rejects - go ahead with McFoam"

    # Surface Area
    surface_area = (2 * ((W * L) + (H * L) + (W * H))) / 1_000_000

    # Rates
    rates = {
        "McFoam": 51.00,
        "Craft Paper": 34.65,
        "Protective Tape": 100.65,
        "Stretchwrap": 14.38
    }

    interleaving_cost_rate = rates.get(interleaving_material, 0)
    interleaving_total_cost = surface_area * interleaving_cost_rate

    # Protective tape advice
    if protective_tape_customer_specified == "No":
        if (fabricated == "Fabricated" and finish == "Mill Finish") or fabricated == "Just Cutting":
            tape_advice = "OK"
        else:
            tape_advice = "Protective tape required to avoid rejects"
    else:
        tape_advice = "Protective tape required as per customer"

    # Protective tape cost condition
    if "Protective tape required" in tape_advice or protective_tape_customer_specified == "Yes":
        protective_tape_cost = surface_area * rates["Protective Tape"]
    else:
        protective_tape_cost = 0.0

    output_rows.append({
        "Identification No.": row["Identification No."],
        "Interleaving Material": interleaving_material,
        "Check": check_message,
        "Surface Area (m²)": round(surface_area, 4),
        "Interleaving Cost (Rs)": round(interleaving_total_cost, 2),
        "Protective Tape Advice": tape_advice,
        "Protective Tape Cost (Rs)": round(protective_tape_cost, 2)
    })

# Output summary
st.markdown("### 🟩 Output Summary")
st.dataframe(pd.DataFrame(output_rows).style.set_properties(
    **{"background-color": "#E6F2FF", "color": "black"}
), use_container_width=True)

# Bundle Stack Inputs and Outputs
st.header("Step 02: Bundle Stack Inputs (if Bundling is Yes)")

bundle_outputs = []

for index, row in input_df.iterrows():
    if row["Bundling"] == "Yes":
        st.markdown(f"#### Bundle for: **{row['Identification No.']}**")

        num_rows = st.number_input(f"Rows (Width) - {row['Identification No.']}", 1, key=f"rows_{index}")
        num_layers = st.number_input(f"Layers (Height) - {row['Identification No.']}", 1, key=f"layers_{index}")
        width_type = st.selectbox(f"Width Profile - {row['Identification No.']}", ["W/mm", "H/mm"], key=f"wtype_{index}")
        height_type = st.selectbox(f"Height Profile - {row['Identification No.']}", ["H/mm", "W/mm"], key=f"htype_{index}")

        dim_map = {"W/mm": row["W (mm)"], "H/mm": row["H (mm)"]}
        bundle_width = num_rows * dim_map[width_type]
        bundle_height = num_layers * dim_map[height_type]
        bundle_length = row["L (mm)"]

        area_covered = 2 * ((bundle_width * bundle_length) + (bundle_height * bundle_length) + (bundle_width * bundle_height)) / 1_000_000

        bundle_outputs.append({
            "Identification No.": row["Identification No."],
            "Bundle Width (mm)": round(bundle_width, 2),
            "Bundle Height (mm)": round(bundle_height, 2),
            "Bundle Length (mm)": bundle_length,
            "Area Covered (m²)": round(area_covered, 4)
        })

if bundle_outputs:
    st.markdown("### 🟦 Bundle Output Table")
    st.dataframe(pd.DataFrame(bundle_outputs).style.set_properties(
        **{"background-color": "#FFF9C4", "color": "black"}
    ), use_container_width=True)

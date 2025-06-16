import streamlit as st
import pandas as pd

st.set_page_config(page_title="🎯💰 Targeted Packing Costing", page_icon="🎯💰")
st.title("🎯💰 Targeted Packing Costing App")

# Sample input table for profile data
input_data = pd.DataFrame({
    "Identification No.": [""],
    "W (mm)": [0.0],
    "H (mm)": [0.0],
    "L (mm)": [0.0],
    "Finish": ["Mill Finish"],
    "Fabricated": ["Fabricated"],
    "Eco-Friendly Packing": ["Yes"],
    "Interleaving Required": ["Yes"],
    "Protective Tape - Customer Specified": ["No"],
    "Bundling": ["Yes"],
    "Crate/ Palletizing": ["Crate"]
})

# Define dropdown options
dropdown_columns = {
    "Finish": {"editor": "select", "options": ["Mill Finish", "Anodized", "Powder Coated", "Wood Finished"]},
    "Fabricated": {"editor": "select", "options": ["Fabricated", "Just Cutting"]},
    "Eco-Friendly Packing": {"editor": "select", "options": ["Yes", "No"]},
    "Interleaving Required": {"editor": "select", "options": ["Yes", "No"]},
    "Protective Tape - Customer Specified": {"editor": "select", "options": ["Yes", "No"]},
    "Bundling": {"editor": "select", "options": ["Yes", "No"]},
    "Crate/ Palletizing": {"editor": "select", "options": ["Crate", "Pallet"]}
}

# Editable table for inputs
st.subheader("📥 Input Data (Fill Below)", divider="grey")
edited_data = st.data_editor(
    input_data,
    column_config=dropdown_columns,
    use_container_width=True,
    num_rows="dynamic",
    key="input_table"
)

# Function to calculate outputs
def calculate_outputs(row):
    W = row["W (mm)"]
    H = row["H (mm)"]
    L = row["L (mm)"]
    finish = row["Finish"]
    fabricated = row["Fabricated"]
    eco_friendly = row["Eco-Friendly Packing"]
    protective_tape_customer_specified = row["Protective Tape - Customer Specified"]
    bundling = row["Bundling"]

    interleaving_material = "Craft Paper" if eco_friendly == "Yes" else "McFoam"
    if finish == "Mill Finish" and interleaving_material == "Craft Paper":
        message = "Okay"
    else:
        message = "Can cause rejects - go ahead with McFoam"

    surface_area = (2 * ((W * L) + (H * L) + (W * H))) / 1_000_000

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

    interleaving_total_cost = surface_area * interleaving_cost

    if protective_tape_customer_specified == "No":
        if (fabricated == "Fabricated" and finish == "Mill Finish") or fabricated == "Just Cutting":
            protective_tape_advice = "OK"
        else:
            protective_tape_advice = "Protective tape required to avoid rejects"
    else:
        protective_tape_advice = "Protective tape required to avoid rejects"

    protective_tape_rate = 100.65
    if protective_tape_advice == "Protective tape required to avoid rejects":
        protective_tape_cost = surface_area * protective_tape_rate
    else:
        protective_tape_cost = 0.0

    return pd.Series({
        "Interleaving Material": interleaving_material,
        "Check": message,
        "Surface Area (m²)": round(surface_area, 4),
        "Cost of Interleaving Material (Rs/m²)": interleaving_cost,
        "Interleaving Cost (Rs)": round(interleaving_total_cost, 2),
        "Protective Tape Advice": protective_tape_advice,
        "Protective Tape Cost (Rs)": round(protective_tape_cost, 2)
    })

# Calculate outputs
st.subheader("📤 Outputs Table", divider="grey")
outputs_df = edited_data.apply(calculate_outputs, axis=1)
st.dataframe(outputs_df, use_container_width=True)

# Bundle stack definition per entry
for i, row in edited_data.iterrows():
    if row["Bundling"] == "Yes":
        st.divider()
        st.subheader(f"📦 Bundle Definition for {row['Identification No.']}")

        num_rows = st.number_input(
            f"Number of Rows (Width direction) - ID {row['Identification No.']}",
            min_value=1,
            step=1,
            key=f"rows_{i}"
        )
        num_layers = st.number_input(
            f"Number of Layers (Height direction) - ID {row['Identification No.']}",
            min_value=1,
            step=1,
            key=f"layers_{i}"
        )

        profile_width_type = st.selectbox(
            f"Width Profile Type - ID {row['Identification No.']}",
            ["W/mm", "H/mm"],
            key=f"width_type_{i}"
        )
        profile_height_type = st.selectbox(
            f"Height Profile Type - ID {row['Identification No.']}",
            ["H/mm", "W/mm"],
            key=f"height_type_{i}"
        )

        profile_dimensions = {"W/mm": row["W (mm)"], "H/mm": row["H (mm)"]}

        bundle_width = num_rows * profile_dimensions[profile_width_type]
        bundle_height = num_layers * profile_dimensions[profile_height_type]
        bundle_length = row["L (mm)"]

        st.markdown("#### 📐 Bundle Dimensions")
        st.write(f"**Bundle Width:** {bundle_width:.2f} mm")
        st.write(f"**Bundle Height:** {bundle_height:.2f} mm")
        st.write(f"**Bundle Length:** {bundle_length:.2f} mm")

        area_covered = 2 * ((bundle_width * bundle_length) + (bundle_height * bundle_length) + (bundle_width * bundle_height)) / 1_000_000
        st.write(f"**Area Covered (m²):** {round(area_covered, 4)}")

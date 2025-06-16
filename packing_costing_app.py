import streamlit as st
import pandas as pd

st.set_page_config(page_title="🎯💰 Targeted Packing Costing", page_icon="🎯💰")
st.title("🎯💰 Targeted Packing Costing App")

# Sample input table
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

dropdown_columns = {
    "Finish": {"editor": "select", "options": ["Mill Finish", "Anodized", "Powder Coated", "Wood Finished"]},
    "Fabricated": {"editor": "select", "options": ["Fabricated", "Just Cutting"]},
    "Eco-Friendly Packing": {"editor": "select", "options": ["Yes", "No"]},
    "Interleaving Required": {"editor": "select", "options": ["Yes", "No"]},
    "Protective Tape - Customer Specified": {"editor": "select", "options": ["Yes", "No"]},
    "Bundling": {"editor": "select", "options": ["Yes", "No"]},
    "Crate/ Palletizing": {"editor": "select", "options": ["Crate", "Pallet"]}
}

st.subheader("📥 Input Table", divider="grey")
edited_data = st.data_editor(
    input_data,
    column_config=dropdown_columns,
    use_container_width=True,
    num_rows="dynamic",
    key="input_table"
)

def calculate_outputs(row):
    W = row["W (mm)"]
    H = row["H (mm)"]
    L = row["L (mm)"]
    finish = row["Finish"]
    fabricated = row["Fabricated"]
    eco_friendly = row["Eco-Friendly Packing"]
    protective_tape_customer_specified = row["Protective Tape - Customer Specified"]

    interleaving_material = "Craft Paper" if eco_friendly == "Yes" else "McFoam"
    message = "Okay" if finish == "Mill Finish" and interleaving_material == "Craft Paper" else "Can cause rejects - go ahead with McFoam"

    surface_area = (2 * ((W * L) + (H * L) + (W * H))) / 1_000_000

    cost_rates = {
        "McFoam": 51.00,
        "Craft Paper": 34.65,
        "Protective Tape": 100.65,
        "Stretchwrap": 14.38
    }
    interleaving_cost = cost_rates.get(interleaving_material, 0.0)
    interleaving_total_cost = surface_area * interleaving_cost

    if protective_tape_customer_specified == "Yes":
        protective_tape_advice = "Protective tape required to avoid rejects"
    elif (fabricated == "Fabricated" and finish == "Mill Finish") or fabricated == "Just Cutting":
        protective_tape_advice = "OK"
    else:
        protective_tape_advice = "Protective tape required to avoid rejects"

    protective_tape_rate = cost_rates["Protective Tape"]
    protective_tape_cost = surface_area * protective_tape_rate if "Protective tape required" in protective_tape_advice else 0.0

    return pd.Series({
        "Interleaving Material": interleaving_material,
        "Check": message,
        "Surface Area (m²)": round(surface_area, 4),
        "Cost of Interleaving Material (Rs/m²)": interleaving_cost,
        "Interleaving Cost (Rs)": round(interleaving_total_cost, 2),
        "Protective Tape Advice": protective_tape_advice,
        "Protective Tape Cost (Rs)": round(protective_tape_cost, 2)
    })

st.subheader("📤 Output Table", divider="grey")
output_table = edited_data.apply(calculate_outputs, axis=1)
st.dataframe(output_table, use_container_width=True)

for i, row in edited_data.iterrows():
    if row["Bundling"] == "Yes":
        st.divider()
        st.subheader(f"📦 Bundle Definition - ID: {row['Identification No.'] or i+1}")

        num_rows = st.number_input(
            f"Number of Rows (Width direction) - ID {i+1}",
            min_value=1,
            step=1,
            key=f"rows_{i}"
        )
        num_layers = st.number_input(
            f"Number of Layers (Height direction) - ID {i+1}",
            min_value=1,
            step=1,
            key=f"layers_{i}"
        )
        profile_width_type = st.selectbox(
            f"Width Profile Type - ID {i+1}",
            ["W/mm", "H/mm"],
            key=f"width_type_{i}"
        )
        profile_height_type = st.selectbox(
            f"Height Profile Type - ID {i+1}",
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

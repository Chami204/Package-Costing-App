import streamlit as st
import pandas as pd

st.set_page_config(page_title="🎯💰 Targeted Packing Costing", page_icon="🎯💰")
st.title("🎯💰 Targeted Packing Costing App")

# Define dropdown options per column
dropdown_options = {
    "Finish": ["Mill Finish", "Anodized", "Powder Coated", "Wood Finished"],
    "Fabricated": ["Fabricated", "Just Cutting"],
    "Eco-Friendly Packing": ["Yes", "No"],
    "Interleaving Required": ["Yes", "No"],
    "Protective Tape - Customer Specified": ["Yes", "No"],
    "Bundling": ["Yes", "No"],
    "Crate/ Palletizing": ["Crate", "Pallet"]
}

# Define column structure and initial row
columns = [
    "Identification No.", "W (mm)", "H (mm)", "L (mm)",
    "Finish", "Fabricated", "Eco-Friendly Packing",
    "Interleaving Required", "Protective Tape - Customer Specified",
    "Bundling", "Crate/ Palletizing"
]
default_row = {
    "Identification No.": "",
    "W (mm)": 0.0,
    "H (mm)": 0.0,
    "L (mm)": 0.0,
    "Finish": "Mill Finish",
    "Fabricated": "Fabricated",
    "Eco-Friendly Packing": "Yes",
    "Interleaving Required": "Yes",
    "Protective Tape - Customer Specified": "No",
    "Bundling": "Yes",
    "Crate/ Palletizing": "Crate"
}

# Initialize editable table
st.subheader("📥 Input Data (Fill Below)", divider="grey")
df_input = pd.DataFrame([default_row])

# Configure dropdowns using st.column_config
column_config = {
    col: st.column_config.SelectboxColumn(col, options=opts)
    for col, opts in dropdown_options.items()
}

editable_data = st.data_editor(
    df_input,
    column_config=column_config,
    use_container_width=True,
    num_rows="dynamic",
    key="input_table"
)

# ---- Calculations ----
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
    message = "Okay" if (finish == "Mill Finish" and interleaving_material == "Craft Paper") else "Can cause rejects - go ahead with McFoam"

    surface_area = (2 * ((W * L) + (H * L) + (W * H))) / 1_000_000

    interleaving_cost = {
        "McFoam": 51.00,
        "Craft Paper": 34.65,
        "Protective Tape": 100.65,
        "Stretchwrap": 14.38
    }.get(interleaving_material, 0.0)

    interleaving_total_cost = surface_area * interleaving_cost

    if protective_tape_customer_specified == "No":
        if (fabricated == "Fabricated" and finish == "Mill Finish") or fabricated == "Just Cutting":
            protective_tape_advice = "OK"
        else:
            protective_tape_advice = "Protective tape required to avoid rejects"
    else:
        protective_tape_advice = "Protective tape required to avoid rejects"

    protective_tape_rate = 100.65
    protective_tape_cost = surface_area * protective_tape_rate if "required" in protective_tape_advice else 0.0

    return pd.Series({
        "Interleaving Material": interleaving_material,
        "Check": message,
        "Surface Area (m²)": round(surface_area, 4),
        "Cost of Interleaving Material (Rs/m²)": interleaving_cost,
        "Interleaving Cost (Rs)": round(interleaving_total_cost, 2),
        "Protective Tape Advice": protective_tape_advice,
        "Protective Tape Cost (Rs)": round(protective_tape_cost, 2)
    })

# Show calculated outputs
st.subheader("📤 Outputs Table", divider="grey")
outputs_df = editable_data.apply(calculate_outputs, axis=1)
st.dataframe(outputs_df, use_container_width=True)

# ---- Bundling Dimensions ----
for i, row in editable_data.iterrows():
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

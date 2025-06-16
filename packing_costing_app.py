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
    "Finish": st.column_config.SelectboxColumn("Finish", options=["Mill Finish", "Anodized", "Powder Coated", "Wood Finished"]),
    "Fabricated": st.column_config.SelectboxColumn("Fabricated", options=["Fabricated", "Just Cutting"]),
    "Eco-Friendly Packing": st.column_config.SelectboxColumn("Eco-Friendly Packing", options=["Yes", "No"]),
    "Interleaving Required": st.column_config.SelectboxColumn("Interleaving Required", options=["Yes", "No"]),
    "Protective Tape - Customer Specified": st.column_config.SelectboxColumn("Protective Tape - Customer Specified", options=["Yes", "No"]),
    "Bundling": st.column_config.SelectboxColumn("Bundling", options=["Yes", "No"]),
    "Crate/ Palletizing": st.column_config.SelectboxColumn("Crate/ Palletizing", options=["Crate", "Pallet"])
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
        "Identification No.": row["Identification No."],
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

# Filter rows where Bundling == "Yes"
bundling_rows = edited_data[edited_data["Bundling"] == "Yes"].copy()

if not bundling_rows.empty:
    st.subheader("📦 Bundle Definition Input Table")
    # Create bundling input dataframe with default values or stored values
    # If running first time, create default columns for bundling inputs
    if "bundling_inputs" not in st.session_state:
        st.session_state.bundling_inputs = pd.DataFrame({
            "Identification No.": bundling_rows["Identification No."],
            "Rows": [1]*len(bundling_rows),
            "Layers": [1]*len(bundling_rows),
            "Width Type": ["W/mm"]*len(bundling_rows),
            "Height Type": ["H/mm"]*len(bundling_rows)
        })

    # Show editable bundling inputs table
    bundling_inputs_edited = st.data_editor(
        st.session_state.bundling_inputs,
        column_config={
            "Identification No.": st.column_config.TextColumn("Identification No.", disabled=True),
            "Rows": st.column_config.NumberColumn("Number of Rows", min_value=1, step=1),
            "Layers": st.column_config.NumberColumn("Number of Layers", min_value=1, step=1),
            "Width Type": st.column_config.SelectboxColumn("Width Profile Type", options=["W/mm", "H/mm"]),
            "Height Type": st.column_config.SelectboxColumn("Height Profile Type", options=["H/mm", "W/mm"]),
        },
        use_container_width=True,
        key="bundling_table"
    )

    # Save edited bundling inputs to session state
    st.session_state.bundling_inputs = bundling_inputs_edited

    # Calculate bundle outputs using bundling inputs + original dimensions
    bundle_output_rows = []
    for _, bundling_row in bundling_inputs_edited.iterrows():
        id_no = bundling_row["Identification No."]
        # Get the corresponding row in edited_data to access W, H, L
        match = edited_data.loc[edited_data["Identification No."] == id_no]
        if match.empty:
            st.warning(f"No matching input found for ID: {id_no}")
            continue
        original_row = match.iloc[0]


        profile_dimensions = {
            "W/mm": original_row["W (mm)"],
            "H/mm": original_row["H (mm)"]
        }

        bundle_width = bundling_row["Rows"] * profile_dimensions[bundling_row["Width Type"]]
        bundle_height = bundling_row["Layers"] * profile_dimensions[bundling_row["Height Type"]]
        bundle_length = original_row["L (mm)"]

        area_covered = 2 * ((bundle_width * bundle_length) + (bundle_height * bundle_length) + (bundle_width * bundle_height)) / 1_000_000

        bundle_output_rows.append({
            "Identification No.": id_no,
            "Rows": bundling_row["Rows"],
            "Layers": bundling_row["Layers"],
            "Width Type": bundling_row["Width Type"],
            "Height Type": bundling_row["Height Type"],
            "Bundle Width (mm)": round(bundle_width, 2),
            "Bundle Height (mm)": round(bundle_height, 2),
            "Bundle Length (mm)": round(bundle_length, 2),
            "Area Covered (m²)": round(area_covered, 4)
        })

    st.subheader("📦 Bundle Dimensions Output Table")
    bundle_df = pd.DataFrame(bundle_output_rows)
    st.dataframe(bundle_df, use_container_width=True)
else:
    st.info("No rows with Bundling = 'Yes' found.")
# Display bundle table if any exist


import streamlit as st
import pandas as pd

st.set_page_config(page_title="🎯💰 Packing Costing App", page_icon="🎯💰")
st.title("🎯💰 Packing Costing App")

# Sample input table for profile data
input_data = pd.DataFrame({
    "Identification No.": [""],
    "W (mm)": [0.0],
    "H (mm)": [0.0],
    "L (mm)": [0.0],
    "Finish": ["Select"],
    "Fabricated": ["Select"],
    "Eco-Friendly Packing": ["Select"],
    "Interleaving Required": ["Select"],
    "Protective Tape - Customer Specified": ["Select"],
    "Bundling": ["Select"],
    "Crate/ Palletizing": ["Select"]
    "Packing Method":["Select"]
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
    "Packing Method":st.column_config.SelectboxColumn("Packing Method", options=["Primary", "Secondary"])
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

    interleaving_material = "Craft Paper" if eco_friendly == "Yes" else "McFoam"
    message = "Okay" if (finish == "Mill Finish" and interleaving_material == "Craft Paper") else "Can cause rejects - go ahead with McFoam"
    surface_area = (2 * ((W * L) + (H * L) + (W * H))) / 1_000_000

    interleaving_cost = {"McFoam": 51.00, "Craft Paper": 34.65, "Protective Tape": 100.65, "Stretchwrap": 14.38}.get(interleaving_material, 0.0)
    interleaving_total_cost = surface_area * interleaving_cost

    if protective_tape_customer_specified == "No":
        if (fabricated == "Fabricated" and finish == "Mill Finish") or (fabricated == "Just Cutting" and finish == "Powder Coated") or (fabricated == "Just Cutting" and finish == "Anodized"):
            protective_tape_advice = "Not necessary."
        else:
            protective_tape_advice = "Protective tape required to avoid rejects"
    else:
        protective_tape_advice = "Protective tape required to avoid rejects"

    protective_tape_cost = surface_area * 100.65 if protective_tape_advice == "Protective tape required to avoid rejects" else 0.0
    
    return pd.Series({
        "Identification No.": row["Identification No."],
        "Interleaving Material": interleaving_material,
        "Check": message,
        "Surface Area (m²)": round(surface_area, 4),
        "Cost of Interleaving Material (Rs/m²)": interleaving_cost,
        "Interleaving Cost (Rs)": round(interleaving_total_cost, 2),
        "Protective Tape Advice": protective_tape_advice,
        "Protective Tape Cost (Rs)": round(protective_tape_cost, 2),
        "Packing Method.": row["Packing Method"],
        
    })

# Calculate outputs
st.subheader("📤 Outputs Table", divider="grey")
outputs_df = edited_data.apply(calculate_outputs, axis=1)
st.dataframe(outputs_df, use_container_width=True)

#-----Primary Packing/ Secondary Packing----





# --- BUNDLING SECTION FIXED ---

# Filter rows where Bundling == "Yes"
bundling_rows = edited_data[edited_data["Bundling"] == "Yes"].copy()

if not bundling_rows.empty:
    st.subheader("📦 Bundle Definition Input Table")

    # Generate updated identification numbers from latest bundling_rows
    id_list = bundling_rows["Identification No."].tolist()

    # Check if bundling_inputs in session state matches updated ID list
    if (
        "bundling_inputs" not in st.session_state
        or sorted(st.session_state.bundling_inputs["Identification No."].tolist()) != sorted(id_list)
    ):
        # Regenerate fresh bundling input table
        st.session_state.bundling_inputs = pd.DataFrame({
            "Identification No.": id_list,
            "Rows": [1] * len(id_list),
            "Layers": [1] * len(id_list),
            "Width Type": ["W/mm"] * len(id_list),
            "Height Type": ["H/mm"] * len(id_list)
        })

    # Show editable bundling inputs
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

    # Save latest edited input
    st.session_state.bundling_inputs = bundling_inputs_edited

    # Process outputs
    bundle_output_rows = []
    for _, bundling_row in bundling_inputs_edited.iterrows():
        id_no = bundling_row["Identification No."]
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


import streamlit as st
import pandas as pd

st.set_page_config(page_title="🎯💰 Targeted Packing Costing", page_icon="🎯💰")
st.title("🎯💰 Targeted Packing Costing App")


# Define columns and initial data row
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



# Input table
st.subheader("📥 Input Data (Fill Below)", divider="grey")
df_input = pd.DataFrame([default_row])

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

# ---- Output Calculation Function ----
def calculate_outputs(row, row_index):
    identification = row["Identification No."]
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

    protective_tape_cost = surface_area * 100.65 if "required" in protective_tape_advice else 0.0

    # Bundle calculation
    if bundling == "Yes":
        num_rows = st.number_input(
            f"Rows (Width) - ID {identification or row_index + 1}", min_value=1, value=1, step=1, key=f"rows_{row_index}"
        )
        num_layers = st.number_input(
            f"Layers (Height) - ID {identification or row_index + 1}", min_value=1, value=1, step=1, key=f"layers_{row_index}"
        )
        width_type = st.selectbox(
            f"Width Profile - ID {identification or row_index + 1}", ["W/mm", "H/mm"], key=f"wtype_{row_index}"
        )
        height_type = st.selectbox(
            f"Height Profile - ID {identification or row_index + 1}", ["H/mm", "W/mm"], key=f"htype_{row_index}"
        )

        dims = {"W/mm": W, "H/mm": H}
        bundle_width = num_rows * dims[width_type]
        bundle_height = num_layers * dims[height_type]
        bundle_length = L
        area_covered = 2 * ((bundle_width * bundle_length) + (bundle_height * bundle_length) + (bundle_width * bundle_height)) / 1_000_000
    else:
        bundle_width = bundle_height = bundle_length = area_covered = 0.0

    return pd.Series({
        "Identification No.": identification,
        "Interleaving Material": interleaving_material,
        "Check": message,
        "Surface Area (m²)": round(surface_area, 4),
        "Cost of Interleaving Material (Rs/m²)": interleaving_cost,
        "Interleaving Cost (Rs)": round(interleaving_total_cost, 2),
        "Protective Tape Advice": protective_tape_advice,
        "Protective Tape Cost (Rs)": round(protective_tape_cost, 2),
        "Bundle Width (mm)": round(bundle_width, 2),
        "Bundle Height (mm)": round(bundle_height, 2),
        "Bundle Length (mm)": round(bundle_length, 2),
        "Bundle Area Covered (m²)": round(area_covered, 4)
    })

# ---- Final Outputs ----
st.subheader("📤 Outputs Table", divider="grey")
outputs_df = pd.concat(
    [calculate_outputs(row, idx) for idx, row in editable_data.iterrows()],
    axis=1
).T.reset_index(drop=True)

st.dataframe(outputs_df, use_container_width=True)

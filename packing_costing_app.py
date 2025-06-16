import streamlit as st
import pandas as pd

# Page config
st.set_page_config(page_title="Targeted Packing Costing", page_icon="🎯💰")
st.title("🎯💰 Targeted Packing Costing App")

st.header("Step 01: Enter Packing Data Table with Dropdowns")

# Define columns and default data
cols = [
    "Identification No.", "W (mm)", "H (mm)", "L (mm)",
    "Finish", "Fabricated", "Eco-Friendly Packing", "Interleaving Required",
    "Protective Tape - Customer Specified", "Bundling", "Crate/ Palletizing"
]
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

input_df = pd.DataFrame(default_data)

# Define column input options
column_config = {
    "Finish": {"editor": "select", "options": ["Mill Finish", "Anodized", "Powder Coated", "Wood Finished"]},
    "Fabricated": {"editor": "select", "options": ["Fabricated", "Just Cutting"]},
    "Eco-Friendly Packing": {"editor": "select", "options": ["Yes", "No"]},
    "Interleaving Required": {"editor": "select", "options": ["Yes", "No"]},
    "Protective Tape - Customer Specified": {"editor": "select", "options": ["Yes", "No"]},
    "Bundling": {"editor": "select", "options": ["Yes", "No"]},
    "Crate/ Palletizing": {"editor": "select", "options": ["Crate", "Pallet"]}
}

# Render editable table with dropdowns
edited = st.data_editor(
    input_df,
    column_config=column_config,
    use_container_width=True,
    num_rows="dynamic"
)

st.header("Step 02: Output Summary")

output_rows = []
for _, row in edited.iterrows():
    W, H, L = row["W (mm)"], row["H (mm)"], row["L (mm)"]
    finish = row["Finish"]
    fabricated = row["Fabricated"]
    eco_friendly = row["Eco-Friendly Packing"]
    specified = row["Protective Tape - Customer Specified"]

    interleaving_material = "Craft Paper" if eco_friendly == "Yes" else "McFoam"
    check = "Okay" if finish == "Mill Finish" and interleaving_material == "Craft Paper" else "Can cause rejects - go ahead with McFoam"
    surface_area = (2 * ((W * L) + (H * L) + (W * H))) / 1e6

    rates = {"McFoam": 51.0, "Craft Paper": 34.65, "Protective Tape": 100.65, "Stretchwrap": 14.38}
    inter_cost_rate = rates[interleaving_material]
    inter_cost = round(surface_area * inter_cost_rate, 2)

    if specified == "No":
        tape_advice = "OK" if ((fabricated == "Fabricated" and finish == "Mill Finish") or fabricated == "Just Cutting") else "Protective tape required to avoid rejects"
    else:
        tape_advice = "Protective tape required as per customer"

    tape_cost = round(surface_area * rates["Protective Tape"], 2) if (specified == "Yes" or "Protective tape required" in tape_advice) else 0.0

    output_rows.append({
        "Identification No.": row["Identification No."],
        "Interleaving Material": interleaving_material,
        "Check": check,
        "Surface Area (m²)": round(surface_area, 4),
        "Interleaving Cost (Rs)": inter_cost,
        "Protective Tape Advice": tape_advice,
        "Protective Tape Cost (Rs)": tape_cost
    })

st.dataframe(
    pd.DataFrame(output_rows).style.set_properties(**{"background-color": "#E6F2FF"}),
    use_container_width=True
)

st.header("Step 03: Bundle Stack (Conditional)")

bundle_outputs = []
for idx, row in edited.iterrows():
    if row["Bundling"] == "Yes":
        st.subheader(f"Bundle Inputs for {row['Identification No.']}")
        nr = st.number_input(f"Rows - {row['Identification No.']}", min_value=1, key=f"nr_{idx}")
        nl = st.number_input(f"Layers - {row['Identification No.']}", min_value=1, key=f"nl_{idx}")
        wt = st.selectbox(f"Width Profile - {row['Identification No.']}", ["W/mm", "H/mm"], key=f"wt_{idx}")
        ht = st.selectbox(f"Height Profile - {row['Identification No.']}", ["H/mm", "W/mm"], key=f"ht_{idx}")

        dims = {"W/mm": row["W (mm)"], "H/mm": row["H (mm)"]}
        bw = nr * dims[wt]
        bh = nl * dims[ht]
        bl = row["L (mm)"]
        area = round(2 * ((bw * bl) + (bh * bl) + (bw * bh)) / 1e6, 4)

        bundle_outputs.append({
            "Identification No.": row["Identification No."],
            "Bundle Width (mm)": bw,
            "Bundle Height (mm)": bh,
            "Bundle Length (mm)": bl,
            "Area Covered (m²)": area
        })

if bundle_outputs:
    st.markdown("### 🟦 Bundle Outputs")
    st.dataframe(
        pd.DataFrame(bundle_outputs).style.set_properties(**{"background-color": "#FFF9C4"}),
        use_container_width=True
    )

import streamlit as st
import pandas as pd
from streamlit_aggrid import AgGrid, GridOptionsBuilder


st.set_page_config(page_title="Packing Costing App", page_icon="📦", layout="wide")
st.title("📦 Packing Costing App with Dropdowns")

st.markdown("### Step 1: Enter Input Data with Dropdowns")

# Create sample DataFrame
df = pd.DataFrame({
    "Identification No.": [""],
    "W (mm)": [0.0],
    "H (mm)": [0.0],
    "L (mm)": [0.0],
    "Finish": [""],
    "Fabricated": [""],
    "Eco-Friendly": [""],
    "Interleaving Required": [""],
    "Protective Tape": [""],
    "Bundling": [""],
    "Crate/Pallet": [""],
})

# Configure AGGrid with dropdowns
gb = GridOptionsBuilder.from_dataframe(df)

dropdown_columns = {
    "Finish": ["Mill Finish", "Anodized", "Powder Coated", "Wood Finished"],
    "Fabricated": ["Fabricated", "Just Cutting"],
    "Eco-Friendly": ["Yes", "No"],
    "Interleaving Required": ["Yes", "No"],
    "Protective Tape": ["Yes", "No"],
    "Bundling": ["Yes", "No"],
    "Crate/Pallet": ["Crate", "Pallet"],
}

for col, options in dropdown_columns.items():
    gb.configure_column(col, editable=True, cellEditor="agSelectCellEditor",
                        cellEditorParams={"values": options})

gb.configure_default_column(editable=True)
grid_options = gb.build()

# Render editable table
grid_response = AgGrid(df, gridOptions=grid_options, editable=True, height=300)
edited_df = grid_response["data"]

st.markdown("### Step 2: Output")

for idx, row in edited_df.iterrows():
    st.markdown(f"#### 📌 Output for ID: {row['Identification No.'] or '(Not Entered)'}")

    # Input values
    try:
        W = float(row["W (mm)"])
        H = float(row["H (mm)"])
        L = float(row["L (mm)"])
    except:
        st.warning("Invalid W, H, or L values.")
        continue

    eco_friendly = row["Eco-Friendly"]
    finish = row["Finish"]
    fabricated = row["Fabricated"]
    protective_tape_customer_specified = row["Protective Tape"]
    bundling = row["Bundling"]

    # Interleaving Material
    interleaving_material = "Craft Paper" if eco_friendly == "Yes" else "McFoam"
    st.write("**Interleaving Material:**", interleaving_material)

    # Check
    if finish == "Mill Finish" and interleaving_material == "Craft Paper":
        st.success("OK")
    else:
        st.error("Can cause rejects - go ahead with McFoam")

    # Surface Area (m²)
    surface_area = (2 * ((W * L) + (H * L) + (W * H))) / 1_000_000
    st.write("**Surface Area (m²):**", round(surface_area, 4))

    # Interleaving Cost
    rates = {
        "McFoam": 51.00,
        "Craft Paper": 34.65,
        "Protective Tape": 100.65,
        "Stretchwrap": 14.38
    }
    interleaving_cost = surface_area * rates.get(interleaving_material, 0)
    st.write("**Interleaving Cost (Rs):**", round(interleaving_cost, 2))

    # Protective Tape Advice
    if protective_tape_customer_specified == "No":
        if (fabricated == "Fabricated" and finish == "Mill Finish") or fabricated == "Just Cutting":
            tape_advice = "OK"
        else:
            tape_advice = "Protective tape required to avoid rejects"
    else:
        tape_advice = "Protective tape required by customer"

    st.write("**Protective Tape Advice:**", tape_advice)

    # Protective Tape Cost
    protective_tape_cost = surface_area * 100.65 if "Protective tape required" in tape_advice else 0
    st.write("**Protective Tape Cost (Rs):**", round(protective_tape_cost, 2))

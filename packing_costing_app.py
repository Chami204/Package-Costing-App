import streamlit as st
import pandas as pd

# Page setup
st.set_page_config(page_title="🎯💰 Packing Costing App", page_icon="🎯💰")
st.title("🎯💰 Packing Costing App")

# ----- PASSWORD-PROTECTED REFERENCE TABLE SETUP -----
EDIT_PASSWORD = "admin123"

if "edit_mode" not in st.session_state:
    st.session_state.edit_mode = False

#----------------Interleaving-------------------------
@st.cache_data
def load_interleaving_table():
    return pd.DataFrame({
        "Material": ["McFoam", "Craft Paper", "Protective Tape", "Stretchwrap"],
        "Cost per m² (LKR)": [51.00, 34.65, 100.65, 14.38]
    })

interleaving_df = load_interleaving_table()
material_cost_lookup = dict(zip(interleaving_df["Material"], interleaving_df["Cost per m² (LKR)"]))

#------------------Polybag-------------------------
@st.cache_data
def load_polybag_table():
    return pd.DataFrame({
        "Polybag Size": ["9 Inch"],
        "Cost per m² (LKR)": [12.8]
    })

polybag_ref = load_polybag_table().iloc[0]
ref_polybag_length = float(polybag_ref["Polybag Size"].split()[0])
polybag_cost_per_m2 = float(polybag_ref["Cost per m² (LKR)"])

#-------------------------------Carboard Box------------------------
@st.cache_data
def load_CardboardBox_table():
    return pd.DataFrame({
        "Width(mm)": ["210"],
        "Height(mm)": ["135"],
        "Length(mm)": ["330"],
        "Cost(LKR)": [205]
    })

cardboard_ref = load_CardboardBox_table().iloc[0]
ref_width = float(cardboard_ref["Width(mm)"])
ref_height = float(cardboard_ref["Height(mm)"])
ref_length = float(cardboard_ref["Length(mm)"])
ref_cost = float(cardboard_ref["Cost(LKR)"])
ref_volume = ref_width * ref_height * ref_length

#---------------------------Stretchwrap------------------------------
@st.cache_data
def load_stretchwrap_table():
    return pd.DataFrame({
        "Area(mm²)": [210000],
        "cost(Rs/mm²)": [135]
    })

stretchwrap_ref = load_stretchwrap_table().iloc[0]
ref_stretch_area = float(stretchwrap_ref["Area(mm²)"])
ref_stretch_cost = float(stretchwrap_ref["cost(Rs/mm²)"])

#----------------------Crate or Pallet Cost reference table---------------------------
@st.cache_data
def load_crate_cost_table():
    return pd.DataFrame({
        "Width (mm)": [480],
        "Height (mm)": [590],
        "Length (mm)": [2000],
        "Cost (LKR)": [5000.0]
    })

@st.cache_data
def load_pallet_cost_table():
    return pd.DataFrame({
        "Width (mm)": [2000],
        "Height (mm)": [600],
        "Cost (LKR)": [3000.0]
    })

crate_cost_df = load_crate_cost_table()
pallet_cost_df = load_pallet_cost_table()

#-------------------------Strapping clips & straps cost------------------------------
@st.cache_data
def load_strapping_cost_table():
    return pd.DataFrame({
        "Strapping Length (m)": [1.0],
        "Cost (LKR/m)": [15.0]
    })

strapping_cost_df = load_strapping_cost_table()

# --------------------------=INPUT TABLE SETUP ------------------------
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
    "Packing Method": ["Primary"]
})

dropdown_columns = {
    "Finish": st.column_config.SelectboxColumn("Finish", options=["Mill Finish", "Anodized", "Powder Coated", "Wood Finished"]),
    "Fabricated": st.column_config.SelectboxColumn("Fabricated", options=["Fabricated", "Just Cutting"]),
    "Eco-Friendly Packing": st.column_config.SelectboxColumn("Eco-Friendly Packing", options=["Yes", "No"]),
    "Interleaving Required": st.column_config.SelectboxColumn("Interleaving Required", options=["Yes", "No"]),
    "Protective Tape - Customer Specified": st.column_config.SelectboxColumn("Protective Tape - Customer Specified", options=["Yes", "No"]),
    "Packing Method": st.column_config.SelectboxColumn("Packing Method", options=["Primary", "Secondary"])
}

edited_data = st.data_editor(
    input_data,
    column_config=dropdown_columns,
    use_container_width=True,
    num_rows="dynamic",
    key="input_table"
)

# ----- COSTING LOGIC -----
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

    interleaving_cost = material_cost_lookup.get(interleaving_material, 0.0)
    interleaving_total_cost = surface_area * interleaving_cost

    if protective_tape_customer_specified == "No":
        if (fabricated == "Fabricated" and finish == "Mill Finish") or (fabricated == "Just Cutting" and finish in ["Powder Coated", "Anodized"]):
            protective_tape_advice = "Not necessary."
        else:
            protective_tape_advice = "Protective tape required to avoid rejects"
    else:
        protective_tape_advice = "Protective tape required to avoid rejects"

    protective_tape_cost = surface_area * material_cost_lookup.get("Protective Tape", 100.65) if protective_tape_advice == "Protective tape required to avoid rejects" else 0.0

    user_volume = W * H * L
    cardboard_cost = (user_volume / ref_volume) * ref_cost if ref_volume else 0.0

    return pd.Series({
        "Identification No.": row["Identification No."],
        "Interleaving Material": interleaving_material,
        "Check": message,
        "Surface Area (m²)": round(surface_area, 4),
        "Cost of Interleaving Material (Rs/m²)": interleaving_cost,
        "Interleaving Cost (Rs)": round(interleaving_total_cost, 2),
        "Protective Tape Advice": protective_tape_advice,
        "Protective Tape Cost (Rs)": round(protective_tape_cost, 2),
        "Cardboard Box Cost (Rs)": round(cardboard_cost, 2)
    })

outputs_df = edited_data.apply(calculate_outputs, axis=1)
st.subheader("📤 Crate/Pallet Input Table", divider="grey")
st.dataframe(outputs_df, use_container_width=True)

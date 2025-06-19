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

#-------------------------------Cardboard Box------------------------
@st.cache_data
def load_CardboardBox_table():
    return pd.DataFrame({
        "Width(mm)": [210],
        "Height(mm)": [135],
        "Length(mm)": [330],
        "Cost(LKR)": [205]
    })

cardboard_ref = load_CardboardBox_table().iloc[0]
ref_volume = float(cardboard_ref["Width(mm)"]) * float(cardboard_ref["Height(mm)"]) * float(cardboard_ref["Length(mm)"])
ref_cost = float(cardboard_ref["Cost(LKR)"])

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

st.subheader("📅 User Input Table", divider="grey")
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

st.subheader("📤 Packing Details", divider="grey")
outputs_df = edited_data.apply(calculate_outputs, axis=1)
st.dataframe(outputs_df, use_container_width=True)

# ----- BUNDLING SECTION -----
bundling_rows = edited_data[edited_data["Packing Method"] == "Secondary"].copy()
if not bundling_rows.empty:
    st.subheader("🛆 Input the data for Secondary Packing (Bundling)")
    id_list = bundling_rows["Identification No."].tolist()

    if ("bundling_inputs" not in st.session_state or
        sorted(st.session_state.bundling_inputs["Identification No."].tolist()) != sorted(id_list)):
        st.session_state.bundling_inputs = pd.DataFrame({
            "Identification No.": id_list,
            "Rows": [1] * len(id_list),
            "Layers": [1] * len(id_list),
            "Width Type": ["W/mm"] * len(id_list),
            "Height Type": ["H/mm"] * len(id_list)
        })

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

    st.session_state.bundling_inputs = bundling_inputs_edited

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

        polybag_cost = (bundle_length / (ref_polybag_length * 25.4)) * polybag_cost_per_m2
        profile_surface_area_mm2 = 2 * ((original_row["W (mm)"] * original_row["L (mm)"]) + (original_row["H (mm)"] * original_row["L (mm)"]) + (original_row["W (mm)"] * original_row["H (mm)"]))
        stretchwrap_cost = (profile_surface_area_mm2 / ref_stretch_area) * ref_stretch_cost if ref_stretch_area else 0.0

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
            "Area Covered (m²)": round(area_covered, 4),
            "Polybag Cost (Rs)": round(polybag_cost, 2),
            "Stretchwrap Cost (Rs)": round(stretchwrap_cost, 2)
        })

    st.subheader("🛆 Secondary Packing (Bundling) Output Table")
    bundle_df = pd.DataFrame(bundle_output_rows)
    st.dataframe(bundle_df, use_container_width=True)
else:
    st.info("No rows with Packing Method = 'Secondary' found.")

# ----- REFERENCE TABLE PASSWORD-PROTECTED EDITING -----
st.subheader("🔐 Admin Reference Tables")
if not st.session_state.edit_mode:
    password = st.text_input("Enter password to edit tables:", type="password")
    if password == EDIT_PASSWORD:
        st.session_state.edit_mode = True
    else:
        st.warning("Read-only mode. Enter correct password to unlock tables.")

tab1, tab2, tab3, tab4 = st.tabs(["📄 Interleaving Cost", "👝 Polybag Cost", "📦 Cardboard Box Cost", "🌀 Stretchwrap Cost"])

with tab1:
    st.markdown("#### Interleaving Material Costs")
    if st.session_state.edit_mode:
        interleaving_df = st.data_editor(interleaving_df, num_rows="dynamic", key="interleaving_table")
    st.dataframe(interleaving_df)

with tab2:
    st.markdown("#### Polybag Cost")
    if st.session_state.edit_mode:
        polybag_ref = st.data_editor(polybag_ref.to_frame().T, num_rows="dynamic", key="polybag_table")
    st.dataframe(polybag_ref.to_frame().T)

with tab3:
    st.markdown("#### Cardboard Box Cost")
    if st.session_state.edit_mode:
        cardboard_ref = st.data_editor(cardboard_ref.to_frame().T, num_rows="dynamic", key="CardboardBox_table")
    st.dataframe(cardboard_ref.to_frame().T)

with tab4:
    st.markdown("#### Stretchwrap Cost")
    if st.session_state.edit_mode:
        stretchwrap_ref = st.data_editor(stretchwrap_ref.to_frame().T, num_rows="dynamic", key="Stretchwrap_Cost_table")
    st.dataframe(stretchwrap_ref.to_frame().T)

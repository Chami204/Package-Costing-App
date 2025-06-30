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
    "SKU No.": [""],
    "W (mm)": [0.0],
    "H (mm)": [0.0],
    "L (mm)": [0.0],
    "Fabricated": ["Select"]
})

dropdown_columns = {
    "Fabricated": st.column_config.SelectboxColumn("Fabricated", options=["Fabricated", "Just Cutting"])
}


# ----- COSTING LOGIC -----
def calculate_outputs(row):
    W = row["W (mm)"]
    H = row["H (mm)"]
    L = row["L (mm)"]
    
st.subheader("📅 SKU Input Table", divider="grey")
edited_data = st.data_editor(
    input_data,
    column_config={
        "Fabricated": st.column_config.SelectboxColumn("Fabricated", options=["Fabricated", "Just Cutting"])
    },
    use_container_width=True,
    num_rows="dynamic",
    key="sku_input_table"
)
# ----- Common Dropdown Selections Outside Table -----
st.subheader("🔹 Common Packing Selections", divider="grey")
finish = st.selectbox("Finish", ["Mill Finish", "Anodized", "Powder Coated", "Wood Finished"], key="finish_option")
eco_friendly = st.selectbox("Eco-Friendly Packing", ["Yes", "No"], key="eco_friendly_option")
interleaving_required = st.selectbox("Interleaving Required", ["Yes", "No"], key="interleaving_option")
protective_tape_customer_specified = st.selectbox("Protective Tape - Customer Specified", ["Yes", "No"], key="tape_option")
packing_method = st.selectbox("Packing Method", ["Primary", "Secondary"], key="packing_option")



# --------- Calculation Logic Hidden Table ------------
def calculate_hidden(row):
    W, H, L = row["W (mm)"], row["H (mm)"], row["L (mm)"]
    interleaving_material = "Craft Paper" if eco_friendly == "Yes" else "McFoam"
    message = "Okay" if (finish == "Mill Finish" and interleaving_material == "Craft Paper") else "Can cause rejects - go ahead with McFoam"
    surface_area = (2 * ((W * L) + (H * L) + (W * H))) / 1_000_000
    interleaving_cost = material_cost_lookup.get(interleaving_material, 0.0)
    interleaving_total_cost = surface_area * interleaving_cost
    if protective_tape_customer_specified == "No":
        if (row["Fabricated"] == "Fabricated" and finish == "Mill Finish") or (row["Fabricated"] == "Just Cutting" and finish in ["Powder Coated", "Anodized"]):
            protective_tape_advice = "Not necessary."
        else:
            protective_tape_advice = "Protective tape required to avoid rejects"
    else:
        protective_tape_advice = "Protective tape required to avoid rejects"
    protective_tape_cost = surface_area * material_cost_lookup.get("Protective Tape", 100.65) if protective_tape_advice == "Protective tape required to avoid rejects" else 0.0
    user_volume = W * H * L
    cardboard_cost = (user_volume / ref_volume) * ref_cost if ref_volume else 0.0
    total = interleaving_total_cost + protective_tape_cost + cardboard_cost
    return pd.Series({
        "SKU": row["SKU No."],
        "Interleaving Cost (Rs)": round(interleaving_total_cost, 2),
        "Protective Tape Cost (Rs)": round(protective_tape_cost, 2),
        "Cardboard Box Cost (Rs)": round(cardboard_cost, 2),
        "Total Cost (Rs)": round(total, 2),
        "Interleaving Material": interleaving_material,
        "Check": message,
        "Protective Tape Advice": protective_tape_advice
    })

hidden_output = edited_data.apply(calculate_hidden, axis=1)

# ----------- Primary Costing Table -------------------
st.subheader("💼 Primary Packing Total Cost")
primary_output = hidden_output[[
    "SKU",
    "Interleaving Cost (Rs)",
    "Protective Tape Cost (Rs)",
    "Cardboard Box Cost (Rs)",
    "Total Cost (Rs)"
]]
st.dataframe(primary_output, use_container_width=True)

# ----------- Special Comments Section ----------------

from streamlit_extras.let_it_rain import rain
st.subheader("🌟 Special Comments")

with st.container():
    st.markdown("**🔗 Packing Method Note**")
    if packing_method == "Primary":
        st.info(f"Costing is done according to *{packing_method}* packing. Therefore, this cost does not include any crate or palletizing charges. Please note that secondary packaging will incur an additional charge.")
    else:
        user_comment = st.text_area("Add additional comments (for Secondary):", "")
        st.info(f"Costing is done according to *{packing_method}* packing. {user_comment}")

    if not hidden_output.empty:
        mat = hidden_output.iloc[0]["Interleaving Material"]
        msg = hidden_output.iloc[0]["Check"]
        tape = hidden_output.iloc[0]["Protective Tape Advice"]
        st.success(f"The interleaving material is **{mat}**. {msg}")
        st.warning(f"{tape}")
        st.markdown( """
        <div style='background-color:#e1f5fe; padding:10px; border-radius:5px;'>
            Costing is only inclusive of interleaving required & Cardboard Box/Polybag.
        </div>
        """,
        unsafe_allow_html=True)



# ----------------- Final Packing --------------------
final_packing_input = pd.DataFrame({
    "Final Packing Method": ["Crate"],
    "Width (mm)": [0],
    "Height (mm)": [0],
    "Length (mm)": [0]
})

st.subheader("🚛 Final Packing Selection", divider="grey")
final_packing_selection = st.data_editor(
    final_packing_input,
    column_config={
        "Final Packing Method": st.column_config.SelectboxColumn("Final Packing Method", options=["Crate", "Pallet"])
    },
    use_container_width=True,
    key="final_packing_selection"
)

st.subheader("💰 Final Crate/Pallet Cost Summary", divider="grey")
packing_output_rows = []

for _, row in final_packing_selection.iterrows():
    method = row["Final Packing Method"]
    width = row["Width (mm)"]
    height = row["Height (mm)"]
    length = row["Length (mm)"]

    if method == "Crate":
        ref_crate = crate_cost_df.iloc[0]
        ref_vol = ref_crate["Width (mm)"] * ref_crate["Height (mm)"] * ref_crate["Length (mm)"]
        user_vol = width * height * length
        cost = (user_vol / ref_vol) * ref_crate["Cost (LKR)"] if ref_vol else 0.0

        strapping_ref = strapping_cost_df.iloc[0]
        length_m = length / 1000
        num_clips = length_m / 0.5
        strapping_cost = length_m * strapping_ref["Cost (LKR/m)"] * num_clips

    elif method == "Pallet":
        ref_pallet = pallet_cost_df.iloc[0]
        ref_area = ref_pallet["Width (mm)"] * ref_pallet["Height (mm)"]
        user_area = width * height
        cost = (user_area / ref_area) * ref_pallet["Cost (LKR)"] if ref_area else 0.0
        strapping_cost = 0.0
        num_clips = 0

    packing_output_rows.append({
        "Method": method,
        "Width (mm)": width,
        "Height (mm)": height,
        "Length (mm)": length if method == "Crate" else "-",
        "Packing Cost (LKR)": round(cost, 2),
        "Strapping Clips": round(num_clips, 2) if method == "Crate" else "-",
        "Strapping Cost (LKR)": round(strapping_cost, 2) if method == "Crate" else "-"
    })

st.dataframe(pd.DataFrame(packing_output_rows), use_container_width=True)

# ----- BUNDLING SECTION (FOR SECONDARY PACKING ONLY) ------------------------------------

if packing_method == "Secondary":
    st.subheader("📦 Input the data for Secondary Packing (Bundling)")
    bundling_data = pd.DataFrame({
        "Rows": [1],
        "Layers": [1],
        "Width Type": ["W/mm"],
        "Height Type": ["H/mm"]
    })

    bundling_common = st.data_editor(
        bundling_data,
        column_config={
            "Rows": st.column_config.NumberColumn("Number of Rows", min_value=1, step=1),
            "Layers": st.column_config.NumberColumn("Number of Layers", min_value=1, step=1),
            "Width Type": st.column_config.SelectboxColumn("Width Profile Type", options=["W/mm", "H/mm"]),
            "Height Type": st.column_config.SelectboxColumn("Height Profile Type", options=["H/mm", "W/mm"]),
        },
        use_container_width=True,
        key="bundling_common_input"
    )

    bundle_output_rows = []
    for _, data_row in edited_data.iterrows():
        profile_dimensions = {
            "W/mm": data_row["W (mm)"],
            "H/mm": data_row["H (mm)"]
        }
        W = float(data_row["W (mm)"])
        H = float(data_row["H (mm)"])
        L = float(data_row["L (mm)"])
        
        rows = bundling_common.loc[0, "Rows"]
        layers = bundling_common.loc[0, "Layers"]
        width_type = bundling_common.loc[0, "Width Type"]
        height_type = bundling_common.loc[0, "Height Type"]
    
        bundle_width = rows * profile_dimensions[width_type]
        bundle_height = layers * profile_dimensions[height_type]
        bundle_length = L
    
        # Polybag cost
        polybag_cost = (bundle_length / (ref_polybag_length * 25.4)) * polybag_cost_per_m2  # inch to mm
    
        # Surface area of single profile for stretchwrap calc
        profile_surface_area = 2 * ((W * L) + (H * L) + (W * H))
        stretchwrap_cost = (profile_surface_area / ref_stretch_area) * ref_stretch_cost if ref_stretch_area else 0.0
    
        # Bundle area covered (approx)
        area_covered = 2 * ((bundle_width * bundle_length) + (bundle_height * bundle_length) + (bundle_width * bundle_height)) / 1_000_000
    
        bundle_output_rows.append({
            "SKU": data_row["SKU No."],
            "Bundle Width (mm)": round(bundle_width, 2),
            "Bundle Height (mm)": round(bundle_height, 2),
            "Bundle Length (mm)": round(bundle_length, 2),
            "Area Covered (m²)": round(area_covered, 4),
            "Polybag Cost (Rs)": round(polybag_cost, 2),
            "Stretchwrap Cost (Rs)": round(stretchwrap_cost, 2)
        })


    
# ---------------- Final Visible Secondary Packing Cost ----------------

    st.subheader("📦 Secondary Packing Cost")
    secondary_cost_df = pd.DataFrame(bundle_output_rows)
    secondary_cost_df["Total Cost (Rs/Pc)"] = secondary_cost_df.iloc[:, 4:].sum(axis=1)
    st.dataframe(secondary_cost_df, use_container_width=True)



# ----------------- Tabs for Reference Tables --------------------
st.subheader("🔐 Admin Reference Tables")
if not st.session_state.edit_mode:
    password = st.text_input("Enter password to edit tables:", type="password")
    if password == EDIT_PASSWORD:
        st.session_state.edit_mode = True
    else:
        st.warning("Read-only mode. Enter correct password to unlock tables.")

tab1, tab2, tab3, tab4, tab5, tab6, tab7 = st.tabs([
    "📄 Interleaving Cost", 
    "👝 Polybag Cost", 
    "📦 Cardboard Box Cost", 
    "🌀 Stretchwrap Cost",
    "📏 Crate Cost", 
    "📐 Pallet Cost", 
    "🧷 PP Strapping Cost"
])

with tab1:
    st.markdown("#### Interleaving Material Costs")
    if st.session_state.edit_mode:
        interleaving_df = st.data_editor(interleaving_df, num_rows="dynamic", key="interleaving_table")
    st.dataframe(interleaving_df)

with tab2:
    st.markdown("#### Polybag Cost")
    if st.session_state.edit_mode:
        polybag_ref = st.data_editor(polybag_ref, num_rows="dynamic", key="polybag_table")
    st.dataframe(polybag_ref)

with tab3:
    st.markdown("#### Cardboard Box Cost")
    if st.session_state.edit_mode:
        cardboard_ref = st.data_editor(cardboard_ref, num_rows="dynamic", key="CardboardBox_table")
    st.dataframe(cardboard_ref)

with tab4:
    st.markdown("#### Stretchwrap Cost")
    if st.session_state.edit_mode:
        stretchwrap_ref = st.data_editor(stretchwrap_ref, num_rows="dynamic", key="Stretchwrap_Cost_table")
    st.dataframe(stretchwrap_ref)

with tab5:
    st.markdown("#### Crate Cost Reference")
    if st.session_state.edit_mode:
        crate_cost_df = st.data_editor(crate_cost_df, num_rows="dynamic", key="crate_cost_edit")
    st.dataframe(crate_cost_df)

with tab6:
    st.markdown("#### Pallet Cost Reference")
    if st.session_state.edit_mode:
        pallet_cost_df = st.data_editor(pallet_cost_df, num_rows="dynamic", key="pallet_cost_edit")
    st.dataframe(pallet_cost_df)

with tab7:
    st.markdown("#### PP Strapping Cost Reference")
    if st.session_state.edit_mode:
        strapping_cost_df = st.data_editor(strapping_cost_df, num_rows="dynamic", key="strapping_cost_edit")
    st.dataframe(strapping_cost_df)

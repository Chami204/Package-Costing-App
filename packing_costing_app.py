import streamlit as st
import pandas as pd

# Page setup
st.set_page_config(layout="wide", page_title="🎯💰 Packing Costing App", page_icon="🎯💰")
st.title("🎯💰 Packing Costing App")
# Custom CSS for wrapping column headers
st.markdown("""
    <style>
    thead tr th div {
        white-space: break-spaces !important;
        text-align: center;
    }
    </style>
    """, unsafe_allow_html=True)


# ----- PASSWORD-PROTECTED REFERENCE TABLE SETUP -----
EDIT_PASSWORD = "admin123"

if "edit_mode" not in st.session_state:
    st.session_state.edit_mode = False

if "save_clicked" not in st.session_state:
    st.session_state.save_clicked = False


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
eco_friendly = st.selectbox("Eco-Friendly Packing", ["McFoam", "Stretchwrap","Craft Paper"], key="eco_friendly_option")
protective_tape_customer_specified = st.selectbox("Protective Tape - Customer Specified", ["Yes", "No"], key="tape_option")
packing_method = st.selectbox("Packing Method", ["Primary", "Secondary"], key="packing_option")


# --------- Calculation Logic Hidden Table ------------
def calculate_hidden(row):
    W = float(row["W (mm)"])
    H = float(row["H (mm)"])
    L = float(row["L (mm)"])
    
    message = "Okay" if (finish == "Mill Finish" and eco_friendly == "Craft Paper") else "Can cause rejects - go ahead with McFoam"
    surface_area = (2 * ((W * L) + (H * L) + (W * H))) / 1000000
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
        "Interleaving Cost (Rs)": f"{interleaving_total_cost:.2f}",
        "Protective Tape Cost (Rs)": f"{protective_tape_cost:.2f}",
        "Cardboard Box Cost (Rs)": f"{cardboard_cost:.2f}",
        "Total Cost (Rs)": f"{total:.2f}",
        "Interleaving Material": interleaving_material,
        "Check": message,
        "Protective Tape Advice": protective_tape_advice
    })

if not edited_data.empty:
    hidden_output = edited_data.apply(calculate_hidden, axis=1)
else:
    hidden_output = pd.DataFrame()

# ----------- Primary Costing Table -------------------
st.subheader("💼 Primary Packing Total Cost")
if not hidden_output.empty:
    primary_output = hidden_output[[
        "SKU",
        "Interleaving Cost (Rs)",
        "Protective Tape Cost (Rs)",
        "Cardboard Box Cost (Rs)",
        "Total Cost (Rs)"
    ]]
    st.dataframe(primary_output, use_container_width=True)
else:
    st.warning("No data to display. Please add SKU information.")

# ----------- Special Comments Section ----------------

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
        st.markdown("""
        <div style='background-color:#e1f5fe; padding:10px; border-radius:5px;'>
            Costing is only inclusive of interleaving required & Cardboard Box/Polybag.
        </div>
        """,
        unsafe_allow_html=True)


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
            "W/mm": float(data_row["W (mm)"]),
            "H/mm": float(data_row["H (mm)"])
        }
        W = float(data_row["W (mm)"])
        H = float(data_row["H (mm)"])
        L = float(data_row["L (mm)"])
        
        rows = int(bundling_common.loc[0, "Rows"])
        layers = int(bundling_common.loc[0, "Layers"])
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

        # Get McFoam cost per m² from interleaving_df
        mcfoam_cost_per_m2 = interleaving_df.loc[interleaving_df["Material"] == "McFoam", "Cost per m² (LKR)"].values[0]
        
        # Calculate McFoam Cost
        McFoam_Cost = area_covered * mcfoam_cost_per_m2
        
        bundle_output_rows.append({
            "SKU": data_row["SKU No."],
            "Bundle Width (mm)": f"{bundle_width:.2f}",
            "Bundle Height (mm)": f"{bundle_height:.2f}",
            "Bundle Length (mm)": f"{bundle_length:.2f}",
            "Area Covered (m²)": f"{area_covered:.2f}",
            "Polybag Cost (Rs)": f"{polybag_cost:.2f}",
            "McFoam_Cost(Rs)": f"{McFoam_Cost:.2f}",
            "Stretchwrap Cost (Rs)": f"{stretchwrap_cost:.2f}"
        })


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
    width = float(row["Width (mm)"])
    height = float(row["Height (mm)"])
    length = float(row["Length (mm)"]) if method == "Crate" else 0

    if method == "Crate":
        ref_crate = crate_cost_df.iloc[0]
        ref_vol = float(ref_crate["Width (mm)"]) * float(ref_crate["Height (mm)"]) * float(ref_crate["Length (mm)"])
        user_vol = width * height * length
        cost = (user_vol / ref_vol) * float(ref_crate["Cost (LKR)"]) if ref_vol else 0.0

        strapping_ref = strapping_cost_df.iloc[0]
        length_m = length / 1000
        num_clips = length_m / 0.5
        strapping_cost = length_m * float(strapping_ref["Cost (LKR/m)"]) * num_clips

    elif method == "Pallet":
        ref_pallet = pallet_cost_df.iloc[0]
        ref_area = float(ref_pallet["Width (mm)"]) * float(ref_pallet["Height (mm)"])
        user_area = width * height
        cost = (user_area / ref_area) * float(ref_pallet["Cost (LKR)"]) if ref_area else 0.0
        strapping_cost = 0.0
        num_clips = 0

    packing_output_rows.append({
        "Method": method,
        "Width (mm)": f"{width:.2f}",
        "Height (mm)": f"{height:.2f}",
        "Length (mm)": f"{length:.2f}" if method == "Crate" else "-",
        "Packing Cost (LKR)": f"{cost:.2f}",
        "Strapping Clips": f"{num_clips:.2f}" if method == "Crate" else "-",
        "Strapping Cost (LKR)": f"{strapping_cost:.2f}" if method == "Crate" else "-"
    })

if packing_output_rows:
    st.dataframe(pd.DataFrame(packing_output_rows), use_container_width=True)
else:
    st.warning("No packing method selected or data available")
    
    # ---------------- Final Visible Secondary Packing Cost ----------------
    st.subheader("📦 Secondary Packing Cost")
    if bundle_output_rows:
        secondary_cost_df = pd.DataFrame(bundle_output_rows)
        secondary_cost_df["Total Cost (Rs/Pc)"] = secondary_cost_df.iloc[:, 4:].sum(axis=1)
        st.dataframe(secondary_cost_df, use_container_width=True)
    else:
        st.warning("No bundle data available")

    # ----------- Special Comments Section for Bundling----------------
    st.subheader("🌟 Special Comments under Secondary Packing")

    with st.container():
        st.markdown("**🔗 Packing Method Note**")
        st.info(f"Costing is done according to *{packing_method}* packing.")

        if not hidden_output.empty:
            mat = hidden_output.iloc[0]["Interleaving Material"]
            msg = hidden_output.iloc[0]["Check"]
            tape = hidden_output.iloc[0]["Protective Tape Advice"]
            st.success(f"The interleaving material is **{mat}**. {msg}")
            st.warning(f"{tape}")
            st.markdown("""
            <div style='background-color:#e1f5fe; padding:10px; border-radius:5px;'>
                Costing is inclusive of secondary packing - pallet or crate, however it is not inclusive of any labels artwork these will incur an additional charge.
            </div>
            """,
            unsafe_allow_html=True)


# ----------------- Tabs for Reference Tables --------------------
st.subheader("🔐 Admin Reference Tables")

col1, col2 = st.columns([3, 1])  # Wider left, button on right
with col1:
    if not st.session_state.edit_mode:
        password = st.text_input("Enter password to edit tables:", type="password")
        if password == EDIT_PASSWORD:
            st.session_state.edit_mode = True
            st.session_state.save_clicked = False
        else:
            st.warning("Read-only mode. Enter correct password to unlock tables.")
with col2:
    if st.session_state.edit_mode:
        if st.button("💾 Save All Tables", use_container_width=True):
            # Simulate saving logic
            st.success("All tables saved!")
            st.session_state.edit_mode = False
            st.session_state.save_clicked = True

#----------------------------------------Final tabs-----------------------------------------------

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
        interleaving_df = st.data_editor(interleaving_df, num_rows="dynamic", key="edit_interleaving")
    st.dataframe(interleaving_df)

with tab2:
    st.markdown("#### Polybag Cost")
    if st.session_state.edit_mode:
        polybag_ref = st.data_editor(polybag_ref.to_frame().T, num_rows="dynamic", key="edit_polybag_table")
    st.dataframe(polybag_ref)

with tab3:
    st.markdown("#### Cardboard Box Cost")
    if st.session_state.edit_mode:
        cardboard_ref = st.data_editor(cardboard_ref.to_frame().T, num_rows="dynamic", key="edit_CardboardBox_table")
    st.dataframe(cardboard_ref)

with tab4:
    st.markdown("#### Stretchwrap Cost")
    if st.session_state.edit_mode:
        stretchwrap_ref = st.data_editor(stretchwrap_ref.to_frame().T, num_rows="dynamic", key="edit_Stretchwrap_Cost_table")
    st.dataframe(stretchwrap_ref)

with tab5:
    st.markdown("#### Crate Cost Reference")
    if st.session_state.edit_mode:
        crate_cost_df = st.data_editor(crate_cost_df, num_rows="dynamic", key="edit_crate_cost_edit")
    st.dataframe(crate_cost_df)

with tab6:
    st.markdown("#### Pallet Cost Reference")
    if st.session_state.edit_mode:
        pallet_cost_df = st.data_editor(pallet_cost_df, num_rows="dynamic", key="edit_pallet_cost_edit")
    st.dataframe(pallet_cost_df)

with tab7:
    st.markdown("#### PP Strapping Cost Reference")
    if st.session_state.edit_mode:
        strapping_cost_df = st.data_editor(strapping_cost_df, num_rows="dynamic", key="edit_strapping_cost_edit")
    st.dataframe(strapping_cost_df)

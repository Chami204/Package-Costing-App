# Final Packing Costing App with All Requested Changes
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

# --------- Load Reference Tables ---------
@st.cache_data
def load_interleaving_table():
    return pd.DataFrame({
        "Material": ["McFoam", "Craft Paper", "Protective Tape", "Stretchwrap"],
        "Cost per m² (LKR)": [51.00, 34.65, 100.65, 14.38]
    })

@st.cache_data
def load_polybag_table():
    return pd.DataFrame({"Polybag Size": ["9 Inch"], "Cost per m² (LKR/m²)": [12.8]})

@st.cache_data
def load_cardboard_table():
    return pd.DataFrame({"Width(mm)": [210], "Height(mm)": [135], "Length(mm)": [330], "Cost(LKR)": [205]})

@st.cache_data
def load_stretchwrap_table():
    return pd.DataFrame({"Area(mm²)": [210000], "cost(Rs/mm²)": [135]})

@st.cache_data
def load_crate_table():
    return pd.DataFrame({"Width (mm)": [480], "Height (mm)": [590], "Length (mm)": [2000], "Cost (LKR)": [5000.0]})

@st.cache_data
def load_pallet_table():
    return pd.DataFrame({"Width (mm)": [2000], "Height (mm)": [600], "Cost (LKR)": [3000.0]})

@st.cache_data
def load_strapping_table():
    return pd.DataFrame({"Strapping Length (m)": [1.0], "Cost (LKR/m)": [15.0]})

interleaving_df = load_interleaving_table()
material_cost_lookup = dict(zip(interleaving_df["Material"], interleaving_df["Cost per m² (LKR)"]))

polybag_ref = load_polybag_table().iloc[0]
ref_polybag_length = float(polybag_ref["Polybag Size"].split()[0])
polybag_cost_per_m2 = float(polybag_ref["Cost per m² (LKR/m²)"])

cardboard_ref = load_cardboard_table().iloc[0]
ref_volume = cardboard_ref["Width(mm)"] * cardboard_ref["Height(mm)"] * cardboard_ref["Length(mm)"]
ref_cost = cardboard_ref["Cost(LKR)"]

stretchwrap_ref = load_stretchwrap_table().iloc[0]
ref_stretch_area = stretchwrap_ref["Area(mm²)"]
ref_stretch_cost = stretchwrap_ref["cost(Rs/mm²)"]

crate_cost_df = load_crate_table()
pallet_cost_df = load_pallet_table()
strapping_cost_df = load_strapping_table()

# ----- SKU Input -----
input_data = pd.DataFrame({"SKU No.": [""], "W (mm)": [0.0], "H (mm)": [0.0], "L (mm)": [0.0], "Fabricated": ["Select"]})
st.subheader("📅 SKU Input Table", divider="grey")
edited_data = st.data_editor(
    input_data,
    column_config={"Fabricated": st.column_config.SelectboxColumn("Fabricated", options=["Fabricated", "Just Cutting"])},
    use_container_width=True,
    num_rows="dynamic",
    key="sku_input_table"
)

# ----- Common Packing Selections -----
st.subheader("🔹 Common Packing Selections", divider="grey")
finish = st.selectbox("Finish", ["Mill Finish", "Anodized", "Powder Coated", "Wood Finished"], key="finish_option")
interleaving_required = st.selectbox("Interleaving Required", ["Yes", "No"], key="interleaving_option")

# Show Eco-Friendly Packing option only if interleaving is Yes
eco_options = ["McFoam", "Stretchwrap", "Craft Paper"] if interleaving_required == "Yes" else ["None"]
eco_friendly_material = st.selectbox("Eco-Friendly Material", eco_options, key="eco_material_option")

protective_tape_required = st.selectbox("Protective Tape - Customer Specified", ["Yes", "No"], key="tape_option")
packing_method = st.selectbox("Packing Method", ["Primary", "Secondary"], key="packing_option")

# ----- Calculate Primary Costing Table -----
st.subheader("💼 Primary Packing Total Cost")

if not edited_data.empty:
    output_rows = []
    for _, row in edited_data.iterrows():
        W = float(row["W (mm)"])
        H = float(row["H (mm)"])
        L = float(row["L (mm)"])
        fabricated = row["Fabricated"]
        surface_area = (2 * ((W * L) + (H * L) + (W * H))) / 1_000_000
        profile_length = L

        # Determine if Polybag or Cardboard
        if profile_length > 550:
            polybag_cost = (polybag_cost_per_m2 * profile_length) / 1  # Single profile
            cardboard_cost = 0.0
        else:
            volume = W * H * L
            cardboard_cost = (volume / ref_volume) * ref_cost if ref_volume else 0.0
            polybag_cost = 0.0

        interleaving_cost = 0.0
        if interleaving_required == "Yes" and eco_friendly_material in material_cost_lookup:
            interleaving_rate = material_cost_lookup[eco_friendly_material]
            interleaving_cost = surface_area * interleaving_rate

        tape_cost = 0.0
        if protective_tape_required == "Yes" or finish == "Anodized" or fabricated == "Fabricated":
            tape_cost = surface_area * material_cost_lookup.get("Protective Tape", 100.65)

        total = interleaving_cost + tape_cost + cardboard_cost + polybag_cost

        output_rows.append({
            "SKU": row["SKU No."],
            "Interleaving Cost (Rs)": f"{interleaving_cost:.2f}",
            "Protective Tape Cost (Rs)": f"{tape_cost:.2f}",
            "Cardboard Cost (Rs)": f"{cardboard_cost:.2f}",
            "Polybag Cost (Rs)": f"{polybag_cost:.2f}",
            "Total Primary Cost (Rs)": f"{total:.2f}"
        })

    primary_df = pd.DataFrame(output_rows)
    st.dataframe(primary_df, use_container_width=True)
else:
    st.warning("No SKU data available")

# -------------------------- Placeholders for next stages -------------------------
st.subheader("🔧 Further Implementation")
st.markdown("The logic for Secondary Packing Cost (bundling via layer/size mode), McFoam, Stretchwrap cost calculations, and final cost summaries will be implemented next.")


# Final Packing Costing App - Bundling Logic Implemented
import streamlit as st
import pandas as pd
import math

# ... [PREVIOUS LOADED TABLES AND PRIMARY SECTION OMITTED FOR BREVITY - already loaded above] ...

# ------------------ Secondary Packing Section ------------------
if packing_method == "Secondary" and not edited_data.empty:
    st.subheader("📦 Input for Secondary Packing (Bundling)")

    bundling_mode = st.radio("What is your input mode for bundle creation?", ["Number of layers", "Size of the bundle"], index=0)

    bundling_input = {}
    if bundling_mode == "Number of layers":
        bundling_input["Rows"] = st.number_input("Number of Rows", min_value=1, value=1)
        bundling_input["Layers"] = st.number_input("Number of Layers", min_value=1, value=1)
        bundling_input["Width Type"] = st.selectbox("Width Type", ["W/mm", "H/mm"])
        bundling_input["Height Type"] = st.selectbox("Height Type", ["H/mm", "W/mm"])
    else:
        bundling_input["Bundle Width"] = st.number_input("Bundle Width (mm)", min_value=100)
        bundling_input["Bundle Height"] = st.number_input("Bundle Height (mm)", min_value=100)
        bundling_input["Bundle Length"] = st.number_input("Bundle Length (mm)", min_value=100)

    # Calculate bundling data
    bundle_rows = []
    for _, row in edited_data.iterrows():
        W = float(row["W (mm)"])
        H = float(row["H (mm)"])
        L = float(row["L (mm)"])
        fabricated = row["Fabricated"]

        profile_surface_area = (2 * ((W * L) + (H * L) + (W * H))) / 1_000_000
        profile_volume = W * H * L

        if bundling_mode == "Number of layers":
            rows = bundling_input["Rows"]
            layers = bundling_input["Layers"]
            width_type = bundling_input["Width Type"]
            height_type = bundling_input["Height Type"]

            profile_w = W if width_type == "W/mm" else H
            profile_h = H if height_type == "H/mm" else W

            bundle_width = rows * profile_w
            bundle_height = layers * profile_h
            bundle_length = L

            profiles_per_bundle = rows * layers  # 1 profile per row-layer pair

        else:
            bundle_width = bundling_input["Bundle Width"]
            bundle_height = bundling_input["Bundle Height"]
            bundle_length = bundling_input["Bundle Length"]

            profiles_per_width = math.floor(bundle_width / W)
            profiles_per_height = math.floor(bundle_height / H)
            profiles_per_length = math.floor(bundle_length / L)
            profiles_per_bundle = profiles_per_width * profiles_per_height * profiles_per_length

            if profiles_per_bundle == 0:
                profiles_per_bundle = 1  # Fallback to avoid division by zero

        # Area of bundle for wrapping
        bundle_area = (2 * ((bundle_width * bundle_length) + (bundle_height * bundle_length) + (bundle_width * bundle_height))) / 1_000_000

        # Polybag cost (per m² * profile length / count)
        polybag_cost_per_bundle = (polybag_cost_per_m2 * L) / profiles_per_bundle

        # Stretchwrap cost
        stretch_cost = (bundle_area / (ref_stretch_area / 1_000_000)) * ref_stretch_cost

        # McFoam cost if required (same as interleaving)
        mcfoam_cost = 0.0
        if interleaving_required == "Yes" and eco_friendly_material == "McFoam":
            mcfoam_cost = bundle_area * material_cost_lookup["McFoam"]

        # Tape cost (based on profile count if required)
        tape_cost = 0.0
        if protective_tape_required == "Yes" or finish == "Anodized" or fabricated == "Fabricated":
            tape_cost = profile_surface_area * material_cost_lookup["Protective Tape"] * profiles_per_bundle

        total_bundle_cost = polybag_cost_per_bundle * profiles_per_bundle + stretch_cost + mcfoam_cost + tape_cost
        cost_per_profile = total_bundle_cost / profiles_per_bundle

        bundle_rows.append({
            "SKU": row["SKU No."],
            "Profiles per Bundle": profiles_per_bundle,
            "Bundle Area (m²)": f"{bundle_area:.2f}",
            "Polybag Cost (Rs)": f"{polybag_cost_per_bundle * profiles_per_bundle:.2f}",
            "McFoam Cost (Rs)": f"{mcfoam_cost:.2f}",
            "Stretchwrap Cost (Rs)": f"{stretch_cost:.2f}",
            "Tape Cost (Rs)": f"{tape_cost:.2f}",
            "Total Bundle Cost (Rs)": f"{total_bundle_cost:.2f}",
            "Cost per Profile (Rs)": f"{cost_per_profile:.2f}"
        })

    # Show bundling result
    if bundle_rows:
        bundling_df = pd.DataFrame(bundle_rows)
        st.subheader("📦 Secondary Packing Cost (Bundling)")
        st.dataframe(bundling_df, use_container_width=True)
    else:
        st.warning("No bundling data available.")




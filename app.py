import streamlit as st
import pandas as pd
import numpy as np

# Set page configuration
st.set_page_config(
    page_title="Packing Costing Calculator",
    page_icon="📦",
    layout="wide"
)

# App title
st.title("📦 Packing Costing Calculator")

# Initialize session state for shared data
if 'sku_data_primary' not in st.session_state:
    sku_columns = ["SKU No", "Width/mm", "Height/mm", "Length/mm", "Comment on fabrication"]
    st.session_state.sku_data_primary = pd.DataFrame(columns=sku_columns)

if 'sku_data_secondary' not in st.session_state:
    st.session_state.sku_data_secondary = pd.DataFrame(columns=sku_columns)

if 'material_costs' not in st.session_state:
    st.session_state.material_costs = pd.DataFrame({
        "Material": ["McFoam", "Craft Paper", "Protective Tape", "Stretchwrap"],
        "Cost/ m²": [51.00, 34.65, 100.65, 14.38]
    })

if 'box_costs' not in st.session_state:
    st.session_state.box_costs = pd.DataFrame({
        "Length(mm)": [330],
        "Width (mm)": [210],
        "Height (mm)": [135],
        "Cost (LKR)": [205.00]
    })

# Create tabs
tab1, tab2 = st.tabs(["Primary Calculations", "Secondary Calculations"])

with tab1:
    st.header("Primary Calculations")
    
    # Sub topic 1 - SKU Table with dimensions
    st.subheader("SKU Table with dimensions")
    
    # Create editable dataframe for SKU input
    edited_sku_df = st.data_editor(
        st.session_state.sku_data_primary,
        num_rows="dynamic",
        use_container_width=True,
        column_config={
            "SKU No": st.column_config.TextColumn("SKU No", required=True),
            "Width/mm": st.column_config.NumberColumn("Width/mm", required=True, min_value=0),
            "Height/mm": st.column_config.NumberColumn("Height/mm", required=True, min_value=0),
            "Length/mm": st.column_config.NumberColumn("Length/mm", required=True, min_value=0),
            "Comment on fabrication": st.column_config.SelectboxColumn(
                "Comment on fabrication",
                options=["Fabricated", "Just Cutting"],
                required=True
            )
        },
        key="sku_editor_primary"
    )
    
    # Update session state with edited data
    st.session_state.sku_data_primary = edited_sku_df
    
    st.divider()
    
    # Section 2: Common Packing selections
    st.subheader("Common Packing Selections")
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        finish = st.selectbox(
            "Finish",
            ["Mill Finish", "Anodised", "PC", "WF"],
            key="finish_primary"
        )
    
    with col2:
        interleaving_required = st.selectbox(
            "Interleaving Required",
            ["Yes", "No"],
            key="interleaving_primary"
        )
    
    with col3:
        eco_friendly = st.selectbox(
            "Eco-Friendly Packing Material",
            ["Mac foam", "Stretch wrap", "Craft Paper"],
            key="eco_friendly_primary"
        )
    
    with col4:
        protective_tape = st.selectbox(
            "Protective Tape (Customer Specified)",
            ["Yes", "No"],
            key="protective_tape_primary"
        )
    
    st.divider()
    
    # Section 3: Primary Packing Total Cost
    st.subheader("Primary Packing Total Cost")
    
    # Table 1: Material Costs
    st.markdown("**Table 1: Primary Packing Material Costs**")
    
    # Create editable material costs table
    edited_material_df = st.data_editor(
        st.session_state.material_costs,
        num_rows="dynamic",
        use_container_width=True,
        column_config={
            "Material": st.column_config.TextColumn("Material", required=True),
            "Cost/ m²": st.column_config.NumberColumn("Cost/ m²", required=True, min_value=0, format="%.2f")
        },
        key="material_editor_primary"
    )
    
    # Update session state
    st.session_state.material_costs = edited_material_df
    
    # Table 2: Cardboard Box Cost
    st.markdown("**Table 2: Cardboard Box Cost**")
    
    # Create editable box costs table
    edited_box_df = st.data_editor(
        st.session_state.box_costs,
        num_rows="dynamic",
        use_container_width=True,
        column_config={
            "Length(mm)": st.column_config.NumberColumn("Length(mm)", required=True, min_value=0),
            "Width (mm)": st.column_config.NumberColumn("Width (mm)", required=True, min_value=0),
            "Height (mm)": st.column_config.NumberColumn("Height (mm)", required=True, min_value=0),
            "Cost (LKR)": st.column_config.NumberColumn("Cost (LKR)", required=True, min_value=0, format="%.2f")
        },
        key="box_editor_primary"
    )
    
    # Update session state
    st.session_state.box_costs = edited_box_df
    
    # Calculate and display Table 3: Primary Packing Total Cost
    st.markdown("**Table 3: Primary Packing Total Cost**")
    
    if not st.session_state.sku_data_primary.empty:
        # Prepare calculations
        calculations_data = []
        
        # Get material costs as dictionary for easy lookup
        material_cost_dict = dict(zip(
            st.session_state.material_costs["Material"],
            st.session_state.material_costs["Cost/ m²"]
        ))
        
        # Get reference box dimensions and cost
        ref_box = st.session_state.box_costs.iloc[0]
        ref_volume = ref_box["Length(mm)"] * ref_box["Width (mm)"] * ref_box["Height (mm)"]
        
        for _, sku in st.session_state.sku_data_primary.iterrows():
            try:
                # Extract SKU dimensions
                width = float(sku["Width/mm"])
                height = float(sku["Height/mm"])
                length = float(sku["Length/mm"])
                
                # Calculate Surface Area in m²
                sa_m2 = (2 * ((width * height) + (width * length) + (height * length))) / (1000 * 1000)
                
                # Calculate Interleaving Cost
                interleaving_cost = 0
                if interleaving_required == "Yes":
                    # Map eco_friendly selection to material name
                    material_map = {
                        "Mac foam": "McFoam",
                        "Stretch wrap": "Stretchwrap",
                        "Craft Paper": "Craft Paper"
                    }
                    selected_material = material_map.get(eco_friendly, "McFoam")
                    cost_per_m2 = material_cost_dict.get(selected_material, 0)
                    interleaving_cost = cost_per_m2 * sa_m2
                
                # Calculate Protective Tape Cost
                protective_tape_cost = 0
                if protective_tape == "Yes":
                    cost_per_m2 = material_cost_dict.get("Protective Tape", 0)
                    protective_tape_cost = cost_per_m2 * sa_m2
                
                # Calculate Packing Cost (proportional to reference box)
                sku_volume = width * height * length
                if ref_volume > 0:
                    packing_cost = (sku_volume / ref_volume) * ref_box["Cost (LKR)"]
                else:
                    packing_cost = 0
                
                # Calculate Total Cost
                total_cost = interleaving_cost + protective_tape_cost + packing_cost
                
                # Add to calculations data
                calculations_data.append({
                    "SKU": sku["SKU No"],
                    "SA(m²)": round(sa_m2, 4),
                    "Interleaving cost (LKR)": round(interleaving_cost, 2),
                    "Protective tape cost (LKR)": round(protective_tape_cost, 2),
                    "Packing type": "Cardboard box",
                    "Packing Cost (LKR)": round(packing_cost, 2),
                    "Total Cost (LKR)": round(total_cost, 2)
                })
                
            except (ValueError, TypeError):
                continue
        
        if calculations_data:
            calculations_df = pd.DataFrame(calculations_data)
            st.dataframe(calculations_df, use_container_width=True)
            
            # Display total sum
            total_sum = calculations_df["Total Cost (LKR)"].sum()
            st.metric("**Total Primary Packing Cost**", f"LKR {total_sum:,.2f}")
        else:
            st.warning("Please enter valid SKU data with numeric dimensions.")
    else:
        st.info("Enter SKU data in the table above to see cost calculations.")
    
    st.divider()
    
    # Section 4: Special Comments Section
    st.subheader("Special Comments Section")
    
    comments_box = f"""
    **Costing is done according to primary packing. Therefore, this cost does not include any crate or palletizing charges. Please note that secondary packaging will incur an additional charge.**
    
    The interleaving material is **"{eco_friendly}"**.
    
    **Protective tape required to avoid rejects**
    
    **Costing is only inclusive of interleaving required & Cardboard Box/Polybag.**
    """
    
    st.info(comments_box)

with tab2:
    st.header("Secondary Calculations")
    
    # First, create material_cost_dict from the shared material_costs table
    material_cost_dict = dict(zip(
        st.session_state.material_costs["Material"],
        st.session_state.material_costs["Cost/ m²"]
    ))
    
    # Get reference box dimensions and cost
    ref_box = st.session_state.box_costs.iloc[0]
    ref_volume = ref_box["Length(mm)"] * ref_box["Width (mm)"] * ref_box["Height (mm)"]
    
    # Section 1: SKU Table with dimensions
    st.subheader("SKU Table with dimensions")
    
    # Create editable dataframe for SKU input
    edited_sku_df_secondary = st.data_editor(
        st.session_state.sku_data_secondary,
        num_rows="dynamic",
        use_container_width=True,
        column_config={
            "SKU No": st.column_config.TextColumn("SKU No", required=True),
            "Width/mm": st.column_config.NumberColumn("Width/mm", required=True, min_value=0),
            "Height/mm": st.column_config.NumberColumn("Height/mm", required=True, min_value=0),
            "Length/mm": st.column_config.NumberColumn("Length/mm", required=True, min_value=0),
            "Comment on fabrication": st.column_config.SelectboxColumn(
                "Comment on fabrication",
                options=["Fabricated", "Just Cutting"],
                required=True
            )
        },
        key="sku_editor_secondary"
    )
    
    # Update session state with edited data
    st.session_state.sku_data_secondary = edited_sku_df_secondary
    
    st.divider()
    
    # Section 2: Common Packing selections
    st.subheader("Common Packing Selections")
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        finish_secondary = st.selectbox(
            "Finish",
            ["Mill Finish", "Anodised", "PC", "WF"],
            key="finish_secondary"
        )
    
    with col2:
        interleaving_required_secondary = st.selectbox(
            "Interleaving Required",
            ["Yes", "No"],
            key="interleaving_secondary"
        )
    
    with col3:
        eco_friendly_secondary = st.selectbox(
            "Eco-Friendly Packing Material",
            ["Mac foam", "Stretch wrap", "Craft Paper"],
            key="eco_friendly_secondary"
        )
    
    with col4:
        protective_tape_secondary = st.selectbox(
            "Protective Tape (Customer Specified)",
            ["Yes", "No"],
            key="protective_tape_secondary"
        )
    
    st.divider()
    
    # Section 3: Bundle Configuration
    st.subheader("Bundle Configuration")
    
    # Bundle input method
    bundle_method = st.radio(
        "Bundle Input Method:",
        ["Number of layers", "Size of the bundle"],
        horizontal=True,
        key="bundle_method"
    )
    
    if bundle_method == "Number of layers":
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
    else:  # Size of the bundle
        bundling_data = pd.DataFrame({
            "Bundle Width (mm)": [0],
            "Bundle Height (mm)": [0]
        })

        bundling_common = st.data_editor(
            bundling_data,
            column_config={
                "Bundle Width (mm)": st.column_config.NumberColumn("Bundle Width (mm)", min_value=0),
                "Bundle Height (mm)": st.column_config.NumberColumn("Bundle Height (mm)", min_value=0)
            },
            use_container_width=True,
            key="bundling_size_input"
        )
    
    st.divider()
    
    # Section 4: Primary Packing Material Costs (from Tab 1)
    st.subheader("Table 1: Primary Packing Material Costs")
    
    # Create editable material costs table (same as Tab 1)
    edited_material_df_secondary = st.data_editor(
        st.session_state.material_costs,
        num_rows="dynamic",
        use_container_width=True,
        column_config={
            "Material": st.column_config.TextColumn("Material", required=True),
            "Cost/ m²": st.column_config.NumberColumn("Cost/ m²", required=True, min_value=0, format="%.2f")
        },
        key="material_editor_secondary"
    )
    
    # Update session state
    st.session_state.material_costs = edited_material_df_secondary
    
    # Update material_cost_dict with any changes
    material_cost_dict = dict(zip(
        st.session_state.material_costs["Material"],
        st.session_state.material_costs["Cost/ m²"]
    ))
    
    st.divider()
    
    # Section 5: Cardboard Box Cost (from Tab 1)
    st.subheader("Table 2: Cardboard Box Cost")
    
    # Create editable box costs table (same as Tab 1)
    edited_box_df_secondary = st.data_editor(
        st.session_state.box_costs,
        num_rows="dynamic",
        use_container_width=True,
        column_config={
            "Length(mm)": st.column_config.NumberColumn("Length(mm)", required=True, min_value=0),
            "Width (mm)": st.column_config.NumberColumn("Width (mm)", required=True, min_value=0),
            "Height (mm)": st.column_config.NumberColumn("Height (mm)", required=True, min_value=0),
            "Cost (LKR)": st.column_config.NumberColumn("Cost (LKR)", required=True, min_value=0, format="%.2f")
        },
        key="box_editor_secondary"
    )
    
    # Update session state
    st.session_state.box_costs = edited_box_df_secondary
    
    # Update reference values
    ref_box = st.session_state.box_costs.iloc[0]
    ref_volume = ref_box["Length(mm)"] * ref_box["Width (mm)"] * ref_box["Height (mm)"]
    
    st.divider()
    
    # Section 6: Secondary Packing Cost Components (as per your reference code)
    st.subheader("Secondary Packing Cost Components")
    
    # Initialize secondary cost components in session state
    if 'crate_cost_df' not in st.session_state:
        st.session_state.crate_cost_df = pd.DataFrame({
            "Width (mm)": [480],
            "Height (mm)": [590],
            "Length (mm)": [2000],
            "Cost (LKR)": [5000.0]
        })
    
    if 'pallet_cost_df' not in st.session_state:
        st.session_state.pallet_cost_df = pd.DataFrame({
            "Width (mm)": [2000],
            "Height (mm)": [600],
            "Cost (LKR)": [3000.0]
        })
    
    if 'strapping_cost_df' not in st.session_state:
        st.session_state.strapping_cost_df = pd.DataFrame({
            "Strapping Length (m)": [1.0],
            "Cost (LKR/m)": [15.0]
        })
    
    if 'polybag_ref' not in st.session_state:
        st.session_state.polybag_ref = pd.DataFrame({
            "Polybag Size": ["9 Inch"],
            "Cost per m (LKR/m)": [12.8]
        })
    
    if 'stretchwrap_ref' not in st.session_state:
        st.session_state.stretchwrap_ref = pd.DataFrame({
            "Area(mm²)": [210000],
            "Cost(Rs/mm²)": [135]
        })
    
    # Create tabs for secondary cost components
    sec_tab1, sec_tab2, sec_tab3, sec_tab4, sec_tab5 = st.tabs([
        "📦 Crate Cost", 
        "📐 Pallet Cost", 
        "🧷 Strapping Cost",
        "👝 Polybag Cost",
        "🌀 Stretchwrap Cost"
    ])
    
    with sec_tab1:
        st.markdown("#### Crate Cost Reference")
        crate_cost_df = st.data_editor(
            st.session_state.crate_cost_df,
            num_rows="dynamic",
            use_container_width=True,
            column_config={
                "Width (mm)": st.column_config.NumberColumn("Width (mm)", required=True, min_value=0),
                "Height (mm)": st.column_config.NumberColumn("Height (mm)", required=True, min_value=0),
                "Length (mm)": st.column_config.NumberColumn("Length (mm)", required=True, min_value=0),
                "Cost (LKR)": st.column_config.NumberColumn("Cost (LKR)", required=True, min_value=0, format="%.2f")
            },
            key="crate_cost_editor"
        )
        st.session_state.crate_cost_df = crate_cost_df
    
    with sec_tab2:
        st.markdown("#### Pallet Cost Reference")
        pallet_cost_df = st.data_editor(
            st.session_state.pallet_cost_df,
            num_rows="dynamic",
            use_container_width=True,
            column_config={
                "Width (mm)": st.column_config.NumberColumn("Width (mm)", required=True, min_value=0),
                "Height (mm)": st.column_config.NumberColumn("Height (mm)", required=True, min_value=0),
                "Cost (LKR)": st.column_config.NumberColumn("Cost (LKR)", required=True, min_value=0, format="%.2f")
            },
            key="pallet_cost_editor"
        )
        st.session_state.pallet_cost_df = pallet_cost_df
    
    with sec_tab3:
        st.markdown("#### PP Strapping Cost Reference")
        strapping_cost_df = st.data_editor(
            st.session_state.strapping_cost_df,
            num_rows="dynamic",
            use_container_width=True,
            column_config={
                "Strapping Length (m)": st.column_config.NumberColumn("Strapping Length (m)", required=True, min_value=0, format="%.2f"),
                "Cost (LKR/m)": st.column_config.NumberColumn("Cost (LKR/m)", required=True, min_value=0, format="%.2f")
            },
            key="strapping_cost_editor"
        )
        st.session_state.strapping_cost_df = strapping_cost_df
    
    with sec_tab4:
        st.markdown("#### Polybag Cost")
        polybag_ref = st.data_editor(
            st.session_state.polybag_ref,
            num_rows="dynamic",
            use_container_width=True,
            column_config={
                "Polybag Size": st.column_config.TextColumn("Polybag Size", required=True),
                "Cost per m (LKR/m)": st.column_config.NumberColumn("Cost per m (LKR/m)", required=True, min_value=0, format="%.2f")
            },
            key="polybag_editor"
        )
        st.session_state.polybag_ref = polybag_ref
    
    with sec_tab5:
        st.markdown("#### Stretchwrap Cost")
        stretchwrap_ref = st.data_editor(
            st.session_state.stretchwrap_ref,
            num_rows="dynamic",
            use_container_width=True,
            column_config={
                "Area(mm²)": st.column_config.NumberColumn("Area(mm²)", required=True, min_value=0),
                "Cost(Rs/mm²)": st.column_config.NumberColumn("Cost(Rs/mm²)", required=True, min_value=0, format="%.2f")
            },
            key="stretchwrap_editor"
        )
        st.session_state.stretchwrap_ref = stretchwrap_ref
    
    st.divider()
    
    # Section 7: Secondary Packing Total Cost Calculation
    st.subheader("Secondary Packing Total Cost")
    
    if not st.session_state.sku_data_secondary.empty:
        # Prepare calculations for secondary packing
        secondary_calculations_data = []
        bundle_output_rows = []  # For bundle calculations
        
        # Get polybag and stretchwrap references
        polybag_cost_per_m = float(st.session_state.polybag_ref["Cost per m (LKR/m)"].iloc[0])
        ref_stretch_area = float(st.session_state.stretchwrap_ref["Area(mm²)"].iloc[0])
        ref_stretch_cost = float(st.session_state.stretchwrap_ref["Cost(Rs/mm²)"].iloc[0])
        
        for _, sku in st.session_state.sku_data_secondary.iterrows():
            try:
                # Extract SKU dimensions
                width = float(sku["Width/mm"])
                height = float(sku["Height/mm"])
                length = float(sku["Length/mm"])
                
                # Calculate bundle dimensions based on method
                if bundle_method == "Number of layers":
                    rows = int(bundling_common.loc[0, "Rows"])
                    layers = int(bundling_common.loc[0, "Layers"])
                    width_type = bundling_common.loc[0, "Width Type"]
                    height_type = bundling_common.loc[0, "Height Type"]
                    
                    profile_dimensions = {"W/mm": width, "H/mm": height}
                    bundle_width_calc = rows * profile_dimensions[width_type]
                    bundle_height_calc = layers * profile_dimensions[height_type]
                    bundle_length_calc = length
                    profiles_per_bundle_calc = rows * layers
                else:  # Size of the bundle
                    bundle_width_calc = float(bundling_common.loc[0, "Bundle Width (mm)"])
                    bundle_height_calc = float(bundling_common.loc[0, "Bundle Height (mm)"])
                    bundle_length_calc = length
                    
                    # Calculate maximum profiles that can fit
                    rows_width = int(bundle_width_calc / width) if width > 0 else 0
                    rows_height = int(bundle_height_calc / height) if height > 0 else 0
                    profiles_per_bundle_calc = rows_width * rows_height if rows_width > 0 and rows_height > 0 else 1
                
                # Calculate bundle surface area in m²
                bundle_area_m2 = 2 * (
                    (bundle_width_calc * bundle_length_calc) + 
                    (bundle_height_calc * bundle_length_calc) + 
                    (bundle_width_calc * bundle_height_calc)
                ) / 1_000_000
                
                # Individual profile surface area
                profile_surface_area = (2 * ((width * height) + (width * length) + (height * length))) / 1_000_000
                
                # Calculate PRIMARY packaging cost (polybag or cardboard box) - PER PROFILE
                user_volume = width * height * length
                if length > 550:  # Use polybag
                    polybag_cost = (polybag_cost_per_m * (length / 1000)) / 1  # For primary packing
                    cardboard_cost = 0.0
                    packaging_type = "Polybag"
                    primary_packaging_cost = polybag_cost
                else:  # Use cardboard box
                    cardboard_cost = (user_volume / ref_volume) * ref_box["Cost (LKR)"] if ref_volume else 0.0
                    polybag_cost = 0.0
                    packaging_type = "Cardboard Box"
                    primary_packaging_cost = cardboard_cost
                
                # Calculate SECONDARY costs - PER PROFILE
                # 1. Interleaving cost (if required)
                interleaving_cost_sec = 0
                if interleaving_required_secondary == "Yes":
                    material_map = {
                        "Mac foam": "McFoam",
                        "Stretch wrap": "Stretchwrap",
                        "Craft Paper": "Craft Paper"
                    }
                    selected_material = material_map.get(eco_friendly_secondary, "McFoam")
                    cost_per_m2 = material_cost_dict.get(selected_material, 0)
                    if eco_friendly_secondary == "Stretch wrap":
                        # Special calculation for stretchwrap at bundle level
                        bundle_surface_area_mm2 = 2 * (
                            (bundle_width_calc * bundle_length_calc) + 
                            (bundle_height_calc * bundle_length_calc) + 
                            (bundle_width_calc * bundle_height_calc)
                        )
                        stretchwrap_cost_bundle = (bundle_surface_area_mm2 / ref_stretch_area) * ref_stretch_cost if ref_stretch_area else 0.0
                        interleaving_cost_sec = stretchwrap_cost_bundle / profiles_per_bundle_calc
                    else:
                        interleaving_cost_sec = (cost_per_m2 * bundle_area_m2) / profiles_per_bundle_calc
                
                # 2. Protective tape cost
                protective_tape_cost_sec = 0
                if protective_tape_secondary == "Yes" or finish_secondary == "Anodised" or sku["Comment on fabrication"] == "Fabricated":
                    cost_per_m2 = material_cost_dict.get("Protective Tape", 0)
                    protective_tape_cost_sec = cost_per_m2 * profile_surface_area
                
                # 3. Pallet/Crate cost (based on your reference code)
                # Get final packing method - default to crate for secondary
                final_packing_method = "Crate"  # Default
                
                # Calculate crate/pallet cost based on bundle dimensions
                if final_packing_method == "Crate":
                    ref_crate = st.session_state.crate_cost_df.iloc[0]
                    ref_crate_vol = float(ref_crate["Width (mm)"]) * float(ref_crate["Height (mm)"]) * float(ref_crate["Length (mm)"])
                    bundle_vol = bundle_width_calc * bundle_height_calc * bundle_length_calc
                    crate_cost_total = (bundle_vol / ref_crate_vol) * float(ref_crate["Cost (LKR)"]) if ref_crate_vol else 0.0
                    
                    # Strapping cost for crate
                    strapping_ref = st.session_state.strapping_cost_df.iloc[0]
                    length_m = bundle_length_calc / 1000
                    num_clips = length_m / 0.5
                    strapping_cost_total = 2 * (length_m + (bundle_width_calc / 1000)) * float(strapping_ref["Cost (LKR/m)"]) * num_clips
                    
                    pallet_cost_total = 0.0
                else:  # Pallet
                    ref_pallet = st.session_state.pallet_cost_df.iloc[0]
                    ref_pallet_area = float(ref_pallet["Width (mm)"]) * float(ref_pallet["Height (mm)"])
                    bundle_area = bundle_width_calc * bundle_height_calc
                    pallet_cost_total = (bundle_area / ref_pallet_area) * float(ref_pallet["Cost (LKR)"]) if ref_pallet_area else 0.0
                    crate_cost_total = 0.0
                    strapping_cost_total = 0.0
                
                # Distribute crate/pallet costs per profile
                secondary_packaging_cost = (crate_cost_total + pallet_cost_total + strapping_cost_total) / profiles_per_bundle_calc
                
                # Total cost per profile
                total_cost_per_profile = (
                    primary_packaging_cost +  # From primary packaging (polybag/cardboard)
                    interleaving_cost_sec + 
                    protective_tape_cost_sec + 
                    secondary_packaging_cost
                )
                
                # Store bundle data
                bundle_output_rows.append({
                    "SKU": sku["SKU No"],
                    "Bundle Width (mm)": f"{bundle_width_calc:.2f}",
                    "Bundle Height (mm)": f"{bundle_height_calc:.2f}",
                    "Bundle Length (mm)": f"{bundle_length_calc:.2f}",
                    "Profiles per Bundle": profiles_per_bundle_calc,
                    "Packaging Type": packaging_type,
                    "Primary Pack Cost (Rs/prof)": f"{primary_packaging_cost:.2f}",
                    "Interleaving (Rs/prof)": f"{interleaving_cost_sec:.2f}",
                    "Protective Tape (Rs/prof)": f"{protective_tape_cost_sec:.2f}",
                    "Crate/Pallet (Rs/prof)": f"{secondary_packaging_cost:.2f}",
                    "Total Cost (Rs/prof)": f"{total_cost_per_profile:.2f}"
                })
                
            except (ValueError, TypeError):
                continue
        
        if bundle_output_rows:
            secondary_calculations_df = pd.DataFrame(bundle_output_rows)
            
            # Make Profiles per Bundle and Packaging Type editable
            editable_secondary_df = st.data_editor(
                secondary_calculations_df,
                column_config={
                    "Profiles per Bundle": st.column_config.NumberColumn(
                        "Profiles per Bundle",
                        min_value=1,
                        step=1
                    ),
                    "Packaging Type": st.column_config.SelectboxColumn(
                        "Packaging Type",
                        options=["Polybag", "Cardboard Box"]
                    )
                },
                use_container_width=True,
                key="secondary_packing_editor"
            )
            
            # Calculate total
            total_secondary_cost = 0
            for _, row in editable_secondary_df.iterrows():
                try:
                    total_secondary_cost += float(row["Total Cost (Rs/prof)"])
                except:
                    continue
            
            # Display totals
            col1, col2 = st.columns(2)
            with col1:
                st.metric("Total Bundles", len(editable_secondary_df))
            with col2:
                st.metric("**Total Secondary Cost**", f"LKR {total_secondary_cost:,.2f}")
        else:
            st.warning("Please enter valid SKU data with numeric dimensions.")
    else:
        st.info("Enter SKU data in the table above to see secondary packing calculations.")
    
    st.divider()
    
    # Section 8: Special Notes for Secondary Packing
    st.subheader("Special Notes")
    
    notes_box = f"""
    **Secondary Packing Specifications:**
    
    - **Finish:** {finish_secondary}
    - **Interleaving:** {interleaving_required_secondary} ({eco_friendly_secondary if interleaving_required_secondary == "Yes" else "Not required"})
    - **Protective Tape:** {protective_tape_secondary}
    - **Bundle Configuration:** {bundle_method}
    
    **Additional Notes:**
    
    1. Secondary packing costs include primary packaging + interleaving + protective tape + crate/pallet costs
    2. Primary packaging cost is based on individual profile packaging (polybag or cardboard box)
    3. Interleaving costs are applied at bundle level and distributed per profile
    4. Protective tape is applied per individual profile where required
    5. Crate/Pallet costs are calculated based on bundle dimensions
    6. All costs shown are per profile
    
    **Note:** This costing includes both primary and secondary packaging components.
    """
    
    st.info(notes_box)

# Footer
st.divider()
st.caption("Packing Costing Calculator v1.0 | All dimensions should be entered in millimeters (mm)")

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
        "Bundle Configuration Method:",
        ["Number of layers", "Bundle dimensions"],
        horizontal=True,
        key="bundle_method"
    )
    
    bundle_config_cols = st.columns(3)
    
    if bundle_method == "Number of layers":
        with bundle_config_cols[0]:
            rows_per_bundle = st.number_input(
                "Rows per Bundle",
                min_value=1,
                value=1,
                step=1,
                key="rows_per_bundle"
            )
        with bundle_config_cols[1]:
            layers_per_bundle = st.number_input(
                "Layers per Bundle",
                min_value=1,
                value=1,
                step=1,
                key="layers_per_bundle"
            )
        with bundle_config_cols[2]:
            orientation = st.selectbox(
                "Bundle Orientation",
                ["Width-wise", "Height-wise"],
                key="bundle_orientation"
            )
    else:  # Bundle dimensions
        with bundle_config_cols[0]:
            bundle_width = st.number_input(
                "Bundle Width (mm)",
                min_value=0,
                value=0,
                step=10,
                key="bundle_width"
            )
        with bundle_config_cols[1]:
            bundle_height = st.number_input(
                "Bundle Height (mm)",
                min_value=0,
                value=0,
                step=10,
                key="bundle_height"
            )
        with bundle_config_cols[2]:
            profiles_per_bundle = st.number_input(
                "Profiles per Bundle",
                min_value=1,
                value=1,
                step=1,
                key="profiles_per_bundle"
            )
    
    st.divider()
    
    # Section 4: Secondary Packing Costs Table
    st.subheader("Secondary Packing Cost Components")
    
    # Initialize secondary cost components in session state
    if 'secondary_costs' not in st.session_state:
        st.session_state.secondary_costs = pd.DataFrame({
            "Component": ["Pallet Cost", "Crate Cost", "Strapping Cost", "Stretch Wrap"],
            "Unit": ["Per pallet", "Per crate", "Per meter", "Per m²"],
            "Cost (LKR)": [2500.00, 5000.00, 15.00, 14.38]
        })
    
    # Create editable secondary costs table
    edited_secondary_costs = st.data_editor(
        st.session_state.secondary_costs,
        num_rows="dynamic",
        use_container_width=True,
        column_config={
            "Component": st.column_config.TextColumn("Component", required=True),
            "Unit": st.column_config.TextColumn("Unit", required=True),
            "Cost (LKR)": st.column_config.NumberColumn("Cost (LKR)", required=True, min_value=0, format="%.2f")
        },
        key="secondary_costs_editor"
    )
    
    # Update session state
    st.session_state.secondary_costs = edited_secondary_costs
    
    # Convert to dictionary for easy lookup
    secondary_cost_dict = dict(zip(
        st.session_state.secondary_costs["Component"],
        st.session_state.secondary_costs["Cost (LKR)"]
    ))
    
    st.divider()
    
    # Section 5: Secondary Packing Total Cost Calculation
    st.subheader("Secondary Packing Total Cost")
    
    if not st.session_state.sku_data_secondary.empty:
        # Prepare calculations for secondary packing
        secondary_calculations_data = []
        total_secondary_cost = 0
        total_profiles = 0
        
        for _, sku in st.session_state.sku_data_secondary.iterrows():
            try:
                # Extract SKU dimensions
                width = float(sku["Width/mm"])
                height = float(sku["Height/mm"])
                length = float(sku["Length/mm"])
                
                # Calculate bundle dimensions based on method
                if bundle_method == "Number of layers":
                    if orientation == "Width-wise":
                        bundle_width_calc = rows_per_bundle * width
                        bundle_height_calc = layers_per_bundle * height
                    else:  # Height-wise
                        bundle_width_calc = rows_per_bundle * height
                        bundle_height_calc = layers_per_bundle * width
                    
                    profiles_per_bundle_calc = rows_per_bundle * layers_per_bundle
                else:  # Bundle dimensions
                    bundle_width_calc = bundle_width
                    bundle_height_calc = bundle_height
                    profiles_per_bundle_calc = profiles_per_bundle
                
                # Calculate bundle volume and surface area
                bundle_volume = bundle_width_calc * bundle_height_calc * length
                bundle_surface_area = 2 * (
                    (bundle_width_calc * bundle_height_calc) + 
                    (bundle_width_calc * length) + 
                    (bundle_height_calc * length)
                ) / (1000 * 1000)  # Convert to m²
                
                # Individual profile surface area
                profile_surface_area = (2 * ((width * height) + (width * length) + (height * length))) / (1000 * 1000)
                
                # Calculate costs
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
                    interleaving_cost_sec = cost_per_m2 * bundle_surface_area / profiles_per_bundle_calc
                
                # 2. Protective tape cost
                protective_tape_cost_sec = 0
                if protective_tape_secondary == "Yes" or finish_secondary == "Anodised" or sku["Comment on fabrication"] == "Fabricated":
                    cost_per_m2 = material_cost_dict.get("Protective Tape", 0)
                    protective_tape_cost_sec = cost_per_m2 * profile_surface_area
                
                # 3. Pallet/Crate cost (distributed per profile)
                # Use bundle volume to estimate pallet/crate requirements
                pallet_cost_per_profile = secondary_cost_dict.get("Pallet Cost", 0) / 50  # Assuming 50 bundles per pallet
                crate_cost_per_profile = secondary_cost_dict.get("Crate Cost", 0) / 20   # Assuming 20 bundles per crate
                
                # 4. Strapping cost
                strapping_length = 2 * (bundle_width_calc + bundle_height_calc) / 1000  # Convert to meters
                strapping_cost = strapping_length * secondary_cost_dict.get("Strapping Cost", 0) / profiles_per_bundle_calc
                
                # 5. Stretch wrap cost
                stretch_wrap_cost = bundle_surface_area * secondary_cost_dict.get("Stretch Wrap", 0) / profiles_per_bundle_calc
                
                # Total cost per profile
                total_cost_per_profile = (
                    interleaving_cost_sec + 
                    protective_tape_cost_sec + 
                    pallet_cost_per_profile + 
                    crate_cost_per_profile + 
                    strapping_cost + 
                    stretch_wrap_cost
                )
                
                # Add to calculations data
                secondary_calculations_data.append({
                    "SKU": sku["SKU No"],
                    "Bundle Width (mm)": round(bundle_width_calc, 2),
                    "Bundle Height (mm)": round(bundle_height_calc, 2),
                    "Profiles/Bundle": profiles_per_bundle_calc,
                    "Interleaving (LKR)": round(interleaving_cost_sec, 2),
                    "Protective Tape (LKR)": round(protective_tape_cost_sec, 2),
                    "Pallet Share (LKR)": round(pallet_cost_per_profile, 2),
                    "Crate Share (LKR)": round(crate_cost_per_profile, 2),
                    "Strapping (LKR)": round(strapping_cost, 2),
                    "Stretch Wrap (LKR)": round(stretch_wrap_cost, 2),
                    "Total Cost/Profile (LKR)": round(total_cost_per_profile, 2)
                })
                
                total_secondary_cost += total_cost_per_profile
                total_profiles += 1
                
            except (ValueError, TypeError):
                continue
        
        if secondary_calculations_data:
            secondary_calculations_df = pd.DataFrame(secondary_calculations_data)
            st.dataframe(secondary_calculations_df, use_container_width=True)
            
            # Display totals
            col1, col2 = st.columns(2)
            with col1:
                st.metric("Total Profiles", total_profiles)
            with col2:
                st.metric("**Total Secondary Cost**", f"LKR {total_secondary_cost:,.2f}")
        else:
            st.warning("Please enter valid SKU data with numeric dimensions.")
    else:
        st.info("Enter SKU data in the table above to see secondary packing calculations.")
    
    st.divider()
    
    # Section 6: Special Notes for Secondary Packing
    st.subheader("Special Notes")
    
    notes_box = f"""
    **Secondary Packing Specifications:**
    
    - **Finish:** {finish_secondary}
    - **Interleaving:** {interleaving_required_secondary} ({eco_friendly_secondary if interleaving_required_secondary == "Yes" else "Not required"})
    - **Protective Tape:** {protective_tape_secondary}
    - **Bundle Configuration:** {bundle_method}
    
    **Additional Notes:**
    
    1. Secondary packing costs include palletizing, crating, strapping, and stretch wrapping
    2. Costs are calculated per profile based on bundle configuration
    3. Pallet and crate costs are distributed across profiles in the bundle
    4. Interleaving costs are applied at bundle level and distributed per profile
    5. Protective tape is applied per individual profile where required
    6. Bundle dimensions are calculated based on SKU dimensions and configuration method
    
    **Total Secondary Packing Cost:** LKR {total_secondary_cost:,.2f}
    """
    
    st.info(notes_box)

# Footer
st.divider()
st.caption("Packing Costing Calculator v1.0 | All dimensions should be entered in millimeters (mm)")

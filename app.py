import streamlit as st
import pandas as pd
import numpy as np

# Set page configuration
st.set_page_config(
    page_title="Packing Costing Calculator",
    page_icon="📦",
    layout="wide"
)

# Initialize session state for calculation triggers
if 'calculate_primary' not in st.session_state:
    st.session_state.calculate_primary = False
if 'calculate_secondary' not in st.session_state:
    st.session_state.calculate_secondary = False

# Function to trigger primary calculations
def trigger_primary_calculation():
    st.session_state.calculate_primary = True

# Function to trigger secondary calculations
def trigger_secondary_calculation():
    st.session_state.calculate_secondary = True

# Function to reset calculation flags
def reset_calculation_flags():
    st.session_state.calculate_primary = False
    st.session_state.calculate_secondary = False

# App title
st.title("📦 Packing Costing Calculator")

# Create tabs
tab1, tab2 = st.tabs(["Primary Calculations", "Secondary Calculations"])

with tab1:
    st.header("Primary Calculations")
    
    # Sub topic 1 - SKU Table with dimensions
    st.subheader("SKU Table with dimensions")
    
    # Initialize session state for primary SKU data
    if 'primary_sku_data' not in st.session_state:
        st.session_state.primary_sku_data = pd.DataFrame(columns=["SKU No", "Width/mm", "Height/mm", "Length/mm", "Comment on fabrication"])
    
    # Create editable dataframe for SKU input
    edited_sku_df = st.data_editor(
        st.session_state.primary_sku_data,
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
    
    # Update session state
    st.session_state.primary_sku_data = edited_sku_df
    
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
    
    # Initialize session state for material costs
    if 'primary_material_costs' not in st.session_state:
        st.session_state.primary_material_costs = pd.DataFrame({
            "Material": ["McFoam", "Craft Paper", "Protective Tape", "Stretchwrap"],
            "Cost/ m²": [51.00, 34.65, 100.65, 14.38]
        })
    
    # Create editable material costs table
    edited_material_df = st.data_editor(
        st.session_state.primary_material_costs,
        num_rows="dynamic",
        use_container_width=True,
        column_config={
            "Material": st.column_config.TextColumn("Material", required=True),
            "Cost/ m²": st.column_config.NumberColumn("Cost/ m²", required=True, min_value=0, format="%.2f")
        },
        key="material_editor_primary"
    )
    
    # Update session state
    st.session_state.primary_material_costs = edited_material_df
    
    # Table 2: Cardboard Box Cost
    st.markdown("**Table 2: Cardboard Box Cost**")
    
    # Initialize session state for box costs
    if 'primary_box_costs' not in st.session_state:
        st.session_state.primary_box_costs = pd.DataFrame({
            "Length(mm)": [330],
            "Width (mm)": [210],
            "Height (mm)": [135],
            "Cost (LKR)": [205.00]
        })
    
    # Create editable box costs table
    edited_box_df = st.data_editor(
        st.session_state.primary_box_costs,
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
    st.session_state.primary_box_costs = edited_box_df
    
    # Add Calculate button
    st.markdown("---")
    calculate_col1, calculate_col2, calculate_col3 = st.columns([1, 1, 1])
    with calculate_col2:
        calculate_primary_btn = st.button("🔢 Calculate Primary Packing Costs", 
                                         type="primary", 
                                         use_container_width=True,
                                         on_click=trigger_primary_calculation)
    
    # Calculate and display Table 3: Primary Packing Total Cost
    if st.session_state.calculate_primary:
        st.markdown("**Table 3: Primary Packing Total Cost**")
        
        if not st.session_state.primary_sku_data.empty:
            # Prepare calculations
            calculations_data = []
            
            # Get material costs as dictionary
            material_cost_dict = dict(zip(
                st.session_state.primary_material_costs["Material"],
                st.session_state.primary_material_costs["Cost/ m²"]
            ))
            
            # Get reference box dimensions and cost
            ref_box = st.session_state.primary_box_costs.iloc[0]
            ref_volume = ref_box["Length(mm)"] * ref_box["Width (mm)"] * ref_box["Height (mm)"]
            
            for _, sku in st.session_state.primary_sku_data.iterrows():
                try:
                    width = float(sku["Width/mm"])
                    height = float(sku["Height/mm"])
                    length = float(sku["Length/mm"])
                    
                    # Calculate Surface Area in m²
                    sa_m2 = (2 * ((width * height) + (width * length) + (height * length))) / (1000 * 1000)
                    
                    # Calculate Interleaving Cost
                    interleaving_cost = 0
                    if interleaving_required == "Yes":
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
                    
                    # Calculate Packing Cost
                    sku_volume = width * height * length
                    # Calculate Packing Cost - Updated formula
                    if ref_box["Length(mm)"] > 0 and ref_box["Width (mm)"] > 0 and ref_box["Height (mm)"] > 0:
                        packing_cost = (ref_box["Cost (LKR)"] / (ref_box["Width (mm)"] * ref_box["Height (mm)"] * ref_box["Length(mm)"])) * (width * height * length)
                    else:
                        packing_cost = 0
                    
                    # Calculate Total Cost
                    total_cost = interleaving_cost + protective_tape_cost + packing_cost
                    
                    calculations_data.append({
                        "SKU": sku["SKU No"],
                        "SA(m²)": round(sa_m2, 4),
                        "Interleaving cost": round(interleaving_cost, 2),
                        "Protective tape cost": round(protective_tape_cost, 2),
                        "Packing type": "Cardboard box",
                        "Box height/mm": round(height, 2),
                        "Box width/mm": round(width, 2),
                        "Box length/mm": round(length, 2),
                        "Packing Cost (LKR)": round(packing_cost, 2),
                        "Total Cost": round(total_cost, 2)
                    })
                    
                except (ValueError, TypeError):
                    continue
            
            if calculations_data:
                # Store calculations in session state
                st.session_state.primary_calculations = pd.DataFrame(calculations_data)
                
                # Display calculations
                st.dataframe(st.session_state.primary_calculations, use_container_width=True)
                
                # Display total summary
                total_sum = st.session_state.primary_calculations["Total Cost"].sum()
                st.metric("**Total Primary Packing Cost**", f"LKR {total_sum:,.2f}")
            else:
                st.warning("Enter valid SKU data")
        else:
            st.info("Enter SKU data")
    
    st.divider()
    
    # Section 4: Special Comments Section
    st.subheader("Special Comments Section")
    
    comments_box = f"""
    Costing is done according to primary packing. Therefore, this cost does not include any crate or palletizing charges. Please note that secondary packaging will incur an additional charge.

    The interleaving material is "{eco_friendly}".

    Protective tape required to avoid rejects

    Costing is only inclusive of interleaving required & Cardboard Box/Polybag.
    """
    
    st.info(comments_box)

with tab2:
    st.header("Secondary Calculations")
    
    # SKU input table
    st.subheader("SKU Table with dimensions")
    
    # Initialize session state for secondary SKU data
    if 'secondary_sku_data' not in st.session_state:
        st.session_state.secondary_sku_data = pd.DataFrame(columns=["SKU No", "Width/mm", "Height/mm", "Length/mm", "Comment on fabrication"])
    
    edited_sku_df_tab2 = st.data_editor(
        st.session_state.secondary_sku_data,
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
    
    # Update session state
    st.session_state.secondary_sku_data = edited_sku_df_tab2
    
    st.divider()
    
    # Common packing selections
    st.subheader("Common Packing Selections")
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        finish_tab2 = st.selectbox(
            "Finish",
            ["Mill Finish", "Anodised", "PC", "WF"],
            key="finish_secondary"
        )
    
    with col2:
        interleaving_required_tab2 = st.selectbox(
            "Interleaving Required",
            ["Yes", "No"],
            key="interleaving_secondary"
        )
    
    with col3:
        eco_friendly_tab2 = st.selectbox(
            "Eco-Friendly Packing Material",
            ["Mac foam", "Stretch wrap", "Craft Paper"],
            key="eco_friendly_secondary"
        )
    
    with col4:
        protective_tape_tab2 = st.selectbox(
            "Protective Tape (Customer Specified)",
            ["Yes", "No"],
            key="protective_tape_secondary"
        )
    
    st.divider()
    
    # New Section: Input Bundling Data
    st.subheader("Input Bundling Data")
    
    # Section 1 - Number of layers (Method 1)
    st.markdown("**Section 1 - Number of layers (Method 1)**")
    
    # Initialize bundling data in session state
    if 'bundling_data' not in st.session_state:
        st.session_state.bundling_data = pd.DataFrame(columns=[
            "Number of rows/bundle", 
            "Number of layer/bundle", 
            "width prof.type", 
            "height prof.type"
        ])
    
    # Create editable bundling data table
    edited_bundling_df = st.data_editor(
        st.session_state.bundling_data,
        num_rows="dynamic",
        use_container_width=True,
        column_config={
            "Number of rows/bundle": st.column_config.NumberColumn("Number of rows/bundle", required=True, min_value=1),
            "Number of layer/bundle": st.column_config.NumberColumn("Number of layer/bundle", required=True, min_value=1),
            "width prof.type": st.column_config.SelectboxColumn(
                "width prof.type",
                options=["W/mm", "H/mm"],
                required=True
            ),
            "height prof.type": st.column_config.TextColumn("height prof.type", required=True, disabled=True)
        },
        key="bundling_editor"
    )
    
    # Update session state with proper height prof.type
    if not edited_bundling_df.empty:
        for idx in range(len(edited_bundling_df)):
            width_prof = edited_bundling_df.iloc[idx]["width prof.type"]
            if width_prof == "W/mm":
                edited_bundling_df.at[idx, "height prof.type"] = "H/mm"
            elif width_prof == "H/mm":
                edited_bundling_df.at[idx, "height prof.type"] = "W/mm"
    
    st.session_state.bundling_data = edited_bundling_df
    
    st.divider()
    
    # Section 2 - Size of bundle (Method 2)
    st.markdown("**Section 2 - Size of bundle (Method 2)**")
    
    # Initialize bundle size data in session state
    if 'bundle_size_data' not in st.session_state:
        st.session_state.bundle_size_data = pd.DataFrame(columns=[
            "Bundle width/mm", 
            "Bundle Height/mm"
        ])
    
    # Create editable bundle size table
    edited_bundle_size_df = st.data_editor(
        st.session_state.bundle_size_data,
        num_rows="dynamic",
        use_container_width=True,
        column_config={
            "Bundle width/mm": st.column_config.NumberColumn("Bundle width/mm", required=True, min_value=0),
            "Bundle Height/mm": st.column_config.NumberColumn("Bundle Height/mm", required=True, min_value=0)
        },
        key="bundle_size_editor"
    )
    
    # Update session state
    st.session_state.bundle_size_data = edited_bundle_size_df
    
    st.divider()
    
    # New Section: Secondary Packing Cost (Per Profile)
    st.subheader("Secondary Packing Cost (Per Profile)")
    
    # Table 1: Primary Packing Material Costs
    st.markdown("**Table 1: Primary Packing Material Costs**")
    
    # Initialize secondary material costs in session state
    if 'secondary_material_costs' not in st.session_state:
        st.session_state.secondary_material_costs = pd.DataFrame({
            "Material": ["McFoam", "Craft Paper", "Protective Tape", "Stretchwrap"],
            "Cost/ m²": [51.00, 34.65, 100.65, 14.38]
        })
    
    # Create editable material costs table
    edited_secondary_material_df = st.data_editor(
        st.session_state.secondary_material_costs,
        num_rows="dynamic",
        use_container_width=True,
        column_config={
            "Material": st.column_config.TextColumn("Material", required=True),
            "Cost/ m²": st.column_config.NumberColumn("Cost/ m²", required=True, min_value=0, format="%.2f")
        },
        key="secondary_material_editor"
    )
    
    # Update session state
    st.session_state.secondary_material_costs = edited_secondary_material_df
    
    # Table 2: Cardboard Box Cost
    st.markdown("**Table 2: Cardboard Box Cost**")
    
    # Initialize secondary box costs in session state
    if 'secondary_box_costs' not in st.session_state:
        st.session_state.secondary_box_costs = pd.DataFrame({
            "Length(mm)": [330],
            "Width (mm)": [210],
            "Height (mm)": [135],
            "Cost (LKR)": [205.00]
        })
    
    # Create editable box costs table
    edited_secondary_box_df = st.data_editor(
        st.session_state.secondary_box_costs,
        num_rows="dynamic",
        use_container_width=True,
        column_config={
            "Length(mm)": st.column_config.NumberColumn("Length(mm)", required=True, min_value=0),
            "Width (mm)": st.column_config.NumberColumn("Width (mm)", required=True, min_value=0),
            "Height (mm)": st.column_config.NumberColumn("Height (mm)", required=True, min_value=0),
            "Cost (LKR)": st.column_config.NumberColumn("Cost (LKR)", required=True, min_value=0, format="%.2f")
        },
        key="secondary_box_editor"
    )
    
    # Update session state
    st.session_state.secondary_box_costs = edited_secondary_box_df
    
    # Table 3: Polybag Cost
    st.markdown("**Table 3: Polybag Cost**")
    
    # Initialize polybag costs in session state
    if 'polybag_costs' not in st.session_state:
        st.session_state.polybag_costs = pd.DataFrame({
            "Polybag size (inches)": [9],
            "Cost/m (LKR/m)": [12.8]
        })
    
    # Create editable polybag costs table
    edited_polybag_df = st.data_editor(
        st.session_state.polybag_costs,
        num_rows="dynamic",
        use_container_width=True,
        column_config={
            "Polybag size (inches)": st.column_config.NumberColumn("Polybag size (inches)", required=True, min_value=0),
            "Cost/m (LKR/m)": st.column_config.NumberColumn("Cost/m (LKR/m)", required=True, min_value=0, format="%.2f")
        },
        key="polybag_editor"
    )
    
    # Update session state
    st.session_state.polybag_costs = edited_polybag_df
    
    # Table 4: Stretch wrap cost
    st.markdown("**Table 4: Stretch wrap cost**")
    
    # Initialize stretch wrap costs in session state
    if 'stretchwrap_costs' not in st.session_state:
        st.session_state.stretchwrap_costs = pd.DataFrame({
            "Area (mm²)": [210000],
            "Cost (LKR/mm²)": [135]
        })
    
    # Create editable stretch wrap costs table
    edited_stretchwrap_df = st.data_editor(
        st.session_state.stretchwrap_costs,
        num_rows="dynamic",
        use_container_width=True,
        column_config={
            "Area (mm²)": st.column_config.NumberColumn("Area (mm²)", required=True, min_value=0),
            "Cost (LKR/mm²)": st.column_config.NumberColumn("Cost (LKR/mm²)", required=True, min_value=0, format="%.10f")
        },
        key="stretchwrap_editor"
    )
    
    # Update session state
    st.session_state.stretchwrap_costs = edited_stretchwrap_df
    
    # Add packing type selection
    packing_type = st.selectbox(
        "Select Packing Type",
        ["polybag", "cardboard box"],
        key="secondary_packing_type"
    )
    
    # Add Calculate button for secondary calculations
    st.markdown("---")
    calculate_secondary_col1, calculate_secondary_col2, calculate_secondary_col3 = st.columns([1, 1, 1])
    with calculate_secondary_col2:
        calculate_secondary_btn = st.button("🔢 Calculate Secondary Packing Costs", 
                                          type="primary", 
                                          use_container_width=True,
                                          on_click=trigger_secondary_calculation)
    
    st.divider()
    
    # Display secondary calculations when triggered
    if st.session_state.calculate_secondary:
        st.subheader("Total Secondary Packing Cost Per Profile")
        
        if not st.session_state.secondary_sku_data.empty:
            # Check which method is used
            use_method1 = not st.session_state.bundling_data.empty
            use_method2 = not st.session_state.bundle_size_data.empty
            
            if not use_method1 and not use_method2:
                st.warning("Please enter data in either Method 1 (Number of layers) or Method 2 (Size of bundle)")
            else:
                # Get data for calculations
                material_cost_dict = dict(zip(
                    st.session_state.secondary_material_costs["Material"],
                    st.session_state.secondary_material_costs["Cost/ m²"]
                ))
                box_data = st.session_state.secondary_box_costs.iloc[0]
                polybag_data = st.session_state.polybag_costs.iloc[0]
                stretchwrap_data = st.session_state.stretchwrap_costs.iloc[0]
                
                # Prepare calculations data
                secondary_calculations_data = []
                
                for _, sku in st.session_state.secondary_sku_data.iterrows():
                    try:
                        # Extract SKU dimensions
                        profile_width = float(sku["Width/mm"])
                        profile_height = float(sku["Height/mm"])
                        profile_length = float(sku["Length/mm"])
                        sku_no = sku["SKU No"]
                        
                        # Calculate Profiles per bundle based on selected method
                        profiles_per_bundle = 0
                        
                        if use_method1:
                            # Method 1: Number of layers method
                            bundling_data = st.session_state.bundling_data.iloc[0]
                            rows_per_bundle = float(bundling_data["Number of rows/bundle"])
                            layers_per_bundle = float(bundling_data["Number of layer/bundle"])
                            profiles_per_bundle = rows_per_bundle * layers_per_bundle
                            
                        elif use_method2:
                            # Method 2: Size of bundle method
                            bundle_size_data = st.session_state.bundle_size_data.iloc[0]
                            bundle_width = float(bundle_size_data["Bundle width/mm"])
                            bundle_height = float(bundle_size_data["Bundle Height/mm"])
                            
                            # Check for division by zero
                            if profile_width > 0 and profile_height > 0:
                                profiles_per_bundle = (bundle_width / profile_width) * (bundle_height / profile_height)
                        
                        # Calculate Packing cost(LKR/profile)
                        packing_cost_per_profile = 0
                        
                        if packing_type == "polybag":
                            polybag_size_inches = polybag_data["Polybag size (inches)"]
                            polybag_cost_per_m = polybag_data["Cost/m (LKR/m)"]
                            
                            if polybag_size_inches > 0 and profiles_per_bundle > 0 and 24.5 > 0:
                                packing_cost_per_profile = (polybag_cost_per_m / 
                                                          (polybag_size_inches * 24.5 * profiles_per_bundle)) * profile_length
                        
                        elif packing_type == "cardboard box":
                            box_volume = box_data["Length(mm)"] * box_data["Width (mm)"] * box_data["Height (mm)"]
                            
                            # Get bundle dimensions based on method used
                            if use_method1:
                                bundling_data = st.session_state.bundling_data.iloc[0]
                                rows_per_bundle = float(bundling_data["Number of rows/bundle"])
                                layers_per_bundle = float(bundling_data["Number of layer/bundle"])
                                
                                width_prof_type = bundling_data["width prof.type"]
                                if width_prof_type == "W/mm":
                                    bundle_width = profile_width * rows_per_bundle
                                    bundle_height = profile_height * layers_per_bundle
                                else:
                                    bundle_width = profile_height * rows_per_bundle
                                    bundle_height = profile_width * layers_per_bundle
                                
                            else:
                                bundle_size_data = st.session_state.bundle_size_data.iloc[0]
                                bundle_width = float(bundle_size_data["Bundle width/mm"])
                                bundle_height = float(bundle_size_data["Bundle Height/mm"])
                            
                            if box_volume > 0 and profiles_per_bundle > 0:
                                packing_cost_per_profile = (box_data["Cost (LKR)"] / (box_volume * profiles_per_bundle)) * \
                                                          (bundle_height * bundle_width * profile_length)
                        
                        # Calculate Stretchwrap cost (LKR/prof.)
                        stretchwrap_cost_per_profile = 0
                        if eco_friendly_tab2 == "Stretch wrap":
                            if stretchwrap_data["Area (mm²)"] > 0 and profiles_per_bundle > 0:
                                if use_method1:
                                    bundling_data = st.session_state.bundling_data.iloc[0]
                                    rows_per_bundle = float(bundling_data["Number of rows/bundle"])
                                    layers_per_bundle = float(bundling_data["Number of layer/bundle"])
                                    
                                    width_prof_type = bundling_data["width prof.type"]
                                    if width_prof_type == "W/mm":
                                        bundle_width = profile_width * rows_per_bundle
                                        bundle_height = profile_height * layers_per_bundle
                                    else:
                                        bundle_width = profile_height * rows_per_bundle
                                        bundle_height = profile_width * layers_per_bundle
                                        
                                else:
                                    bundle_size_data = st.session_state.bundle_size_data.iloc[0]
                                    bundle_width = float(bundle_size_data["Bundle width/mm"])
                                    bundle_height = float(bundle_size_data["Bundle Height/mm"])
                                
                                stretchwrap_cost_per_profile = (stretchwrap_data["Cost (LKR/mm²)"] / 
                                                               (stretchwrap_data["Area (mm²)"] * profiles_per_bundle)) * \
                                                              (bundle_width * bundle_height)
                        
                        # Calculate Protective tape cost (LKR/profile)
                        protective_tape_cost_per_profile = 0
                        if protective_tape_tab2 == "Yes":
                            if use_method1:
                                bundling_data = st.session_state.bundling_data.iloc[0]
                                rows_per_bundle = float(bundling_data["Number of rows/bundle"])
                                layers_per_bundle = float(bundling_data["Number of layer/bundle"])
                                
                                width_prof_type = bundling_data["width prof.type"]
                                if width_prof_type == "W/mm":
                                    bundle_width = profile_width * rows_per_bundle
                                    bundle_height = profile_height * layers_per_bundle
                                else:
                                    bundle_width = profile_height * rows_per_bundle
                                    bundle_height = profile_width * layers_per_bundle
                                    
                            else:
                                bundle_size_data = st.session_state.bundle_size_data.iloc[0]
                                bundle_width = float(bundle_size_data["Bundle width/mm"])
                                bundle_height = float(bundle_size_data["Bundle Height/mm"])
                            
                            bundle_surface_area_m2 = (2 * ((bundle_width * bundle_height) + 
                                                         (bundle_width * profile_length) + 
                                                         (bundle_height * profile_length))) / (1000 * 1000)
                            
                            protective_tape_cost_per_m2 = material_cost_dict.get("Protective Tape", 0)
                            total_protective_tape_cost = bundle_surface_area_m2 * protective_tape_cost_per_m2
                            
                            if profiles_per_bundle > 0:
                                protective_tape_cost_per_profile = total_protective_tape_cost / profiles_per_bundle
                        
                        # Calculate Total cost per profile
                        total_cost_per_profile = (packing_cost_per_profile + 
                                                stretchwrap_cost_per_profile + 
                                                protective_tape_cost_per_profile)
                        
                        # Add to calculations data
                        secondary_calculations_data.append({
                            "SKU": sku_no,
                            "Profiles per bundle": round(profiles_per_bundle, 2),
                            "Packing type": packing_type,
                            "Packing cost(LKR/profile)": round(packing_cost_per_profile, 4),
                            "Stretchwrap cost (LKR/prof.)": round(stretchwrap_cost_per_profile, 4),
                            "Protective tape cost (LKR/profile)": round(protective_tape_cost_per_profile, 4),
                            "Total cost per profile": round(total_cost_per_profile, 4)
                        })
                        
                    except (ValueError, TypeError, ZeroDivisionError) as e:
                        continue
                
                if secondary_calculations_data:
                    st.session_state.secondary_calculations = pd.DataFrame(secondary_calculations_data)
                    st.dataframe(st.session_state.secondary_calculations, use_container_width=True)
                    
                    total_cost_all = sum(item["Total cost per profile"] for item in secondary_calculations_data)
                    st.metric("**Total Secondary Packing Cost (All SKUs)**", f"LKR {total_cost_all:,.4f}")
                else:
                    st.warning("Unable to calculate costs. Please check all input data is valid.")
        else:
            st.info("Enter SKU data to see secondary packing cost calculations.")
    
    # Reset calculation flag after displaying results
    if st.session_state.calculate_secondary:
        st.session_state.calculate_secondary = False

# Create download button at the bottom
st.markdown("---")
col1, col2, col3 = st.columns([1, 2, 1])
with col2:
    if st.button("📥 Download Complete Report (Excel)", type="primary", use_container_width=True):
        try:
            # Import here to avoid circular imports
            from io import BytesIO
            
            # Create an Excel writer
            output = BytesIO()
            with pd.ExcelWriter(output, engine='openpyxl') as writer:
                # Sheet 1: Primary Calculations
                if 'primary_calculations' in st.session_state:
                    primary_summary = pd.DataFrame({
                        'Primary Calculations Summary': ['Primary Packing Costing Report']
                    })
                    primary_summary.to_excel(writer, sheet_name='Primary Calculations', index=False, startrow=0)
                    
                    st.session_state.primary_sku_data.to_excel(writer, sheet_name='Primary Calculations', index=False, startrow=3)
                    
                    writer.sheets['Primary Calculations'].cell(row=len(st.session_state.primary_sku_data) + 6, column=1).value = 'Common Packing Selections'
                    writer.sheets['Primary Calculations'].cell(row=len(st.session_state.primary_sku_data) + 7, column=1).value = f'Finish: {st.session_state.get("finish_primary", "Mill Finish")}'
                    writer.sheets['Primary Calculations'].cell(row=len(st.session_state.primary_sku_data) + 8, column=1).value = f'Interleaving Required: {st.session_state.get("interleaving_primary", "No")}'
                    writer.sheets['Primary Calculations'].cell(row=len(st.session_state.primary_sku_data) + 9, column=1).value = f'Eco-Friendly Material: {st.session_state.get("eco_friendly_primary", "Mac foam")}'
                    writer.sheets['Primary Calculations'].cell(row=len(st.session_state.primary_sku_data) + 10, column=1).value = f'Protective Tape: {st.session_state.get("protective_tape_primary", "No")}'
                    
                    st.session_state.primary_material_costs.to_excel(writer, sheet_name='Primary Calculations', index=False, 
                                                                   startrow=len(st.session_state.primary_sku_data) + 13)
                    
                    st.session_state.primary_box_costs.to_excel(writer, sheet_name='Primary Calculations', index=False,
                                                              startrow=len(st.session_state.primary_sku_data) + len(st.session_state.primary_material_costs) + 16)
                    
                    st.session_state.primary_calculations.to_excel(writer, sheet_name='Primary Calculations', index=False,
                                                                 startrow=len(st.session_state.primary_sku_data) + len(st.session_state.primary_material_costs) + len(st.session_state.primary_box_costs) + 19)
                
                # Sheet 2: Secondary Calculations
                if 'secondary_calculations' in st.session_state:
                    secondary_summary = pd.DataFrame({
                        'Secondary Calculations Summary': ['Secondary Packing Costing Report']
                    })
                    secondary_summary.to_excel(writer, sheet_name='Secondary Calculations', index=False, startrow=0)
                    
                    st.session_state.secondary_sku_data.to_excel(writer, sheet_name='Secondary Calculations', index=False, startrow=3)
                    
                    writer.sheets['Secondary Calculations'].cell(row=len(st.session_state.secondary_sku_data) + 6, column=1).value = 'Common Packing Selections'
                    writer.sheets['Secondary Calculations'].cell(row=len(st.session_state.secondary_sku_data) + 7, column=1).value = f'Finish: {st.session_state.get("finish_secondary", "Mill Finish")}'
                    writer.sheets['Secondary Calculations'].cell(row=len(st.session_state.secondary_sku_data) + 8, column=1).value = f'Interleaving Required: {st.session_state.get("interleaving_secondary", "No")}'
                    writer.sheets['Secondary Calculations'].cell(row=len(st.session_state.secondary_sku_data) + 9, column=1).value = f'Eco-Friendly Material: {st.session_state.get("eco_friendly_secondary", "Mac foam")}'
                    writer.sheets['Secondary Calculations'].cell(row=len(st.session_state.secondary_sku_data) + 10, column=1).value = f'Protective Tape: {st.session_state.get("protective_tape_secondary", "No")}'
                    
                    if 'bundling_data' in st.session_state and not st.session_state.bundling_data.empty:
                        st.session_state.bundling_data.to_excel(writer, sheet_name='Secondary Calculations', index=False,
                                                               startrow=len(st.session_state.secondary_sku_data) + 13)
                    
                    if 'bundle_size_data' in st.session_state and not st.session_state.bundle_size_data.empty:
                        start_row = len(st.session_state.secondary_sku_data) + len(st.session_state.bundling_data) + 16 if 'bundling_data' in st.session_state and not st.session_state.bundling_data.empty else len(st.session_state.secondary_sku_data) + 13
                        st.session_state.bundle_size_data.to_excel(writer, sheet_name='Secondary Calculations', index=False,
                                                                  startrow=start_row)
                    
                    if 'secondary_calculations' in st.session_state:
                        next_row = len(st.session_state.secondary_sku_data) + 16
                        if 'bundling_data' in st.session_state and not st.session_state.bundling_data.empty:
                            next_row += len(st.session_state.bundling_data) + 3
                        if 'bundle_size_data' in st.session_state and not st.session_state.bundle_size_data.empty:
                            next_row += len(st.session_state.bundle_size_data) + 3
                        
                        writer.sheets['Secondary Calculations'].cell(row=next_row, column=1).value = 'Secondary Packing Cost Per Profile'
                        st.session_state.secondary_calculations.to_excel(writer, sheet_name='Secondary Calculations', index=False,
                                                                       startrow=next_row + 2)
            
            output.seek(0)
            
            st.download_button(
                label="⬇️ Click to Download Excel File",
                data=output.getvalue(),
                file_name="packing_costing_report.xlsx",
                mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                use_container_width=True
            )
        except Exception as e:
            st.error(f"Error generating report: {str(e)}")

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

# Create tabs
tab1, tab2 = st.tabs(["Primary Calculations", "Secondary Calculations"])

with tab1:
    st.header("Primary Calculations")
    
    # Sub topic 1 - SKU Table with dimensions
    st.subheader("SKU Table with dimensions")
    
    # Create initial empty dataframe for SKU table
    sku_columns = ["SKU No", "Width/mm", "Height/mm", "Length/mm", "Comment on fabrication"]
    initial_sku_data = pd.DataFrame(columns=sku_columns)
    
    # Create editable dataframe for SKU input
    edited_sku_df = st.data_editor(
        initial_sku_data,
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
    material_costs = pd.DataFrame({
        "Material": ["McFoam", "Craft Paper", "Protective Tape", "Stretchwrap"],
        "Cost/ m²": [51.00, 34.65, 100.65, 14.38]
    })
    
    edited_material_df = st.data_editor(
        material_costs,
        num_rows="dynamic",
        use_container_width=True,
        column_config={
            "Material": st.column_config.TextColumn("Material", required=True),
            "Cost/ m²": st.column_config.NumberColumn("Cost/ m²", required=True, min_value=0, format="%.2f")
        },
        key="material_editor_primary"
    )
    
    # Table 2: Cardboard Box Cost
    st.markdown("**Table 2: Cardboard Box Cost**")
    
    # Create editable box costs table
    box_costs = pd.DataFrame({
        "Length(mm)": [330],
        "Width (mm)": [210],
        "Height (mm)": [135],
        "Cost (LKR)": [205.00]
    })
    
    edited_box_df = st.data_editor(
        box_costs,
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
    
    # Calculate and display Table 3: Primary Packing Total Cost
    st.markdown("**Table 3: Primary Packing Total Cost**")
    
    if not edited_sku_df.empty:
        # Prepare calculations
        calculations_data = []
        
        # Get material costs as dictionary
        material_cost_dict = dict(zip(
            edited_material_df["Material"],
            edited_material_df["Cost/ m²"]
        ))
        
        # Get reference box dimensions and cost
        ref_box = edited_box_df.iloc[0]
        ref_volume = ref_box["Length(mm)"] * ref_box["Width (mm)"] * ref_box["Height (mm)"]
        
        for _, sku in edited_sku_df.iterrows():
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
                packing_cost = (sku_volume / ref_volume) * ref_box["Cost (LKR)"]
                
                # Calculate Total Cost
                total_cost = interleaving_cost + protective_tape_cost + packing_cost
                
                calculations_data.append({
                    "SKU": sku["SKU No"],
                    "SA(m²)": round(sa_m2, 4),
                    "Interleaving cost": round(interleaving_cost, 2),
                    "Protective tape cost": round(protective_tape_cost, 2),
                    "Packing type": "Cardboard box",
                    "Packing Cost (LKR)": round(packing_cost, 2),
                    "Total Cost": round(total_cost, 2)
                })
                
            except (ValueError, TypeError):
                continue
        
        if calculations_data:
            calculations_df = pd.DataFrame(calculations_data)
            st.dataframe(calculations_df, use_container_width=True)
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
    
    # SKU input table (same as tab1)
    st.subheader("SKU Table with dimensions")
    
    # Create empty dataframe for SKU table
    initial_sku_data_tab2 = pd.DataFrame(columns=sku_columns)
    
    edited_sku_df_tab2 = st.data_editor(
        initial_sku_data_tab2,
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
    
    st.divider()
    
    # Common packing selections (same as tab1)
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
    
    # Section 1 - Number of layers
    st.markdown("**Section 1 - Number of layers**")
    
    # Initialize bundling data in session state
    if 'bundling_data' not in st.session_state:
        st.session_state.bundling_data = pd.DataFrame(columns=[
            "Number of rows/bundle", 
            "Number of layer/bundle", 
            "width prof.type", 
            "height prof.type"
        ])
    
    # Create callback to update height prof.type based on width selection
    def update_height_prof_type(df):
        if not df.empty:
            for idx, row in df.iterrows():
                width_prof = row["width prof.type"]
                if width_prof == "W/mm":
                    df.at[idx, "height prof.type"] = "H/mm"
                elif width_prof == "H/mm":
                    df.at[idx, "height prof.type"] = "W/mm"
        return df
    
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
    
    # Update height prof.type based on width prof.type selection
    updated_bundling_df = update_height_prof_type(edited_bundling_df.copy())
    st.session_state.bundling_data = updated_bundling_df
    
    st.divider()
    
    # Section 2 - Size of bundle
    st.markdown("**Section 2 - Size of bundle**")
    
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
    
    # Table 1: Primary Packing Material Costs (same as primary section)
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
    
    # Table 2: Cardboard Box Cost (same as primary section)
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
            "Area (mm²)": [210000],  # Default 1 m² = 1,000,000 mm²
            "Cost (LKR/mm²)": [135]  # Default cost
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
    
    st.divider()
    
    # Subsection: Total Secondary packing cost per profile table
    st.subheader("Total Secondary Packing Cost Per Profile")
    
    # Add packing type selection
    packing_type = st.selectbox(
        "Select Packing Type",
        ["polybag", "cardboard box"],
        key="secondary_packing_type"
    )
    
    # Calculate and display the table
    if (not edited_sku_df_tab2.empty and 
        not st.session_state.bundle_size_data.empty and
        not st.session_state.bundling_data.empty):
        
        # Get data for calculations
        bundle_size_data = st.session_state.bundle_size_data.iloc[0]
        bundling_data = st.session_state.bundling_data.iloc[0]
        material_cost_dict = dict(zip(
            st.session_state.secondary_material_costs["Material"],
            st.session_state.secondary_material_costs["Cost/ m²"]
        ))
        box_data = st.session_state.secondary_box_costs.iloc[0]
        polybag_data = st.session_state.polybag_costs.iloc[0]
        stretchwrap_data = st.session_state.stretchwrap_costs.iloc[0]
        
        # Prepare calculations data
        secondary_calculations_data = []
        
        for _, sku in edited_sku_df_tab2.iterrows():
            try:
                # Extract SKU dimensions
                profile_width = float(sku["Width/mm"])
                profile_height = float(sku["Height/mm"])
                profile_length = float(sku["Length/mm"])
                sku_no = sku["SKU No"]
                
                # Bundle dimensions
                bundle_width = float(bundle_size_data["Bundle width/mm"])
                bundle_height = float(bundle_size_data["Bundle Height/mm"])
                
                # Calculate Profiles per bundle
                profiles_per_bundle = (bundle_width / profile_width) * (bundle_height / profile_height)
                
                # Calculate Packing cost(LKR/profile)
                packing_cost_per_profile = 0
                if packing_type == "polybag":
                    # (polybag cost/(polybag size*24.5*profiles per bundle))*Profile length
                    # Convert inches to mm: 1 inch = 25.4 mm
                    polybag_size_mm = polybag_data["Polybag size (inches)"] * 25.4
                    packing_cost_per_profile = (polybag_data["Cost/m (LKR/m)"] / 
                                              (polybag_size_mm * 24.5 * profiles_per_bundle)) * profile_length
                
                elif packing_type == "cardboard box":
                    # (cardboard box price/cardboard box volume*profiles per bundle)*(Bundle height*Bundle width*bundle length)
                    # Note: Need bundle length - using profile length as bundle length
                    box_volume = box_data["Length(mm)"] * box_data["Width (mm)"] * box_data["Height (mm)"]
                    if box_volume > 0:
                        packing_cost_per_profile = (box_data["Cost (LKR)"] / (box_volume * profiles_per_bundle)) * \
                                                  (bundle_height * bundle_width * profile_length)
                
                # Calculate Stretchwrap cost (LKR/prof.)
                stretchwrap_cost_per_profile = 0
                if stretchwrap_data["Area (mm²)"] > 0:
                    stretchwrap_cost_per_profile = (stretchwrap_data["Cost (LKR/mm²)"] / 
                                                   (stretchwrap_data["Area (mm²)"] * profiles_per_bundle)) * \
                                                  (profile_width * profile_height)
                
                # Calculate Protective tape cost (LKR/profile)
                protective_tape_cost_per_profile = 0
                if protective_tape_tab2 == "Yes":
                    # Calculate bundle surface area in m²
                    bundle_surface_area_m2 = (2 * ((bundle_width * bundle_height) + 
                                                 (bundle_width * profile_length) + 
                                                 (bundle_height * profile_length))) / (1000 * 1000)
                    
                    # Get protective tape cost per m²
                    protective_tape_cost_per_m2 = material_cost_dict.get("Protective Tape", 0)
                    
                    # Calculate total protective tape cost for bundle
                    total_protective_tape_cost = bundle_surface_area_m2 * protective_tape_cost_per_m2
                    
                    # Cost per profile
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
            secondary_calculations_df = pd.DataFrame(secondary_calculations_data)
            st.dataframe(secondary_calculations_df, use_container_width=True)
            
            # Calculate and display total summary
            total_cost_all = sum(item["Total cost per profile"] for item in secondary_calculations_data)
            st.metric("**Total Secondary Packing Cost (All SKUs)**", f"LKR {total_cost_all:,.4f}")
        else:
            st.warning("Unable to calculate costs. Please check all input data is valid.")
    else:
        st.info("Enter SKU data, bundle data, and bundling data to see secondary packing cost calculations.")

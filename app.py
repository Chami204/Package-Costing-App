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
if 'sku_data' not in st.session_state:
    sku_columns = ["SKU No", "Width/mm", "Height/mm", "Length/mm", "Comment on fabrication"]
    st.session_state.sku_data = pd.DataFrame(columns=sku_columns)

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
        st.session_state.sku_data,
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
    st.session_state.sku_data = edited_sku_df
    
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
        key="material_editor"
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
        key="box_editor"
    )
    
    # Update session state
    st.session_state.box_costs = edited_box_df
    
    # Calculate and display Table 3: Primary Packing Total Cost
    st.markdown("**Table 3: Primary Packing Total Cost**")
    
    if not st.session_state.sku_data.empty:
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
        
        for _, sku in st.session_state.sku_data.iterrows():
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
                # Skip if dimensions are not valid numbers
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
    
    # Section 1: SKU Table with dimensions (same as tab1)
    st.subheader("SKU Table with dimensions")
    
    # Create editable dataframe for SKU input
    edited_sku_df_secondary = st.data_editor(
        st.session_state.sku_data,
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
    st.session_state.sku_data = edited_sku_df_secondary
    
    st.divider()
    
    # Section 2: Common Packing selections (same as tab1)
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
    
    # Section 3: Secondary Packing Calculations
    st.subheader("Secondary Packing Cost Calculations")
    
    # Add new inputs specific to secondary packing
    st.markdown("**Secondary Packing Parameters**")
    
    sec_col1, sec_col2, sec_col3 = st.columns(3)
    
    with sec_col1:
        pallet_type = st.selectbox(
            "Pallet Type",
            ["Wooden Pallet", "Plastic Pallet", "Paper Pallet", "Metal Pallet"],
            key="pallet_type"
        )
    
    with sec_col2:
        crate_type = st.selectbox(
            "Crate Type",
            ["Wooden Crate", "Plastic Crate", "Cardboard Crate", "Metal Crate"],
            key="crate_type"
        )
    
    with sec_col3:
        container_type = st.selectbox(
            "Container Type",
            ["20ft Container", "40ft Container", "40ft HC Container"],
            key="container_type"
        )
    
    # Cost inputs for secondary packing
    st.markdown("**Secondary Packing Costs**")
    
    cost_col1, cost_col2, cost_col3 = st.columns(3)
    
    with cost_col1:
        pallet_cost = st.number_input(
            "Pallet Cost (LKR)",
            min_value=0.0,
            value=2500.0,
            step=100.0,
            key="pallet_cost"
        )
    
    with cost_col2:
        crate_cost = st.number_input(
            "Crate Cost (LKR)",
            min_value=0.0,
            value=5000.0,
            step=500.0,
            key="crate_cost"
        )
    
    with cost_col3:
        strapping_cost = st.number_input(
            "Strapping/Covering Cost (LKR)",
            min_value=0.0,
            value=1500.0,
            step=100.0,
            key="strapping_cost"
        )
    
    st.divider()
    
    # Section 4: Secondary Packing Total Cost Calculation
    st.subheader("Secondary Packing Total Cost")
    
    if not st.session_state.sku_data.empty:
        # Calculate secondary packing
        secondary_data = []
        total_volume = 0
        total_weight = 0
        
        for _, sku in st.session_state.sku_data.iterrows():
            try:
                # Extract SKU dimensions
                width = float(sku["Width/mm"])
                height = float(sku["Height/mm"])
                length = float(sku["Length/mm"])
                
                # Calculate volume in cubic meters
                volume_m3 = (width * height * length) / (1000 * 1000 * 1000)
                
                # Estimate weight (assuming standard density)
                # You can modify this based on your actual requirements
                estimated_weight = volume_m3 * 2700  # Assuming aluminum density (2700 kg/m³)
                
                # Calculate secondary packing cost
                # This is a simplified calculation - adjust based on your business logic
                sku_secondary_cost = 0
                sku_secondary_cost += pallet_cost * 0.1  # Example: 10% of pallet cost per SKU
                sku_secondary_cost += crate_cost * 0.05  # Example: 5% of crate cost per SKU
                sku_secondary_cost += strapping_cost * 0.15  # Example: 15% of strapping cost per SKU
                
                secondary_data.append({
                    "SKU": sku["SKU No"],
                    "Volume (m³)": round(volume_m3, 4),
                    "Estimated Weight (kg)": round(estimated_weight, 2),
                    "Pallet Share (LKR)": round(pallet_cost * 0.1, 2),
                    "Crate Share (LKR)": round(crate_cost * 0.05, 2),
                    "Strapping Share (LKR)": round(strapping_cost * 0.15, 2),
                    "Total Secondary Cost (LKR)": round(sku_secondary_cost, 2)
                })
                
                total_volume += volume_m3
                total_weight += estimated_weight
                
            except (ValueError, TypeError):
                continue
        
        if secondary_data:
            secondary_df = pd.DataFrame(secondary_data)
            st.dataframe(secondary_df, use_container_width=True)
            
            # Display totals
            col1, col2, col3 = st.columns(3)
            
            with col1:
                st.metric("Total Volume", f"{total_volume:.3f} m³")
            
            with col2:
                st.metric("Total Estimated Weight", f"{total_weight:.2f} kg")
            
            with col3:
                total_secondary_cost = secondary_df["Total Secondary Cost (LKR)"].sum()
                st.metric("**Total Secondary Cost**", f"LKR {total_secondary_cost:,.2f}")
            
            # Container capacity information
            st.divider()
            st.subheader("Container Loading Information")
            
            # Simple container capacity calculation
            container_capacities = {
                "20ft Container": 33.0,  # m³
                "40ft Container": 67.0,  # m³
                "40ft HC Container": 76.0  # m³
            }
            
            container_capacity = container_capacities.get(container_type, 33.0)
            
            if total_volume > 0 and container_capacity > 0:
                containers_needed = np.ceil(total_volume / container_capacity)
                utilization_percentage = (total_volume / (container_capacity * containers_needed)) * 100
                
                info_col1, info_col2, info_col3 = st.columns(3)
                
                with info_col1:
                    st.metric(f"{container_type} Capacity", f"{container_capacity} m³")
                
                with info_col2:
                    st.metric("Containers Needed", f"{int(containers_needed)}")
                
                with info_col3:
                    st.metric("Utilization", f"{utilization_percentage:.1f}%")
        else:
            st.warning("Please enter valid SKU data with numeric dimensions.")
    else:
        st.info("Enter SKU data in the table above to see secondary packing calculations.")
    
    st.divider()
    
    # Section 5: Special Notes for Secondary Packing
    st.subheader("Special Notes")
    
    notes_box = f"""
    **Secondary Packing Specifications:**
    
    - **Pallet Type:** {pallet_type}
    - **Crate Type:** {crate_type}
    - **Container Type:** {container_type}
    
    **Additional Notes:**
    
    1. Secondary packing costs include palletizing, crating, and strapping charges
    2. Container loading is calculated based on volume optimization
    3. Weight estimates are approximate and based on standard material density
    4. Actual costs may vary based on specific handling requirements
    5. Insurance and shipping costs are not included in this calculation
    """
    
    st.info(notes_box)

# Footer
st.divider()
st.caption("Packing Costing Calculator v1.0 | All dimensions should be entered in millimeters (mm)")

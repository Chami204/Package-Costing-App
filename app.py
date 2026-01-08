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
        }
    )
    
    st.divider()
    
    # Section 2: Common Packing selections
    st.subheader("Common Packing Selections")
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        finish = st.selectbox(
            "Finish",
            ["Mill Finish", "Anodised", "PC", "WF"]
        )
    
    with col2:
        interleaving_required = st.selectbox(
            "Interleaving Required",
            ["Yes", "No"]
        )
    
    with col3:
        eco_friendly = st.selectbox(
            "Eco-Friendly Packing Material",
            ["Mac foam", "Stretch wrap", "Craft Paper"]
        )
    
    with col4:
        protective_tape = st.selectbox(
            "Protective Tape (Customer Specified)",
            ["Yes", "No"]
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
        }
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
        }
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
        }
    )
    
    st.divider()
    
    # Common packing selections (same as tab1)
    st.subheader("Common Packing Selections")
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        finish_tab2 = st.selectbox(
            "Finish",
            ["Mill Finish", "Anodised", "PC", "WF"],
            key="finish_tab2"
        )
    
    with col2:
        interleaving_required_tab2 = st.selectbox(
            "Interleaving Required",
            ["Yes", "No"],
            key="interleaving_tab2"
        )
    
    with col3:
        eco_friendly_tab2 = st.selectbox(
            "Eco-Friendly Packing Material",
            ["Mac foam", "Stretch wrap", "Craft Paper"],
            key="eco_friendly_tab2"
        )
    
    with col4:
        protective_tape_tab2 = st.selectbox(
            "Protective Tape (Customer Specified)",
            ["Yes", "No"],
            key="protective_tape_tab2"
        )
    
    # Secondary calculations placeholder
    st.divider()
    st.subheader("Secondary Packing Calculations")
    st.info("Secondary packing calculations will be added here.")

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


# Create download button
def create_excel_report():
    """Create Excel report with primary and secondary calculations"""
    from io import BytesIO
    
    # Create an Excel writer
    output = BytesIO()
    with pd.ExcelWriter(output, engine='openpyxl') as writer:
        # Sheet 1: Primary Calculations
        if 'sku_data' in locals() and not edited_sku_df.empty:
            # Create a summary dataframe for primary calculations
            primary_summary = pd.DataFrame({
                'Primary Calculations Summary': ['Primary Packing Costing Report']
            })
            primary_summary.to_excel(writer, sheet_name='Primary Calculations', index=False, startrow=0)
            
            # Add SKU Table
            edited_sku_df.to_excel(writer, sheet_name='Primary Calculations', index=False, startrow=3)
            
            # Add spacing
            writer.sheets['Primary Calculations'].cell(row=len(edited_sku_df) + 6, column=1).value = 'Common Packing Selections'
            writer.sheets['Primary Calculations'].cell(row=len(edited_sku_df) + 7, column=1).value = f'Finish: {finish}'
            writer.sheets['Primary Calculations'].cell(row=len(edited_sku_df) + 8, column=1).value = f'Interleaving Required: {interleaving_required}'
            writer.sheets['Primary Calculations'].cell(row=len(edited_sku_df) + 9, column=1).value = f'Eco-Friendly Material: {eco_friendly}'
            writer.sheets['Primary Calculations'].cell(row=len(edited_sku_df) + 10, column=1).value = f'Protective Tape: {protective_tape}'
            
            # Add Material Costs
            edited_material_df.to_excel(writer, sheet_name='Primary Calculations', index=False, 
                                       startrow=len(edited_sku_df) + 13)
            
            # Add Cardboard Box Costs
            edited_box_df.to_excel(writer, sheet_name='Primary Calculations', index=False,
                                  startrow=len(edited_sku_df) + len(edited_material_df) + 16)
            
            # Add Primary Packing Total Cost
            if 'edited_primary_calc' in st.session_state:
                st.session_state.edited_primary_calc.to_excel(writer, sheet_name='Primary Calculations', index=False,
                                                            startrow=len(edited_sku_df) + len(edited_material_df) + len(edited_box_df) + 19)
            elif 'calculations_df' in locals():
                calculations_df.to_excel(writer, sheet_name='Primary Calculations', index=False,
                                        startrow=len(edited_sku_df) + len(edited_material_df) + len(edited_box_df) + 19)
        
        # Sheet 2: Secondary Calculations
        if 'edited_sku_df_tab2' in locals() and not edited_sku_df_tab2.empty:
            # Create a summary dataframe for secondary calculations
            secondary_summary = pd.DataFrame({
                'Secondary Calculations Summary': ['Secondary Packing Costing Report']
            })
            secondary_summary.to_excel(writer, sheet_name='Secondary Calculations', index=False, startrow=0)
            
            # Add SKU Table
            edited_sku_df_tab2.to_excel(writer, sheet_name='Secondary Calculations', index=False, startrow=3)
            
            # Add Common Packing Selections
            writer.sheets['Secondary Calculations'].cell(row=len(edited_sku_df_tab2) + 6, column=1).value = 'Common Packing Selections'
            writer.sheets['Secondary Calculations'].cell(row=len(edited_sku_df_tab2) + 7, column=1).value = f'Finish: {finish_tab2}'
            writer.sheets['Secondary Calculations'].cell(row=len(edited_sku_df_tab2) + 8, column=1).value = f'Interleaving Required: {interleaving_required_tab2}'
            writer.sheets['Secondary Calculations'].cell(row=len(edited_sku_df_tab2) + 9, column=1).value = f'Eco-Friendly Material: {eco_friendly_tab2}'
            writer.sheets['Secondary Calculations'].cell(row=len(edited_sku_df_tab2) + 10, column=1).value = f'Protective Tape: {protective_tape_tab2}'
            
            # Add Bundling Data if available
            if 'bundling_data' in st.session_state and not st.session_state.bundling_data.empty:
                st.session_state.bundling_data.to_excel(writer, sheet_name='Secondary Calculations', index=False,
                                                       startrow=len(edited_sku_df_tab2) + 13, 
                                                       header=True)
            
            # Add Bundle Size Data if available
            if 'bundle_size_data' in st.session_state and not st.session_state.bundle_size_data.empty:
                start_row = len(edited_sku_df_tab2) + len(st.session_state.bundling_data) + 16 if 'bundling_data' in st.session_state and not st.session_state.bundling_data.empty else len(edited_sku_df_tab2) + 13
                st.session_state.bundle_size_data.to_excel(writer, sheet_name='Secondary Calculations', index=False,
                                                          startrow=start_row,
                                                          header=True)
            
            # Add Secondary Packing Cost Per Profile if available
            if 'secondary_calculations_df' in locals():
                # Find the next available row
                next_row = len(edited_sku_df_tab2) + 16
                if 'bundling_data' in st.session_state and not st.session_state.bundling_data.empty:
                    next_row += len(st.session_state.bundling_data) + 3
                if 'bundle_size_data' in st.session_state and not st.session_state.bundle_size_data.empty:
                    next_row += len(st.session_state.bundle_size_data) + 3
                
                writer.sheets['Secondary Calculations'].cell(row=next_row, column=1).value = 'Secondary Packing Cost Per Profile'
                secondary_calculations_df.to_excel(writer, sheet_name='Secondary Calculations', index=False,
                                                  startrow=next_row + 2)
            
            # Add Crate/Pallet Dimensions if available
            if 'crate_pallet_data' in st.session_state and not st.session_state.crate_pallet_data.empty:
                # Find the next available row
                next_row = len(edited_sku_df_tab2) + 16
                if 'bundling_data' in st.session_state and not st.session_state.bundling_data.empty:
                    next_row += len(st.session_state.bundling_data) + 3
                if 'bundle_size_data' in st.session_state and not st.session_state.bundle_size_data.empty:
                    next_row += len(st.session_state.bundle_size_data) + 3
                if 'secondary_calculations_df' in locals():
                    next_row += len(secondary_calculations_df) + 5
                
                writer.sheets['Secondary Calculations'].cell(row=next_row, column=1).value = 'Crate/Pallet Dimensions'
                st.session_state.crate_pallet_data.to_excel(writer, sheet_name='Secondary Calculations', index=False,
                                                           startrow=next_row + 2)
            
            # Add Crate/Pallet Cost Calculations if available
            if 'crate_pallet_calculations_df' in locals():
                # Find the next available row
                next_row = len(edited_sku_df_tab2) + 16
                if 'bundling_data' in st.session_state and not st.session_state.bundling_data.empty:
                    next_row += len(st.session_state.bundling_data) + 3
                if 'bundle_size_data' in st.session_state and not st.session_state.bundle_size_data.empty:
                    next_row += len(st.session_state.bundle_size_data) + 3
                if 'secondary_calculations_df' in locals():
                    next_row += len(secondary_calculations_df) + 5
                if 'crate_pallet_data' in st.session_state and not st.session_state.crate_pallet_data.empty:
                    next_row += len(st.session_state.crate_pallet_data) + 5
                
                writer.sheets['Secondary Calculations'].cell(row=next_row, column=1).value = 'Crate/Pallet Cost Calculations'
                crate_pallet_calculations_df.to_excel(writer, sheet_name='Secondary Calculations', index=False,
                                                     startrow=next_row + 2)
    
    # Get the Excel data
    output.seek(0)
    return output.getvalue()

# Add download button at the top
col1, col2, col3 = st.columns([1, 2, 1])
with col2:
    if st.button("📥 Download Complete Report (Excel)", type="primary", use_container_width=True):
        try:
            excel_data = create_excel_report()
            st.download_button(
                label="⬇️ Click to Download Excel File",
                data=excel_data,
                file_name="packing_costing_report.xlsx",
                mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                use_container_width=True
            )
        except Exception as e:
            st.error(f"Error generating report: {str(e)}")






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
                # Calculate Packing Cost - Updated formula
                if ref_box["Length(mm)"] > 0 and ref_box["Width (mm)"] > 0 and ref_box["Height (mm)"] > 0:
                # ((Table 2: Cardboard Box Cost Cost LKR)/width*height*length)*(Table 3: Primary Packing Total Cost Box height/mm*Box width/mm*Box length/mm)
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
            # Create initial calculations dataframe
            calculations_df = pd.DataFrame(calculations_data)
            
            # Store reference box data for calculations
            ref_box = edited_box_df.iloc[0]
            
            # Initialize session state for edited data if not exists
            if 'edited_primary_calc' not in st.session_state:
                st.session_state.edited_primary_calc = calculations_df.copy()
            
            # Function to recalculate costs based on edited dimensions
            def recalculate_costs(df):
                ref_length = ref_box["Length(mm)"]
                ref_width = ref_box["Width (mm)"]
                ref_height = ref_box["Height (mm)"]
                ref_cost = ref_box["Cost (LKR)"]
                
                # Calculate reference box volume
                if ref_length > 0 and ref_width > 0 and ref_height > 0:
                    ref_volume = ref_length * ref_width * ref_height
                    cost_per_volume = ref_cost / ref_volume
                else:
                    cost_per_volume = 0
                
                # Recalculate for each row
                updated_df = df.copy()
                for idx, row in updated_df.iterrows():
                    try:
                        # Get box dimensions
                        box_length = float(row["Box length/mm"])
                        box_width = float(row["Box width/mm"])
                        box_height = float(row["Box height/mm"])
                        
                        # Calculate box volume
                        box_volume = box_length * box_width * box_height
                        
                        # Recalculate packing cost
                        if cost_per_volume > 0:
                            new_packing_cost = cost_per_volume * box_volume
                        else:
                            new_packing_cost = 0
                        
                        # Get original costs that shouldn't change
                        interleaving_cost = float(row["Interleaving cost"])
                        protective_tape_cost = float(row["Protective tape cost"])
                        
                        # Calculate new total cost
                        new_total_cost = interleaving_cost + protective_tape_cost + new_packing_cost
                        
                        # Update the row
                        updated_df.at[idx, "Packing Cost (LKR)"] = round(new_packing_cost, 2)
                        updated_df.at[idx, "Total Cost"] = round(new_total_cost, 2)
                        
                    except (ValueError, TypeError):
                        continue
                
                return updated_df
            
            # Create editable dataframe
            edited_df = st.data_editor(
                st.session_state.edited_primary_calc,
                num_rows="fixed",
                use_container_width=True,
                column_config={
                    "SKU": st.column_config.TextColumn("SKU", required=True, disabled=True),
                    "SA(m²)": st.column_config.NumberColumn("SA(m²)", required=True, min_value=0, format="%.4f", disabled=True),
                    "Interleaving cost": st.column_config.NumberColumn("Interleaving cost", required=True, min_value=0, format="%.2f", disabled=True),
                    "Protective tape cost": st.column_config.NumberColumn("Protective tape cost", required=True, min_value=0, format="%.2f", disabled=True),
                    "Packing type": st.column_config.TextColumn("Packing type", required=True, disabled=True),
                    "Box height/mm": st.column_config.NumberColumn("Box height/mm", required=True, min_value=0, format="%.2f"),
                    "Box width/mm": st.column_config.NumberColumn("Box width/mm", required=True, min_value=0, format="%.2f"),
                    "Box length/mm": st.column_config.NumberColumn("Box length/mm", required=True, min_value=0, format="%.2f"),
                    "Packing Cost (LKR)": st.column_config.NumberColumn("Packing Cost (LKR)", required=True, min_value=0, format="%.2f", disabled=True),
                    "Total Cost": st.column_config.NumberColumn("Total Cost", required=True, min_value=0, format="%.2f", disabled=True)
                },
                key="primary_calculations_editor"
            )
            
            # Check if data has been edited and recalculate
            if not edited_df.equals(st.session_state.edited_primary_calc):
                # Recalculate costs based on new dimensions
                recalculated_df = recalculate_costs(edited_df)
                st.session_state.edited_primary_calc = recalculated_df
                st.rerun()
            
            # Display the updated dataframe
            st.dataframe(st.session_state.edited_primary_calc, use_container_width=True)
            
            # Display total summary
            total_sum = st.session_state.edited_primary_calc["Total Cost"].sum()
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
    if not edited_sku_df_tab2.empty:
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
            
            for _, sku in edited_sku_df_tab2.iterrows():
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
                        # (Polybag Cost/(polybag size*24.5* profiles per bundle))*(profile length)
                        # Note: polybag size is in inches
                        polybag_size_inches = polybag_data["Polybag size (inches)"]
                        polybag_cost_per_m = polybag_data["Cost/m (LKR/m)"]
                        
                        # Check for valid values to avoid division by zero
                        if polybag_size_inches > 0 and profiles_per_bundle > 0 and 24.5 > 0:
                            # Convert polybag size from inches to meters (1 inch = 0.0254 m)
                            polybag_size_m = polybag_size_inches
                            packing_cost_per_profile = (polybag_cost_per_m / 
                                                      (polybag_size_m * 24.5 * profiles_per_bundle)) * profile_length
                    
                    elif packing_type == "cardboard box":
                        # Keep the same calculation as before
                        box_volume = box_data["Length(mm)"] * box_data["Width (mm)"] * box_data["Height (mm)"]
                        
                        # Get bundle dimensions based on method used
                        if use_method1:
                            # For method 1, we need to calculate bundle dimensions
                            # Use profile dimensions multiplied by rows/layers
                            bundling_data = st.session_state.bundling_data.iloc[0]
                            rows_per_bundle = float(bundling_data["Number of rows/bundle"])
                            layers_per_bundle = float(bundling_data["Number of layer/bundle"])
                            
                            # Determine orientation based on width prof.type
                            width_prof_type = bundling_data["width prof.type"]
                            if width_prof_type == "W/mm":
                                # Width is profile width, height is profile height
                                bundle_width = profile_width * rows_per_bundle
                                bundle_height = profile_height * layers_per_bundle
                            else:  # "H/mm"
                                # Width is profile height, height is profile width
                                bundle_width = profile_height * rows_per_bundle
                                bundle_height = profile_width * layers_per_bundle
                            
                        else:  # use_method2
                            bundle_size_data = st.session_state.bundle_size_data.iloc[0]
                            bundle_width = float(bundle_size_data["Bundle width/mm"])
                            bundle_height = float(bundle_size_data["Bundle Height/mm"])
                        
                        if box_volume > 0 and profiles_per_bundle > 0:
                            packing_cost_per_profile = (box_data["Cost (LKR)"] / (box_volume * profiles_per_bundle)) * \
                                                      (bundle_height * bundle_width * profile_length)
                    
                    # Calculate Stretchwrap cost (LKR/prof.) - CORRECTED CONDITION
                    stretchwrap_cost_per_profile = 0
                    # Only calculate stretchwrap cost if user selected "Stretch wrap" in Eco-Friendly Packing Material
                    if eco_friendly_tab2 == "Stretch wrap":
                        if stretchwrap_data["Area (mm²)"] > 0 and profiles_per_bundle > 0:
                            # Get bundle dimensions based on method used
                            if use_method1:
                                bundling_data = st.session_state.bundling_data.iloc[0]
                                rows_per_bundle = float(bundling_data["Number of rows/bundle"])
                                layers_per_bundle = float(bundling_data["Number of layer/bundle"])
                                
                                width_prof_type = bundling_data["width prof.type"]
                                if width_prof_type == "W/mm":
                                    # Width is profile width, height is profile height
                                    bundle_width = profile_width * rows_per_bundle
                                    bundle_height = profile_height * layers_per_bundle
                                else:  # "H/mm"
                                    # Width is profile height, height is profile width
                                    bundle_width = profile_height * rows_per_bundle
                                    bundle_height = profile_width * layers_per_bundle
                                    
                            else:  # use_method2
                                bundle_size_data = st.session_state.bundle_size_data.iloc[0]
                                bundle_width = float(bundle_size_data["Bundle width/mm"])
                                bundle_height = float(bundle_size_data["Bundle Height/mm"])
                            
                            stretchwrap_cost_per_profile = (stretchwrap_data["Cost (LKR/mm²)"] / 
                                                           (stretchwrap_data["Area (mm²)"] * profiles_per_bundle)) * \
                                                          (bundle_width * bundle_height)  # <-- CORRECTED: Use bundle dimensions
                    
                    # Calculate Protective tape cost (LKR/profile)
                    protective_tape_cost_per_profile = 0
                    if protective_tape_tab2 == "Yes":
                        # Get bundle dimensions for surface area calculation
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
                                
                        else:  # use_method2
                            bundle_size_data = st.session_state.bundle_size_data.iloc[0]
                            bundle_width = float(bundle_size_data["Bundle width/mm"])
                            bundle_height = float(bundle_size_data["Bundle Height/mm"])
                        
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
        st.info("Enter SKU data to see secondary packing cost calculations.")


    st.divider()
    
    # New Section: Crate/Pallet dimensions table
    st.subheader("Crate/Pallet Dimensions Table")
    
    # Initialize crate/pallet data in session state
    if 'crate_pallet_data' not in st.session_state:
        st.session_state.crate_pallet_data = pd.DataFrame(columns=[
            "SKU", 
            "packing method", 
            "Width/mm", 
            "Height/mm", 
            "Length/mm"
        ])
    
    # Create dataframe with SKUs from the SKU input table
    if not edited_sku_df_tab2.empty:
        # Get unique SKUs from the SKU table
        sku_list = edited_sku_df_tab2["SKU No"].unique().tolist()
        
        # Check if crate_pallet_data needs to be updated with new SKUs
        existing_skus = st.session_state.crate_pallet_data["SKU"].unique().tolist() if not st.session_state.crate_pallet_data.empty else []
        
        # Add new SKUs that aren't already in the crate/pallet table
        new_skus = [sku for sku in sku_list if sku not in existing_skus]
        
        if new_skus:
            new_rows = []
            for sku in new_skus:
                new_rows.append({
                    "SKU": sku,
                    "packing method": "pallet",  # default value
                    "Width/mm": 0,
                    "Height/mm": 0,
                    "Length/mm": 0
                })
            
            if new_rows:
                new_df = pd.DataFrame(new_rows)
                st.session_state.crate_pallet_data = pd.concat([st.session_state.crate_pallet_data, new_df], ignore_index=True)
    
    # Create editable crate/pallet dimensions table
    edited_crate_pallet_df = st.data_editor(
        st.session_state.crate_pallet_data,
        num_rows="dynamic",
        use_container_width=True,
        column_config={
            "SKU": st.column_config.TextColumn("SKU", required=True),
            "packing method": st.column_config.SelectboxColumn(
                "packing method",
                options=["pallet", "crate"],
                required=True
            ),
            "Width/mm": st.column_config.NumberColumn("Width/mm", required=True, min_value=0),
            "Height/mm": st.column_config.NumberColumn("Height/mm", required=True, min_value=0),
            "Length/mm": st.column_config.NumberColumn("Length/mm", required=True, min_value=0)
        },
        key="crate_pallet_editor"
    )
    
    # Update session state
    st.session_state.crate_pallet_data = edited_crate_pallet_df
 # New Section: Total crate/pallet cost
    st.subheader("Total Crate/Pallet Cost")
    
    # Table 1: Crate cost
    st.markdown("**Table 1: Crate Cost**")
    
    # Initialize crate costs in session state
    if 'crate_costs' not in st.session_state:
        st.session_state.crate_costs = pd.DataFrame({
            "Crate width/mm": [480],
            "Crate Height/mm": [590],
            "Crate Length/mm": [2000],
            "Cost (LKR)": [5000.00]
        })
    
    # Create editable crate costs table
    edited_crate_costs_df = st.data_editor(
        st.session_state.crate_costs,
        num_rows="dynamic",
        use_container_width=True,
        column_config={
            "Crate width/mm": st.column_config.NumberColumn("Crate width/mm", required=True, min_value=0),
            "Crate Height/mm": st.column_config.NumberColumn("Crate Height/mm", required=True, min_value=0),
            "Crate Length/mm": st.column_config.NumberColumn("Crate Length/mm", required=True, min_value=0),
            "Cost (LKR)": st.column_config.NumberColumn("Cost (LKR)", required=True, min_value=0, format="%.2f")
        },
        key="crate_costs_editor"
    )
    
    # Update session state
    st.session_state.crate_costs = edited_crate_costs_df
    
    # Table 2: Pallet Cost
    st.markdown("**Table 2: Pallet Cost**")
    
    # Initialize pallet costs in session state
    if 'pallet_costs' not in st.session_state:
        st.session_state.pallet_costs = pd.DataFrame({
            "Pallet width/mm": [2000],
            "Pallet Height/mm": [600],
            "Cost (LKR)": [3000.00]
        })
    
    # Create editable pallet costs table
    edited_pallet_costs_df = st.data_editor(
        st.session_state.pallet_costs,
        num_rows="dynamic",
        use_container_width=True,
        column_config={
            "Pallet width/mm": st.column_config.NumberColumn("Pallet width/mm", required=True, min_value=0),
            "Pallet Height/mm": st.column_config.NumberColumn("Pallet Height/mm", required=True, min_value=0),
            "Cost (LKR)": st.column_config.NumberColumn("Cost (LKR)", required=True, min_value=0, format="%.2f")
        },
        key="pallet_costs_editor"
    )
    
    # Update session state
    st.session_state.pallet_costs = edited_pallet_costs_df
    
    # Table 3: Strapping clip cost
    st.markdown("**Table 3: Strapping Clip Cost**")
    
    # Initialize strapping clip costs in session state
    if 'strapping_clip_costs' not in st.session_state:
        st.session_state.strapping_clip_costs = pd.DataFrame({
            "number of clips": [1],
            "Cost": [12.00]
        })
    
    # Create editable strapping clip costs table
    edited_strapping_clip_df = st.data_editor(
        st.session_state.strapping_clip_costs,
        num_rows="dynamic",
        use_container_width=True,
        column_config={
            "number of clips": st.column_config.NumberColumn("number of clips", required=True, min_value=1),
            "Cost": st.column_config.NumberColumn("Cost", required=True, min_value=0, format="%.2f")
        },
        key="strapping_clip_editor"
    )
    
    # Update session state
    st.session_state.strapping_clip_costs = edited_strapping_clip_df
    
    # Table 4: PP strapping cost
    st.markdown("**Table 4: PP Strapping Cost**")
    
    # Initialize PP strapping costs in session state
    if 'pp_strapping_costs' not in st.session_state:
        st.session_state.pp_strapping_costs = pd.DataFrame({
            "Strapping Length/m": [1],
            "Cost (LKR/m)": [15.00]
        })
    
    # Create editable PP strapping costs table
    edited_pp_strapping_df = st.data_editor(
        st.session_state.pp_strapping_costs,
        num_rows="dynamic",
        use_container_width=True,
        column_config={
            "Strapping Length/m": st.column_config.NumberColumn("Strapping Length/m", required=True, min_value=0),
            "Cost (LKR/m)": st.column_config.NumberColumn("Cost (LKR/m)", required=True, min_value=0, format="%.2f")
        },
        key="pp_strapping_editor"
    )
    
    # Update session state
    st.session_state.pp_strapping_costs = edited_pp_strapping_df
    
    st.divider()
    
    # Calculation table for Total crate/pallet cost
    st.markdown("**Total Crate/Pallet Cost Calculation**")
    
    if not edited_sku_df_tab2.empty and not st.session_state.crate_pallet_data.empty:
        # Get data for calculations
        crate_data = st.session_state.crate_costs.iloc[0]
        pallet_data = st.session_state.pallet_costs.iloc[0]
        strapping_clip_data = st.session_state.strapping_clip_costs.iloc[0]
        pp_strapping_data = st.session_state.pp_strapping_costs.iloc[0]
        
        # Prepare calculations data
        crate_pallet_calculations_data = []
        
        # Create a dictionary to map SKU to its dimensions from SKU table
        sku_dimensions = {}
        for _, sku in edited_sku_df_tab2.iterrows():
            try:
                sku_dimensions[sku["SKU No"]] = {
                    "width": float(sku["Width/mm"]),
                    "height": float(sku["Height/mm"]),
                    "length": float(sku["Length/mm"])
                }
            except (ValueError, TypeError):
                continue
        
        # Process each entry in crate/pallet data
        for _, crate_pallet_row in st.session_state.crate_pallet_data.iterrows():
            try:
                sku_no = crate_pallet_row["SKU"]
                packing_method = crate_pallet_row["packing method"]
                crate_pallet_width = float(crate_pallet_row["Width/mm"])
                crate_pallet_height = float(crate_pallet_row["Height/mm"])
                crate_pallet_length = float(crate_pallet_row["Length/mm"])
                
                # Get SKU dimensions
                if sku_no not in sku_dimensions:
                    continue
                    
                profile_width = sku_dimensions[sku_no]["width"]
                profile_height = sku_dimensions[sku_no]["height"]
                profile_length = sku_dimensions[sku_no]["length"]
                
                # Calculate profiles per pallet/crate
                profiles_per_crate_pallet = 0
                if profile_width > 0 and profile_height > 0:
                    profiles_per_crate_pallet = (crate_pallet_width / profile_width) * (crate_pallet_height / profile_height)
                
                # Calculate crate/pallet cost(LKR)
                crate_pallet_cost = 0
                if packing_method == "pallet":
                    # (((Crate/Pallet Dimensions Table width*height*length) / (Table 2: Pallet Cost width*height*length)) * Table 2: Pallet Cost cost)
                    crate_pallet_volume = crate_pallet_width * crate_pallet_height * crate_pallet_length
                    pallet_ref_volume = pallet_data["Pallet width/mm"] * pallet_data["Pallet Height/mm"] * crate_pallet_length
                    
                    if pallet_ref_volume > 0:
                        crate_pallet_cost = (crate_pallet_volume / pallet_ref_volume) * pallet_data["Cost (LKR)"]
                
                elif packing_method == "crate":
                    # (((Crate/Pallet Dimensions Table width*height*length) / (Table 1: Crate Cost width*height*length)) * Table 1: Crate Cost cost)
                    crate_pallet_volume = crate_pallet_width * crate_pallet_height * crate_pallet_length
                    crate_ref_volume = crate_data["Crate width/mm"] * crate_data["Crate Height/mm"] * crate_data["Crate Length/mm"]
                    
                    if crate_ref_volume > 0:
                        crate_pallet_cost = (crate_pallet_volume / crate_ref_volume) * crate_data["Cost (LKR)"]
                        
                
                # Calculate packing cost per profile(LKR/prof)
                # Formula: crate_pallet_cost / profiles per pallet/crate
                packing_cost_per_profile = 0
                if profiles_per_crate_pallet > 0:
                    packing_cost_per_profile = crate_pallet_cost / profiles_per_crate_pallet
                
                # Calculate Number of strapping clips
                number_of_strapping_clips = 0
                if crate_pallet_length > 0:
                    number_of_strapping_clips = np.ceil(crate_pallet_length / 500)
                
                # Calculate strapping clip cost per profile
                strapping_clip_cost_per_profile = 0
                if profiles_per_crate_pallet > 0:
                    total_clip_cost = number_of_strapping_clips * strapping_clip_data["Cost"]
                    strapping_clip_cost_per_profile = total_clip_cost / profiles_per_crate_pallet
                
                # Calculate PP strapping cost per profile
                # Formula: ((number of strapping clips * 2) * (crate/pallet width + height)) / profiles per pallet/crate
                pp_strapping_cost_per_profile = 0
                if profiles_per_crate_pallet > 0:
                    pp_strapping_cost_per_profile = ((number_of_strapping_clips * 2) * (crate_pallet_width + crate_pallet_height)) / profiles_per_crate_pallet
                
                # PP strapping cost (for display, not used in calculation)
                pp_strapping_cost = pp_strapping_cost_per_profile * profiles_per_crate_pallet
                
                # Calculate Total cost
                total_cost = packing_cost_per_profile + strapping_clip_cost_per_profile + pp_strapping_cost_per_profile
                
                # Add to calculations data
                crate_pallet_calculations_data.append({
                    "SKU": sku_no,
                    "Packing method": packing_method,
                    "profiles per pallet/crate": round(profiles_per_crate_pallet, 2),
                    "crate/pallet cost(LKR)": round(crate_pallet_cost, 2),
                    "packing cost per profile(LKR/prof)": round(packing_cost_per_profile, 4),
                    "Number of strapping clips": int(number_of_strapping_clips),
                    "strapping clip cost per profile": round(strapping_clip_cost_per_profile, 4),
                    "PP strapping cost": round(pp_strapping_cost, 4),
                    "PP strapping cost per profile": round(pp_strapping_cost_per_profile, 4),
                    "Total cost": round(total_cost, 4)
                })
                
            except (ValueError, TypeError, ZeroDivisionError) as e:
                continue
        
        if crate_pallet_calculations_data:
            crate_pallet_calculations_df = pd.DataFrame(crate_pallet_calculations_data)
            st.dataframe(crate_pallet_calculations_df, use_container_width=True)
            
            # Calculate and display total summary
            total_cost_all = sum(item["Total cost"] for item in crate_pallet_calculations_data)
            st.metric("**Total Crate/Pallet Cost (All SKUs)**", f"LKR {total_cost_all:,.4f}")
        else:
            st.warning("Unable to calculate crate/pallet costs. Please check all input data is valid.")
    else:
        st.info("Enter SKU data and crate/pallet dimensions to see crate/pallet cost calculations.")

    st.divider()
    
    # New Section: Special Comments under Secondary Packing
    st.subheader("Special Comments under Secondary Packing")
    
    # Determine protective tape comment based on finish selection
    protective_tape_comment = ""
    if finish_tab2 in ["PC", "WF", "Anodised"]:
        protective_tape_comment = "Protective tape required to avoid rejects"
    else:
        protective_tape_comment = "Protective tape is not mandatory"
    
    # Create the comments box
    comments_box = f"""
    **Packing Method Note:**
    
    1. Costing is done according to Secondary packing.
    
    2. The interleaving material is **"{eco_friendly_tab2}"**.
    
    3. {protective_tape_comment}
    
    4. Costing is inclusive of secondary packing - pallet or crate, however it is not inclusive of any labels or artwork. These will incur an additional charge.
    """
    
    st.info(comments_box)


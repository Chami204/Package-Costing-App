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

# Create download button
def create_excel_report():
    """Create Excel report with primary and secondary calculations"""
    from io import BytesIO
    from openpyxl import Workbook
    from openpyxl.styles import Border, Side, Alignment, Font, PatternFill
    from openpyxl.utils.dataframe import dataframe_to_rows
    
    # Create an Excel writer
    output = BytesIO()
    
    # Create border style
    thin_border = Border(
        left=Side(style='thin'),
        right=Side(style='thin'),
        top=Side(style='thin'),
        bottom=Side(style='thin')
    )
    
    # Create heading style
    heading_font = Font(name='Calibri', size=12, bold=True, color='FFFFFF')
    heading_fill = PatternFill(start_color='4B0082', end_color='4B0082', fill_type='solid')  # Dark purple
    
    with pd.ExcelWriter(output, engine='openpyxl') as writer:
        workbook = writer.book
        
        # Sheet 1: Primary Calculations
        if 'primary_calculations' in st.session_state and not st.session_state.primary_calculations.empty:
            # Get primary selections from session state
            finish_primary = st.session_state.get("finish_primary", "Mill Finish")
            interleaving_primary = st.session_state.get("interleaving_primary", "No")
            eco_friendly_primary = st.session_state.get("eco_friendly_primary", "Mac foam")
            protective_tape_primary = st.session_state.get("protective_tape_primary", "No")
            
            # Create a summary dataframe for primary calculations
            primary_summary = pd.DataFrame({
                'Primary Calculations Summary': ['Primary Packing Costing Report']
            })
            primary_summary.to_excel(writer, sheet_name='Primary Calculations', index=False, startrow=0)
            
            # Format the primary summary
            ws = writer.sheets['Primary Calculations']
            ws['A1'].font = heading_font
            ws['A1'].fill = heading_fill
            ws['A1'].alignment = Alignment(horizontal='center')
            ws.column_dimensions['A'].width = 35
            
            # Add SKU Table
            start_row = 4
            ws.cell(row=start_row, column=1, value="SKU Table with dimensions").font = heading_font
            ws.cell(row=start_row, column=1).fill = heading_fill
            st.session_state.primary_sku_data.to_excel(writer, sheet_name='Primary Calculations', index=False, startrow=start_row + 1)
            
            # Apply borders to SKU table
            sku_data_rows = len(st.session_state.primary_sku_data)
            sku_data_cols = len(st.session_state.primary_sku_data.columns)
            for row in range(start_row + 2, start_row + sku_data_rows + 3):
                for col in range(1, sku_data_cols + 1):
                    cell = ws.cell(row=row, column=col)
                    cell.border = thin_border
            
            # Add Common Packing Selections heading
            common_start_row = start_row + sku_data_rows + 5
            ws.cell(row=common_start_row, column=1, value="Common Packing Selections").font = heading_font
            ws.cell(row=common_start_row, column=1).fill = heading_fill
            
            # Add Common Packing Selections details
            ws.cell(row=common_start_row + 1, column=1, value=f'Finish: {finish_primary}')
            ws.cell(row=common_start_row + 2, column=1, value=f'Interleaving Required: {interleaving_primary}')
            ws.cell(row=common_start_row + 3, column=1, value=f'Eco-Friendly Material: {eco_friendly_primary}')
            ws.cell(row=common_start_row + 4, column=1, value=f'Protective Tape: {protective_tape_primary}')
            
            # Apply borders to common selections
            for row in range(common_start_row + 1, common_start_row + 5):
                cell = ws.cell(row=row, column=1)
                cell.border = thin_border
            
            # Add Material Costs heading
            material_start_row = common_start_row + 6
            ws.cell(row=material_start_row, column=1, value="Table 1: Primary Packing Material Costs").font = heading_font
            ws.cell(row=material_start_row, column=1).fill = heading_fill
            
            # Add Material Costs
            st.session_state.primary_material_costs.to_excel(writer, sheet_name='Primary Calculations', index=False, 
                                   startrow=material_start_row + 1)
            
            # Apply borders to material costs table
            material_rows = len(st.session_state.primary_material_costs)
            material_cols = len(st.session_state.primary_material_costs.columns)
            for row in range(material_start_row + 2, material_start_row + material_rows + 3):
                for col in range(1, material_cols + 1):
                    cell = ws.cell(row=row, column=col)
                    cell.border = thin_border
            
            # Add Cardboard Box Cost heading
            box_start_row = material_start_row + material_rows + 4
            ws.cell(row=box_start_row, column=1, value="Table 2: Cardboard Box Cost").font = heading_font
            ws.cell(row=box_start_row, column=1).fill = heading_fill
            
            # Add Cardboard Box Costs
            st.session_state.primary_box_costs.to_excel(writer, sheet_name='Primary Calculations', index=False,
                              startrow=box_start_row + 1)
            
            # Apply borders to box costs table
            box_rows = len(st.session_state.primary_box_costs)
            box_cols = len(st.session_state.primary_box_costs.columns)
            for row in range(box_start_row + 2, box_start_row + box_rows + 3):
                for col in range(1, box_cols + 1):
                    cell = ws.cell(row=row, column=col)
                    cell.border = thin_border
            
            # Add Primary Packing Total Cost heading
            calc_start_row = box_start_row + box_rows + 4
            ws.cell(row=calc_start_row, column=1, value="Table 3: Primary Packing Total Cost").font = heading_font
            ws.cell(row=calc_start_row, column=1).fill = heading_fill
            
            # Add Primary Packing Total Cost
            st.session_state.primary_calculations.to_excel(writer, sheet_name='Primary Calculations', index=False,
                                                    startrow=calc_start_row + 1)
            
            # Apply borders to calculations table
            calc_rows = len(st.session_state.primary_calculations)
            calc_cols = len(st.session_state.primary_calculations.columns)
            for row in range(calc_start_row + 2, calc_start_row + calc_rows + 3):
                for col in range(1, calc_cols + 1):
                    cell = ws.cell(row=row, column=col)
                    cell.border = thin_border
        
        # Sheet 2: Secondary Calculations
        if 'secondary_calculations' in st.session_state and not st.session_state.secondary_calculations.empty:
            # Get secondary selections from session state
            finish_secondary = st.session_state.get("finish_secondary", "Mill Finish")
            interleaving_secondary = st.session_state.get("interleaving_secondary", "No")
            eco_friendly_secondary = st.session_state.get("eco_friendly_secondary", "Mac foam")
            protective_tape_secondary = st.session_state.get("protective_tape_secondary", "No")
            
            # Create a summary dataframe for secondary calculations
            secondary_summary = pd.DataFrame({
                'Secondary Calculations Summary': ['Secondary Packing Costing Report']
            })
            secondary_summary.to_excel(writer, sheet_name='Secondary Calculations', index=False, startrow=0)
            
            # Format the secondary summary
            ws2 = writer.sheets['Secondary Calculations']
            ws2['A1'].font = heading_font
            ws2['A1'].fill = heading_fill
            ws2['A1'].alignment = Alignment(horizontal='center')
            ws2.column_dimensions['A'].width = 35
            
            # Add SKU Table heading
            start_row_sec = 4
            ws2.cell(row=start_row_sec, column=1, value="SKU Table with dimensions").font = heading_font
            ws2.cell(row=start_row_sec, column=1).fill = heading_fill
            
            # Add SKU Table
            st.session_state.secondary_sku_data.to_excel(writer, sheet_name='Secondary Calculations', index=False, startrow=start_row_sec + 1)
            
            # Apply borders to SKU table
            sku_data_rows_sec = len(st.session_state.secondary_sku_data)
            sku_data_cols_sec = len(st.session_state.secondary_sku_data.columns)
            for row in range(start_row_sec + 2, start_row_sec + sku_data_rows_sec + 3):
                for col in range(1, sku_data_cols_sec + 1):
                    cell = ws2.cell(row=row, column=col)
                    cell.border = thin_border
            
            # Add Common Packing Selections heading
            common_start_row_sec = start_row_sec + sku_data_rows_sec + 5
            ws2.cell(row=common_start_row_sec, column=1, value="Common Packing Selections").font = heading_font
            ws2.cell(row=common_start_row_sec, column=1).fill = heading_fill
            
            # Add Common Packing Selections details
            ws2.cell(row=common_start_row_sec + 1, column=1, value=f'Finish: {finish_secondary}')
            ws2.cell(row=common_start_row_sec + 2, column=1, value=f'Interleaving Required: {interleaving_secondary}')
            ws2.cell(row=common_start_row_sec + 3, column=1, value=f'Eco-Friendly Material: {eco_friendly_secondary}')
            ws2.cell(row=common_start_row_sec + 4, column=1, value=f'Protective Tape: {protective_tape_secondary}')
            
            # Apply borders to common selections
            for row in range(common_start_row_sec + 1, common_start_row_sec + 5):
                cell = ws2.cell(row=row, column=1)
                cell.border = thin_border
            
            # Add Bundling Data if available
            current_row = common_start_row_sec + 6
            if 'bundling_data' in st.session_state and not st.session_state.bundling_data.empty:
                ws2.cell(row=current_row, column=1, value="Section 1 - Number of layers (Method 1)").font = heading_font
                ws2.cell(row=current_row, column=1).fill = heading_fill
                
                st.session_state.bundling_data.to_excel(writer, sheet_name='Secondary Calculations', index=False,
                                                       startrow=current_row + 1, 
                                                       header=True)
                
                # Apply borders to bundling data
                bundling_rows = len(st.session_state.bundling_data)
                bundling_cols = len(st.session_state.bundling_data.columns)
                for row in range(current_row + 2, current_row + bundling_rows + 3):
                    for col in range(1, bundling_cols + 1):
                        cell = ws2.cell(row=row, column=col)
                        cell.border = thin_border
                
                current_row += bundling_rows + 5
            
            # Add Bundle Size Data if available
            if 'bundle_size_data' in st.session_state and not st.session_state.bundle_size_data.empty:
                ws2.cell(row=current_row, column=1, value="Section 2 - Size of bundle (Method 2)").font = heading_font
                ws2.cell(row=current_row, column=1).fill = heading_fill
                
                st.session_state.bundle_size_data.to_excel(writer, sheet_name='Secondary Calculations', index=False,
                                                          startrow=current_row + 1,
                                                          header=True)
                
                # Apply borders to bundle size data
                bundle_size_rows = len(st.session_state.bundle_size_data)
                bundle_size_cols = len(st.session_state.bundle_size_data.columns)
                for row in range(current_row + 2, current_row + bundle_size_rows + 3):
                    for col in range(1, bundle_size_cols + 1):
                        cell = ws2.cell(row=row, column=col)
                        cell.border = thin_border
                
                current_row += bundle_size_rows + 5
            
            # Add Cost Tables heading
            current_row += 2
            ws2.cell(row=current_row, column=1, value="Secondary Packing Cost Tables").font = heading_font
            ws2.cell(row=current_row, column=1).fill = heading_fill
            current_row += 2
            
            # Add Material Costs
            if 'secondary_material_costs' in st.session_state and not st.session_state.secondary_material_costs.empty:
                ws2.cell(row=current_row, column=1, value="Table 1: Primary Packing Material Costs").font = heading_font
                ws2.cell(row=current_row, column=1).fill = heading_fill
                
                st.session_state.secondary_material_costs.to_excel(writer, sheet_name='Secondary Calculations', index=False,
                                                       startrow=current_row + 1)
                
                # Apply borders
                mat_rows = len(st.session_state.secondary_material_costs)
                mat_cols = len(st.session_state.secondary_material_costs.columns)
                for row in range(current_row + 2, current_row + mat_rows + 3):
                    for col in range(1, mat_cols + 1):
                        cell = ws2.cell(row=row, column=col)
                        cell.border = thin_border
                
                current_row += mat_rows + 5
            
            # Add Box Costs
            if 'secondary_box_costs' in st.session_state and not st.session_state.secondary_box_costs.empty:
                ws2.cell(row=current_row, column=1, value="Table 2: Cardboard Box Cost").font = heading_font
                ws2.cell(row=current_row, column=1).fill = heading_fill
                
                st.session_state.secondary_box_costs.to_excel(writer, sheet_name='Secondary Calculations', index=False,
                                                       startrow=current_row + 1)
                
                # Apply borders
                box_rows_sec = len(st.session_state.secondary_box_costs)
                box_cols_sec = len(st.session_state.secondary_box_costs.columns)
                for row in range(current_row + 2, current_row + box_rows_sec + 3):
                    for col in range(1, box_cols_sec + 1):
                        cell = ws2.cell(row=row, column=col)
                        cell.border = thin_border
                
                current_row += box_rows_sec + 5
            
            # Add Polybag Costs
            if 'polybag_costs' in st.session_state and not st.session_state.polybag_costs.empty:
                ws2.cell(row=current_row, column=1, value="Table 3: Polybag Cost").font = heading_font
                ws2.cell(row=current_row, column=1).fill = heading_fill
                
                st.session_state.polybag_costs.to_excel(writer, sheet_name='Secondary Calculations', index=False,
                                                       startrow=current_row + 1)
                
                # Apply borders
                polybag_rows = len(st.session_state.polybag_costs)
                polybag_cols = len(st.session_state.polybag_costs.columns)
                for row in range(current_row + 2, current_row + polybag_rows + 3):
                    for col in range(1, polybag_cols + 1):
                        cell = ws2.cell(row=row, column=col)
                        cell.border = thin_border
                
                current_row += polybag_rows + 5
            
            # Add Stretchwrap Costs
            if 'stretchwrap_costs' in st.session_state and not st.session_state.stretchwrap_costs.empty:
                ws2.cell(row=current_row, column=1, value="Table 4: Stretch wrap cost").font = heading_font
                ws2.cell(row=current_row, column=1).fill = heading_fill
                
                st.session_state.stretchwrap_costs.to_excel(writer, sheet_name='Secondary Calculations', index=False,
                                                       startrow=current_row + 1)
                
                # Apply borders
                stretch_rows = len(st.session_state.stretchwrap_costs)
                stretch_cols = len(st.session_state.stretchwrap_costs.columns)
                for row in range(current_row + 2, current_row + stretch_rows + 3):
                    for col in range(1, stretch_cols + 1):
                        cell = ws2.cell(row=row, column=col)
                        cell.border = thin_border
                
                current_row += stretch_rows + 5
            
            # Add Crate/Pallet Cost Tables
            current_row += 2
            ws2.cell(row=current_row, column=1, value="Crate/Pallet Cost Tables").font = heading_font
            ws2.cell(row=current_row, column=1).fill = heading_fill
            current_row += 2
            
            # Add Crate Costs
            if 'crate_costs' in st.session_state and not st.session_state.crate_costs.empty:
                ws2.cell(row=current_row, column=1, value="Table 1: Crate Cost").font = heading_font
                ws2.cell(row=current_row, column=1).fill = heading_fill
                
                st.session_state.crate_costs.to_excel(writer, sheet_name='Secondary Calculations', index=False,
                                                     startrow=current_row + 1)
                
                # Apply borders
                crate_rows = len(st.session_state.crate_costs)
                crate_cols = len(st.session_state.crate_costs.columns)
                for row in range(current_row + 2, current_row + crate_rows + 3):
                    for col in range(1, crate_cols + 1):
                        cell = ws2.cell(row=row, column=col)
                        cell.border = thin_border
                
                current_row += crate_rows + 5
            
            # Add Pallet Costs
            if 'pallet_costs' in st.session_state and not st.session_state.pallet_costs.empty:
                ws2.cell(row=current_row, column=1, value="Table 2: Pallet Cost").font = heading_font
                ws2.cell(row=current_row, column=1).fill = heading_fill
                
                st.session_state.pallet_costs.to_excel(writer, sheet_name='Secondary Calculations', index=False,
                                                     startrow=current_row + 1)
                
                # Apply borders
                pallet_rows = len(st.session_state.pallet_costs)
                pallet_cols = len(st.session_state.pallet_costs.columns)
                for row in range(current_row + 2, current_row + pallet_rows + 3):
                    for col in range(1, pallet_cols + 1):
                        cell = ws2.cell(row=row, column=col)
                        cell.border = thin_border
                
                current_row += pallet_rows + 5
            
            # Add Strapping Clip Costs
            if 'strapping_clip_costs' in st.session_state and not st.session_state.strapping_clip_costs.empty:
                ws2.cell(row=current_row, column=1, value="Table 3: Strapping Clip Cost").font = heading_font
                ws2.cell(row=current_row, column=1).fill = heading_fill
                
                st.session_state.strapping_clip_costs.to_excel(writer, sheet_name='Secondary Calculations', index=False,
                                                             startrow=current_row + 1)
                
                # Apply borders
                clip_rows = len(st.session_state.strapping_clip_costs)
                clip_cols = len(st.session_state.strapping_clip_costs.columns)
                for row in range(current_row + 2, current_row + clip_rows + 3):
                    for col in range(1, clip_cols + 1):
                        cell = ws2.cell(row=row, column=col)
                        cell.border = thin_border
                
                current_row += clip_rows + 5
            
            # Add PP Strapping Costs
            if 'pp_strapping_costs' in st.session_state and not st.session_state.pp_strapping_costs.empty:
                ws2.cell(row=current_row, column=1, value="Table 4: PP Strapping Cost").font = heading_font
                ws2.cell(row=current_row, column=1).fill = heading_fill
                
                st.session_state.pp_strapping_costs.to_excel(writer, sheet_name='Secondary Calculations', index=False,
                                                           startrow=current_row + 1)
                
                # Apply borders
                pp_rows = len(st.session_state.pp_strapping_costs)
                pp_cols = len(st.session_state.pp_strapping_costs.columns)
                for row in range(current_row + 2, current_row + pp_rows + 3):
                    for col in range(1, pp_cols + 1):
                        cell = ws2.cell(row=row, column=col)
                        cell.border = thin_border
                
                current_row += pp_rows + 5
            
            # Add Secondary Packing Cost Per Profile heading
            current_row += 2
            ws2.cell(row=current_row, column=1, value="Secondary Packing Cost Per Profile").font = heading_font
            ws2.cell(row=current_row, column=1).fill = heading_fill
            
            # Add Secondary Packing Cost Per Profile
            st.session_state.secondary_calculations.to_excel(writer, sheet_name='Secondary Calculations', index=False,
                                                  startrow=current_row + 2)
            
            # Apply borders to calculations table
            sec_calc_rows = len(st.session_state.secondary_calculations)
            sec_calc_cols = len(st.session_state.secondary_calculations.columns)
            for row in range(current_row + 3, current_row + sec_calc_rows + 4):
                for col in range(1, sec_calc_cols + 1):
                    cell = ws2.cell(row=row, column=col)
                    cell.border = thin_border
            
            # Add Crate/Pallet Dimensions if available
            current_row += sec_calc_rows + 6
            if 'crate_pallet_data' in st.session_state and not st.session_state.crate_pallet_data.empty:
                ws2.cell(row=current_row, column=1, value="Crate/Pallet Dimensions").font = heading_font
                ws2.cell(row=current_row, column=1).fill = heading_fill
                
                st.session_state.crate_pallet_data.to_excel(writer, sheet_name='Secondary Calculations', index=False,
                                                           startrow=current_row + 2)
                
                # Apply borders
                cp_dim_rows = len(st.session_state.crate_pallet_data)
                cp_dim_cols = len(st.session_state.crate_pallet_data.columns)
                for row in range(current_row + 3, current_row + cp_dim_rows + 4):
                    for col in range(1, cp_dim_cols + 1):
                        cell = ws2.cell(row=row, column=col)
                        cell.border = thin_border
                
                current_row += cp_dim_rows + 6
            
            # Add Crate/Pallet Cost Calculations if available
            if 'crate_pallet_calculations' in st.session_state and not st.session_state.crate_pallet_calculations.empty:
                ws2.cell(row=current_row, column=1, value="Crate/Pallet Cost Calculations").font = heading_font
                ws2.cell(row=current_row, column=1).fill = heading_fill
                
                st.session_state.crate_pallet_calculations.to_excel(writer, sheet_name='Secondary Calculations', index=False,
                                                     startrow=current_row + 2)
                
                # Apply borders
                cp_calc_rows = len(st.session_state.crate_pallet_calculations)
                cp_calc_cols = len(st.session_state.crate_pallet_calculations.columns)
                for row in range(current_row + 3, current_row + cp_calc_rows + 4):
                    for col in range(1, cp_calc_cols + 1):
                        cell = ws2.cell(row=row, column=col)
                        cell.border = thin_border
    
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
    
    # Function to auto-calculate all fields in SKU table
    def auto_calculate_sku_table():
        """Auto-calculate all fields in SKU table"""
        if not st.session_state.primary_sku_data.empty:
            df_copy = st.session_state.primary_sku_data.copy()
            
            for idx, row in df_copy.iterrows():
                try:
                    # Calculate total weight per profile
                    unit_weight = float(row["Unit weight(kg/m)"])
                    length_mm = float(row["Length/mm"])
                    total_weight = unit_weight * (length_mm / 1000)
                    df_copy.at[idx, "total weight per profile (kg)"] = round(total_weight, 4)
                    
                    # Get profile dimensions
                    width = float(row["Width/mm"])
                    height = float(row["Height/mm"])
                    length = float(row["Length/mm"])
                    
                    # Calculate box dimensions (round to nearest 100)
                    def round_to_nearest_100(num):
                        return round(num / 100) * 100
                    
                    # Calculate box dimensions if they're 0 or not set
                    if pd.isna(row["Box Width/mm"]) or float(row["Box Width/mm"]) == 0:
                        df_copy.at[idx, "Box Width/mm"] = round_to_nearest_100(width)
                    if pd.isna(row["Box Height/mm"]) or float(row["Box Height/mm"]) == 0:
                        df_copy.at[idx, "Box Height/mm"] = round_to_nearest_100(height)
                    if pd.isna(row["Box Length/mm"]) or float(row["Box Length/mm"]) == 0:
                        df_copy.at[idx, "Box Length/mm"] = round_to_nearest_100(length)
                    
                    # Get box dimensions
                    box_width = float(df_copy.at[idx, "Box Width/mm"])
                    box_height = float(df_copy.at[idx, "Box Height/mm"])
                    box_length = float(df_copy.at[idx, "Box Length/mm"])
                    
                    # Set default W/mm and H/mm if not set
                    if pd.isna(row["W/mm"]) or row["W/mm"] == "":
                        df_copy.at[idx, "W/mm"] = "Profiles are arranged in W direction"
                        df_copy.at[idx, "H/mm"] = "Profiles are arranged in height direction"
                    
                    # Calculate Number of profiles per box based on W/mm selection
                    w_direction = df_copy.at[idx, "W/mm"]
                    profiles_per_box = 0
                    
                    if w_direction == "Profiles are arranged in height direction":
                        # (Box Height/profile width)*(Box Width/profile Height)
                        if width > 0 and height > 0:
                            profiles_per_box = (box_height / width) * (box_width / height)
                    else:  # "Profiles are arranged in W direction"
                        # (Box Width/profile width)*(Box Height/profile Height)
                        if width > 0 and height > 0:
                            profiles_per_box = (box_width / width) * (box_height / height)
                    
                    df_copy.at[idx, "Number of profiles per box"] = round(profiles_per_box, 2) if profiles_per_box > 0 else 0
                    
                    # Update H/mm based on W/mm selection
                    if w_direction == "Profiles are arranged in W direction":
                        df_copy.at[idx, "H/mm"] = "Profiles are arranged in height direction"
                    elif w_direction == "Profiles are arranged in height direction":
                        df_copy.at[idx, "H/mm"] = "Profiles are arranged in W direction"
                        
                except (ValueError, TypeError, ZeroDivisionError):
                    df_copy.at[idx, "Box Width/mm"] = 0
                    df_copy.at[idx, "Box Height/mm"] = 0
                    df_copy.at[idx, "Box Length/mm"] = 0
                    df_copy.at[idx, "Number of profiles per box"] = 0
            
            # Update session state
            st.session_state.primary_sku_data = df_copy
            st.success("Auto-calculation completed!")
    
    # Sub topic 1 - SKU Table with dimensions with auto-calc button
    col1, col2 = st.columns([3, 1])
    with col1:
        st.subheader("SKU Table with dimensions")
    with col2:
        st.markdown("<br>", unsafe_allow_html=True)
        if st.button("🔄 Auto-Calculate All Fields", 
                    help="Click to auto-calculate total weight, box dimensions, and profiles per box",
                    use_container_width=True):
            auto_calculate_sku_table()
            st.rerun()
    
    # Initialize session state for primary SKU data with new columns
    if 'primary_sku_data' not in st.session_state:
        st.session_state.primary_sku_data = pd.DataFrame(columns=[
            "SKU No", 
            "Unit weight(kg/m)", 
            "total weight per profile (kg)", 
            "Width/mm", 
            "Height/mm", 
            "Length/mm",
            "Box Width/mm",
            "Box Height/mm", 
            "Box Length/mm",
            "W/mm",
            "H/mm",
            "Number of profiles per box",
            "Comment on fabrication"
        ])
    
    # Function to calculate box dimensions and number of profiles per box
    def calculate_box_and_profiles(df):
        """Calculate box dimensions and number of profiles per box"""
        df_copy = df.copy()
        for idx, row in df_copy.iterrows():
            try:
                # Get profile dimensions
                width = float(row["Width/mm"])
                height = float(row["Height/mm"])
                length = float(row["Length/mm"])
                
                # Calculate box dimensions (round to nearest 100)
                def round_to_nearest_100(num):
                    """Round to nearest 100"""
                    return round(num / 100) * 100
                
                # Calculate box dimensions if they're 0 or not set
                if pd.isna(row["Box Width/mm"]) or float(row["Box Width/mm"]) == 0:
                    df_copy.at[idx, "Box Width/mm"] = round_to_nearest_100(width)
                if pd.isna(row["Box Height/mm"]) or float(row["Box Height/mm"]) == 0:
                    df_copy.at[idx, "Box Height/mm"] = round_to_nearest_100(height)
                if pd.isna(row["Box Length/mm"]) or float(row["Box Length/mm"]) == 0:
                    df_copy.at[idx, "Box Length/mm"] = round_to_nearest_100(length)
                
                # Get box dimensions
                box_width = float(df_copy.at[idx, "Box Width/mm"])
                box_height = float(df_copy.at[idx, "Box Height/mm"])
                box_length = float(df_copy.at[idx, "Box Length/mm"])
                
                # Set default W/mm and H/mm if not set
                if pd.isna(row["W/mm"]) or row["W/mm"] == "":
                    df_copy.at[idx, "W/mm"] = "Profiles are arranged in W direction"
                    df_copy.at[idx, "H/mm"] = "Profiles are arranged in height direction"
                
                # Calculate Number of profiles per box based on W/mm selection
                w_direction = df_copy.at[idx, "W/mm"]
                profiles_per_box = 0
                
                if w_direction == "Profiles are arranged in height direction":
                    # (Box Height/profile width)*(Box Width/profile Height)
                    if width > 0 and height > 0:
                        profiles_per_box = (box_height / width) * (box_width / height)
                else:  # "Profiles are arranged in W direction"
                    # (Box Width/profile width)*(Box Height/profile Height)
                    if width > 0 and height > 0:
                        profiles_per_box = (box_width / width) * (box_height / height)
                
                df_copy.at[idx, "Number of profiles per box"] = round(profiles_per_box, 2) if profiles_per_box > 0 else 0
                
                # Update H/mm based on W/mm selection
                if w_direction == "Profiles are arranged in W direction":
                    df_copy.at[idx, "H/mm"] = "Profiles are arranged in height direction"
                elif w_direction == "Profiles are arranged in height direction":
                    df_copy.at[idx, "H/mm"] = "Profiles are arranged in W direction"
                    
            except (ValueError, TypeError, ZeroDivisionError):
                df_copy.at[idx, "Box Width/mm"] = 0
                df_copy.at[idx, "Box Height/mm"] = 0
                df_copy.at[idx, "Box Length/mm"] = 0
                df_copy.at[idx, "Number of profiles per box"] = 0
        
        return df_copy
    
    # Calculate initial values
    if not st.session_state.primary_sku_data.empty:
        st.session_state.primary_sku_data = calculate_box_and_profiles(st.session_state.primary_sku_data)
    
    # Create editable dataframe for SKU input
    edited_sku_df = st.data_editor(
        st.session_state.primary_sku_data,
        num_rows="dynamic",
        use_container_width=True,
        column_config={
            "SKU No": st.column_config.TextColumn("SKU No", required=True),
            "Unit weight(kg/m)": st.column_config.NumberColumn("Unit weight(kg/m)", required=True, min_value=0, format="%.4f"),
            "total weight per profile (kg)": st.column_config.NumberColumn("total weight per profile (kg)", required=True, min_value=0, format="%.4f", disabled=True),
            "Width/mm": st.column_config.NumberColumn("Width/mm", required=True, min_value=0, format="%.1f"),
            "Height/mm": st.column_config.NumberColumn("Height/mm", required=True, min_value=0, format="%.1f"),
            "Length/mm": st.column_config.NumberColumn("Length/mm", required=True, min_value=0, format="%.1f"),
            "Box Width/mm": st.column_config.NumberColumn("Box Width/mm", required=True, min_value=0, format="%d", step=100),
            "Box Height/mm": st.column_config.NumberColumn("Box Height/mm", required=True, min_value=0, format="%d", step=100),
            "Box Length/mm": st.column_config.NumberColumn("Box Length/mm", required=True, min_value=0, format="%d", step=100),
            "W/mm": st.column_config.SelectboxColumn(
                "W/mm",
                options=[
                    "Profiles are arranged in W direction", 
                    "Profiles are arranged in height direction"
                ],
                required=True
            ),
            "H/mm": st.column_config.TextColumn(
                "H/mm",
                required=True,
                disabled=True
            ),
            "Number of profiles per box": st.column_config.NumberColumn(
                "Number of profiles per box", 
                required=True, 
                min_value=0, 
                format="%.2f",
                disabled=True
            ),
            "Comment on fabrication": st.column_config.SelectboxColumn(
                "Comment on fabrication",
                options=["Fabricated", "Just Cutting"],
                required=True
            )
        },
        key="sku_editor_primary"
    )
    
    # Callback function to auto-calculate total weight
    def calculate_total_weight(df):
        """Calculate total weight per profile based on unit weight and length"""
        df_copy = df.copy()
        for idx, row in df_copy.iterrows():
            try:
                unit_weight = float(row["Unit weight(kg/m)"])
                length_mm = float(row["Length/mm"])
                # Calculate: Unit weight(kg/m) * (Length(mm) / 1000)
                total_weight = unit_weight * (length_mm / 1000)
                df_copy.at[idx, "total weight per profile (kg)"] = round(total_weight, 4)
            except (ValueError, TypeError):
                df_copy.at[idx, "total weight per profile (kg)"] = 0
        return df_copy
    
    # Update the session state with calculated weights and box dimensions
    if not edited_sku_df.equals(st.session_state.primary_sku_data):
        # Recalculate total weights
        edited_sku_df_with_weights = calculate_total_weight(edited_sku_df)
        # Recalculate box dimensions and profiles
        edited_sku_df_with_all = calculate_box_and_profiles(edited_sku_df_with_weights)
        st.session_state.primary_sku_data = edited_sku_df_with_all
        st.rerun()
    
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
            
            for _, sku in st.session_state.primary_sku_data.iterrows():
                try:
                    # Get SKU dimensions
                    width = float(sku["Width/mm"])
                    height = float(sku["Height/mm"])
                    length = float(sku["Length/mm"])
                    unit_weight = float(sku["Unit weight(kg/m)"])
                    total_weight = float(sku["total weight per profile (kg)"])
                    
                    # Get box dimensions from SKU table
                    box_width = float(sku["Box Width/mm"])
                    box_height = float(sku["Box Height/mm"])
                    box_length = float(sku["Box Length/mm"])
                    profiles_per_box = float(sku["Number of profiles per box"])
                    
                    # Calculate Surface Area in m² (using profile dimensions)
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
                    
                    # Calculate Packing Cost - UPDATED FORMULA
                    # Using box dimensions from SKU table divided by number of profiles per box
                    packing_cost = 0
                    if ref_box["Length(mm)"] > 0 and ref_box["Width (mm)"] > 0 and ref_box["Height (mm)"] > 0:
                        if profiles_per_box > 0:
                            # Calculate cost per box volume
                            box_volume_cost = (ref_box["Cost (LKR)"] / (ref_box["Width (mm)"] * ref_box["Height (mm)"] * ref_box["Length(mm)"]))
                            # Calculate actual box volume from SKU table
                            actual_box_volume = box_width * box_height * box_length
                            # Total box cost = cost per volume * actual box volume
                            total_box_cost = box_volume_cost * actual_box_volume
                            # Packing cost per profile = total box cost / number of profiles per box
                            packing_cost = total_box_cost / profiles_per_box
                        else:
                            # Fallback to original calculation if profiles_per_box is 0
                            packing_cost = (ref_box["Cost (LKR)"] / (ref_box["Width (mm)"] * ref_box["Height (mm)"] * ref_box["Length(mm)"])) * (width * height * length)
                    
                    # Calculate Total Cost
                    total_cost = interleaving_cost + protective_tape_cost + packing_cost
                    
                    calculations_data.append({
                        "SKU": sku["SKU No"],
                        "Unit weight(kg/m)": round(unit_weight, 4),
                        "Total weight (kg)": round(total_weight, 4),
                        "SA(m²)": round(sa_m2, 4),
                        "Interleaving cost": round(interleaving_cost, 2),
                        "Protective tape cost": round(protective_tape_cost, 2),
                        "Packing type": "Cardboard box",
                        "Box width/mm": round(box_width, 0),
                        "Box height/mm": round(box_height, 0),
                        "Box length/mm": round(box_length, 0),
                        "Profiles per box": round(profiles_per_box, 2),
                        "Packing Cost (LKR)": round(packing_cost, 2),
                        "Total Cost": round(total_cost, 2)
                    })
                    
                except (ValueError, TypeError, ZeroDivisionError):
                    continue
            
            if calculations_data:
                # Store calculations in session state
                st.session_state.primary_calculations = pd.DataFrame(calculations_data)
                
                # Create editable dataframe with initial calculations
                editable_df = st.session_state.primary_calculations.copy()
                
                # Create editable dataframe for calculations
                edited_calc_df = st.data_editor(
                    editable_df,
                    num_rows="fixed",
                    use_container_width=True,
                    column_config={
                        "SKU": st.column_config.TextColumn("SKU", required=True, disabled=True),
                        "Unit weight(kg/m)": st.column_config.NumberColumn("Unit weight(kg/m)", required=True, min_value=0, format="%.4f", disabled=True),
                        "Total weight (kg)": st.column_config.NumberColumn("Total weight (kg)", required=True, min_value=0, format="%.4f", disabled=True),
                        "SA(m²)": st.column_config.NumberColumn("SA(m²)", required=True, min_value=0, format="%.4f", disabled=True),
                        "Interleaving cost": st.column_config.NumberColumn("Interleaving cost", required=True, min_value=0, format="%.2f", disabled=True),
                        "Protective tape cost": st.column_config.NumberColumn("Protective tape cost", required=True, min_value=0, format="%.2f", disabled=True),
                        "Packing type": st.column_config.TextColumn("Packing type", required=True, disabled=True),
                        "Box width/mm": st.column_config.NumberColumn("Box width/mm", required=True, min_value=0, format="%.0f"),
                        "Box height/mm": st.column_config.NumberColumn("Box height/mm", required=True, min_value=0, format="%.0f"),
                        "Box length/mm": st.column_config.NumberColumn("Box length/mm", required=True, min_value=0, format="%.0f"),
                        "Profiles per box": st.column_config.NumberColumn("Profiles per box", required=True, min_value=0, format="%.2f", disabled=True),
                        "Packing Cost (LKR)": st.column_config.NumberColumn("Packing Cost (LKR)", required=True, min_value=0, format="%.2f", disabled=True),
                        "Total Cost": st.column_config.NumberColumn("Total Cost", required=True, min_value=0, format="%.2f", disabled=True)
                    },
                    key="primary_calculations_editor"
                )
                
                # Recalculate if box dimensions changed
                if not edited_calc_df.equals(st.session_state.primary_calculations):
                    # Recalculate packing costs based on new dimensions
                    ref_length = ref_box["Length(mm)"]
                    ref_width = ref_box["Width (mm)"]
                    ref_height = ref_box["Height (mm)"]
                    ref_cost = ref_box["Cost (LKR)"]
                    
                    if ref_length > 0 and ref_width > 0 and ref_height > 0:
                        cost_per_volume = ref_cost / (ref_width * ref_height * ref_length)
                    else:
                        cost_per_volume = 0
                    
                    # Update calculations
                    for idx, row in edited_calc_df.iterrows():
                        try:
                            # Get profiles per box from original SKU data
                            sku_no = row["SKU"]
                            sku_row = st.session_state.primary_sku_data[st.session_state.primary_sku_data["SKU No"] == sku_no]
                            if not sku_row.empty:
                                profiles_per_box = float(sku_row.iloc[0]["Number of profiles per box"])
                            else:
                                profiles_per_box = 1
                            
                            box_width = float(row["Box width/mm"])
                            box_height = float(row["Box height/mm"])
                            box_length = float(row["Box length/mm"])
                            
                            box_volume = box_width * box_height * box_length
                            
                            if cost_per_volume > 0 and profiles_per_box > 0:
                                new_packing_cost = (cost_per_volume * box_volume) / profiles_per_box
                            else:
                                new_packing_cost = 0
                            
                            # Get original costs
                            interleaving_cost = float(row["Interleaving cost"])
                            protective_tape_cost = float(row["Protective tape cost"])
                            
                            # Calculate new total cost
                            new_total_cost = interleaving_cost + protective_tape_cost + new_packing_cost
                            
                            # Update the row
                            edited_calc_df.at[idx, "Packing Cost (LKR)"] = round(new_packing_cost, 2)
                            edited_calc_df.at[idx, "Total Cost"] = round(new_total_cost, 2)
                            
                        except (ValueError, TypeError):
                            continue
                    
                    # Update session state
                    st.session_state.primary_calculations = edited_calc_df
                    st.rerun()
                
                # Display the updated dataframe
                st.dataframe(st.session_state.primary_calculations, use_container_width=True)
                
                # Display total summary
                total_sum = st.session_state.primary_calculations["Total Cost"].sum()
                st.metric("**Total Primary Packing Cost**", f"LKR {total_sum:,.2f}")
                
            else:
                st.warning("Enter valid SKU data")
        else:
            st.info("Enter SKU data")
        
        # Reset calculation flag after displaying
        st.session_state.calculate_primary = False
    
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

# Note: Secondary Calculations tab code remains unchanged from the original
with tab2:
    st.header("Secondary Calculations")
    st.info("Secondary calculations section would go here...")

import streamlit as st
import pandas as pd

st.set_page_config(page_title="🎯💰 Targeted Packing Costing", page_icon="🎯💰")
st.title("🎯💰 Targeted Packing Costing App")

st.header("Step 1: Packing Data Table with Dropdowns")

# Define initial DataFrame
default = {
    "Identification No.": ["ID001"],
    "W (mm)": [50.0],
    "H (mm)": [60.0],
    "L (mm)": [1000.0],
    "Finish": ["Mill Finish"],
    "Fabricated": ["Fabricated"],
    "Eco-Friendly Packing": ["Yes"],
    "Interleaving Required": ["Yes"],
    "Protective Tape - Customer Specified": ["No"],
    "Bundling": ["Yes"],
    "Crate/ Palletizing": ["Crate"]
}
df = pd.DataFrame(default)

# Configure dropdown columns
dropdowns = {
    "Finish": ["Mill Finish", "Anodized", "Powder Coated", "Wood Finished"],
    "Fabricated": ["Fabricated", "Just Cutting"],
    "Eco-Friendly Packing": ["Yes", "No"],
    "Interleaving Required": ["Yes", "No"],
    "Protective Tape - Customer Specified": ["Yes", "No"],
    "Bundling": ["Yes", "No"],
    "Crate/ Palletizing": ["Crate", "Pallet"]
}

# Render editable table with dropdowns
df_edited = st.data_editor(
    df,
    column_config={col: {"editor": "select", "options": opts} for col, opts in dropdowns.items()},
    use_container_width=True,
    num_rows="dynamic"
)

# Processing and Output
outputs = []
for _, r in df_edited.iterrows():
    W, H, L = r["W (mm)"], r["H (mm)"], r["L (mm)"]
    eco = r["Eco-Friendly Packing"]
    finish = r["Finish"]
    fab = r["Fabricated"]
    spec = r["Protective Tape - Customer Specified"]

    # Logic
    mat = "Craft Paper" if eco == "Yes" else "McFoam"
    chk = "Okay" if finish == "Mill Finish" and mat == "Craft Paper" else "Can cause rejects - go ahead with McFoam"
    area = (2 * ((W * L) + (H * L) + (W * H))) / 1e6
    rates = {"McFoam": 51, "Craft Paper": 34.65, "Protective Tape": 100.65, "Stretchwrap": 14.38}
    icost = round(area * rates[mat], 2)
    if spec == "No":
        advice = "OK" if ((fab == "Fabricated" and finish == "Mill Finish") or fab == "Just Cutting") else "Protective tape required to avoid rejects"
    else:
        advice = "Protective tape required (customer)"
    tcost = round(area * rates["Protective Tape"], 2) if spec == "Yes" or "Protective tape required" in advice else 0.0

    outputs.append({
        "Identification No.": r["Identification No."],
        "Interleaving Material": mat,
        "Check": chk,
        "Surface Area (m²)": round(area, 4),
        "Interleaving Cost (Rs)": icost,
        "Protective Tape Advice": advice,
        "Protective Tape Cost (Rs)": tcost
    })

st.markdown("### 🟩 Output Summary")
st.dataframe(
    pd.DataFrame(outputs).style.set_properties(**{"background-color": "#E6F2FF"}),
    use_container_width=True
)

# Bundle Section
bundle_out = []
st.header("Step 2: Bundle Stack Inputs & Outputs")

for i, r in df_edited.iterrows():
    if r["Bundling"] == "Yes":
        st.subheader(f"Bundle – {r['Identification No.']}")
        nr = st.number_input(f"Rows – {r['Identification No.']}", min_value=1, key=f"nr{i}")
        nl = st.number_input(f"Layers – {r['Identification No.']}", min_value=1, key=f"nl{i}")
        wt = st.selectbox(f"Width Profile – {r['Identification No.']}", ["W/mm", "H/mm"], key=f"wt{i}")
        ht = st.selectbox(f"Height Profile – {r['Identification No.']}", ["H/mm", "W/mm"], key=f"ht{i}")
        dims = {"W/mm": r["W (mm)"], "H/mm": r["H (mm)"]}

        bw = nr * dims[wt]
        bh = nl * dims[ht]
        bl = r["L (mm)"]
        cov = round(2 * ((bw * bl) + (bh * bl) + (bw * bh)) / 1e6, 4)

        bundle_out.append({
            "Identification No.": r["Identification No."],
            "Bundle Width (mm)": bw,
            "Bundle Height (mm)": bh,
            "Bundle Length (mm)": bl,
            "Area Covered (m²)": cov
        })

if bundle_out:
    st.markdown("### 🟦 Bundle Outputs")
    st.dataframe(
        pd.DataFrame(bundle_out).style.set_properties(**{"background-color": "#FFF9C4"}),
        use_container_width=True
    )

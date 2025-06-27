import streamlit as st
import pandas as pd
import networkx as nx
import matplotlib.pyplot as plt

st.set_page_config(page_title="Edwards Family Tree", layout="wide")

st.title("📜 Edwards Family Tree Explorer")
st.markdown("Upload the Excel file to generate the interactive family tree.")

uploaded_file = st.file_uploader("Upload your Excel file", type=["xlsx"])

if uploaded_file:
    # Read all sheets into a dictionary of DataFrames
    df_dict = pd.read_excel(uploaded_file, sheet_name=None)

    root_name = "Henrietta & Edmond"
    G = nx.DiGraph()
    G.add_node(root_name)

    for sheet_name, df in df_dict.items():
        if df.empty:
            continue
        parent = sheet_name.strip()
        G.add_edge(root_name, parent)

        # Loop through the names in the sheet and add as descendants
        for _, row in df.iterrows():
            for col in df.columns:
                val = str(row[col]).strip()
                if val and val.lower() not in ["nan", "none"]:
                    G.add_edge(parent, val)

    # Generate a layout (spring layout doesn't require pygraphviz)
    pos = nx.spring_layout(G, seed=42)

    plt.figure(figsize=(20, 12))
    nx.draw(
        G,
        pos,
        with_labels=True,
        arrows=False,
        node_size=3000,
        node_color="#f9f9f9",
        font_size=8,
        font_weight="bold",
        edge_color="gray"
    )
    st.pyplot(plt)

    st.markdown("---")
    st.success("✅ Tree successfully generated.")

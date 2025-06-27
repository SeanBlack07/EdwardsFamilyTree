import streamlit as st
import pandas as pd
import networkx as nx
import matplotlib.pyplot as plt
from networkx.drawing.nx_agraph import graphviz_layout
import pygraphviz as pgv
import io

# Page config
st.set_page_config(page_title="Edwards Family Tree Explorer", layout="wide")
st.title("Edwards Family Tree")

# File uploader
uploaded_file = st.file_uploader("Upload your Excel family tree (XLSX)", type=["xlsx"])

if uploaded_file:
    df_dict = pd.read_excel(uploaded_file, sheet_name=None)
    G = nx.DiGraph()

    # Build graph from each sheet (assuming each sheet is a family branch)
    for sheet_name, df in df_dict.items():
        df.fillna("", inplace=True)
        for _, row in df.iterrows():
            parent = row[0].strip()
            for val in row[1:]:
                if val and isinstance(val, str):
                    G.add_edge(parent, val.strip())

    # Sidebar filter
    all_nodes = sorted(G.nodes())
    root_filter = st.sidebar.selectbox("Select a root to filter by", options=["All"] + all_nodes)

    if root_filter != "All":
        descendants = nx.descendants(G, root_filter)
        sub_nodes = [root_filter] + list(descendants)
        subG = G.subgraph(sub_nodes).copy()
    else:
        subG = G

    # Draw the tree
    try:
        pos = graphviz_layout(subG, prog='dot')
    except Exception:
        pos = nx.spring_layout(subG, seed=42)

    fig, ax = plt.subplots(figsize=(24, 18))
    nx.draw(
        subG,
        pos,
        with_labels=True,
        node_color="#f0f9ff",
        node_size=3000,
        font_size=10,
        font_weight="bold",
        arrows=False,
        ax=ax
    )
    st.pyplot(fig)
    st.success(f"Tree rendered for {root_filter if root_filter != 'All' else 'all branches'}.")
else:
    st.info("Please upload a valid Excel file to view the family tree.")

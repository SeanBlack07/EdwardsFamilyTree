import streamlit as st
import pandas as pd
import networkx as nx
import matplotlib.pyplot as plt
from networkx.drawing.nx_pydot import graphviz_layout

# Set page configuration
st.set_page_config(page_title="Edwards Family Tree", layout="wide")
st.title("Edwards Family Tree Viewer")

# File uploader
uploaded_file = st.file_uploader("Upload the Family Tree Excel file", type=["xlsx"])

if uploaded_file:
    df_dict = pd.read_excel(uploaded_file, sheet_name=None, engine="openpyxl")
    
    # Create selection for original child branches (excluding Henrietta & Edmond)
    original_children = list(df_dict.keys())[1:]  # Skip the root tab (Henrietta & Edmond)
    selected_branch = st.sidebar.selectbox("Select a Family Branch", ["All"] + original_children)

    # Create a directed graph
    G = nx.DiGraph()
    root_name = "Henrietta & Edmond"
    G.add_node(root_name)

    def build_tree(sheet_name, df):
        parent = sheet_name
        G.add_edge(root_name, parent)
        for name in df.iloc[:, 0]:  # Assuming names are in the first column
            if pd.notna(name) and "(" not in str(name):  # Avoid adding notes as nodes
                G.add_edge(parent, name)

    if selected_branch == "All":
        for sheet_name, df in df_dict.items():
            if sheet_name != root_name:
                build_tree(sheet_name, df)
    else:
        build_tree(selected_branch, df_dict[selected_branch])

    # Generate layout
    try:
        pos = graphviz_layout(G, prog='dot')
    except Exception:
        pos = nx.spring_layout(G, k=0.7, iterations=50)

    # Draw the tree
    plt.figure(figsize=(20, 10))
    nx.draw(G, pos, with_labels=True, arrows=False, node_size=3000,
            node_color="#f2efe9", font_size=9, font_weight="bold", edge_color="#ccc")
    st.pyplot(plt)

    st.markdown("---")
    st.subheader("Add Family Notes")
    with st.expander("Click to open note fields"):
        for node in G.nodes:
            if node != root_name:
                note = st.text_area(f"Note for {node}", "")

else:
    st.info("Please upload the Edwards Family Tree Excel file.")

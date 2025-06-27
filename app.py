import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import networkx as nx
import io

st.set_page_config(page_title="Edwards Family Tree", layout="wide")
st.title("Edwards Family Tree Viewer")

uploaded_file = st.file_uploader("Upload your Edwards Family Tree Excel file", type=["xlsx"])

if uploaded_file:
    df_dict = pd.read_excel(uploaded_file, sheet_name=None)
    
    root_name = "Henrietta & Edmond"
    G = nx.DiGraph()
    G.add_node(root_name)

    family_color_map = {}

    # Process each tab (each child of Henrietta and Edmond)
    for sheet_name, df in df_dict.items():
        if df.empty or df.columns[0] not in df.columns:
            continue

        parent = sheet_name.strip()
        full_branch = df[df.columns[0]].dropna().astype(str).tolist()

        if not full_branch:
            continue

        G.add_edge(root_name, parent)

        for child in full_branch:
            G.add_edge(parent, child)
            family_color_map[child] = parent  # color-coded by parent branch

    # Sidebar filter
    selected_branch = st.sidebar.selectbox("Select a branch (original child):", ["All"] + list(df_dict.keys()))

    filtered_nodes = list(G.nodes())
    if selected_branch != "All":
        descendants = list(nx.descendants(G, selected_branch))
        filtered_nodes = [root_name, selected_branch] + descendants

    subgraph = G.subgraph(filtered_nodes)
    pos = nx.spring_layout(subgraph, seed=42)

    plt.figure(figsize=(20, 12))
    
    node_colors = []
    for node in subgraph.nodes():
        if node == root_name:
            node_colors.append("#8B0000")
        elif node in df_dict:
            node_colors.append("#FF8C00")
        else:
            parent = family_color_map.get(node, None)
            node_colors.append("#D3D3D3" if parent is None else plt.cm.tab20(hash(parent) % 20))

    nx.draw(
        subgraph,
        pos,
        with_labels=True,
        node_color=node_colors,
        node_size=2500,
        font_size=9,
        font_weight="bold",
        arrows=False,
        edge_color="#A9A9A9"
    )
    st.pyplot(plt)

    st.info("You can filter descendants by original children in the sidebar. This display uses a layout optimized for browser compatibility.")

    st.markdown("---")
    st.subheader("Family Notes")
    st.markdown("Use this space throughout the year to collect notes and memories about each family member.")

    selected_person = st.selectbox("Select a person to leave a note:", list(G.nodes())[1:])
    note = st.text_area("Your Note:")
    if st.button("Save Note"):
        st.success(f"Note saved for {selected_person} (demo only – connect to a database to store).")

else:
    st.warning("Please upload your Excel file to begin.")

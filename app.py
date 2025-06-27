import streamlit as st
import pandas as pd
import networkx as nx
import matplotlib.pyplot as plt

st.set_page_config(page_title="Edwards Family Tree", layout="wide")

st.title("🌳 Edwards Family Tree Explorer")
st.markdown("Upload the Excel file to generate the interactive family tree.")

uploaded_file = st.file_uploader("Upload your Excel file", type=["xlsx"])

if uploaded_file:
    # Read all sheets into a dictionary of DataFrames
    df_dict = pd.read_excel(uploaded_file, sheet_name=None)

    root_name = "Henrietta & Edmond"
    G = nx.DiGraph()
    G.add_node(root_name)

    original_children = []
    for sheet_name in df_dict:
        child = sheet_name.strip()
        original_children.append(child)
        G.add_edge(root_name, child)

        df = df_dict[sheet_name]
        if df.empty:
            continue

        for _, row in df.iterrows():
            parent = child
            for col in df.columns:
                val = str(row[col]).strip()
                if val and val.lower() not in ["nan", "none"]:
                    G.add_edge(parent, val)
                    parent = val  # Next child in the chain

    # Sidebar filter
    st.sidebar.title("📁 Filter Branch")
    selected_branch = st.sidebar.selectbox("Select a branch to view", ["All"] + original_children)

    # Filter the graph
    def collect_descendants(graph, start_node):
        nodes = set()
        edges = []

        def recurse(node):
            if node in nodes:
                return
            nodes.add(node)
            for child in graph.successors(node):
                edges.append((node, child))
                recurse(child)

        recurse(start_node)
        return nodes, edges

    if selected_branch == "All":
        subgraph = G
    else:
        nodes, edges = collect_descendants(G, selected_branch)
        nodes.add(root_name)
        edges.append((root_name, selected_branch))
        subgraph = G.edge_subgraph(edges).copy()
        subgraph.add_nodes_from(nodes)

    # Hierarchical layout helper
    def hierarchy_pos(G, root, width=1.0, vert_gap=0.2, vert_loc=0, xcenter=0.5, pos=None, parent=None):
        if pos is None:
            pos = {root: (xcenter, vert_loc)}
        else:
            pos[root] = (xcenter, vert_loc)
        children = list(G.successors(root))
        if not children:
            return pos
        dx = width / len(children)
        nextx = xcenter - width / 2 - dx / 2
        for child in children:
            nextx += dx
            pos = hierarchy_pos(G, child, width=dx, vert_gap=vert_gap,
                                vert_loc=vert_loc - vert_gap, xcenter=nextx, pos=pos, parent=root)
        return pos

    # Draw tree
    try:
        pos = hierarchy_pos(subgraph, root=root_name)
        plt.figure(figsize=(22, 14))
        nx.draw(
            subgraph,
            pos,
            with_labels=True,
            arrows=False,
            node_size=3000,
            node_color="#f0f8ff",
            font_size=8,
            font_weight="bold",
            edge_color="gray"
        )
        st.pyplot(plt)
        st.success("✅ Tree successfully displayed.")
    except Exception as e:
        st.error(f"❌ Error rendering tree layout: {e}")

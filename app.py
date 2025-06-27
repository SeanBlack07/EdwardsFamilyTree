import streamlit as st
import pandas as pd
import networkx as nx
import matplotlib.pyplot as plt

st.set_page_config(page_title="Edwards Family Tree", layout="wide")
st.title("🌳 Edwards Family Tree Explorer")
st.markdown("Upload the Excel file to generate the interactive family tree.")

uploaded_file = st.file_uploader("Upload your Excel file", type=["xlsx"])

if uploaded_file:
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
                    if parent != val:
                        G.add_edge(parent, val)
                        parent = val  # chain continues
                    else:
                        st.warning(f"Skipped self-reference: {val}")

    # Sidebar filter
    st.sidebar.title("📁 Filter Branch")
    selected_branch = st.sidebar.selectbox("Select a branch to view", ["All"] + original_children)

    # Filter logic
    def collect_descendants(graph, start_node, seen=None):
        if seen is None:
            seen = set()
        if start_node in seen:
            return set(), []
        seen.add(start_node)
        nodes = {start_node}
        edges = []
        for child in graph.successors(start_node):
            edges.append((start_node, child))
            child_nodes, child_edges = collect_descendants(graph, child, seen)
            nodes.update(child_nodes)
            edges.extend(child_edges)
        return nodes, edges

    if selected_branch == "All":
        subgraph = G
        layout_root = root_name
    else:
        nodes, edges = collect_descendants(G, selected_branch)
        nodes.add(root_name)
        edges.append((root_name, selected_branch))
        subgraph = G.edge_subgraph(edges).copy()
        subgraph.add_nodes_from(nodes)
        layout_root = root_name if root_name in nodes else selected_branch

    # Safe hierarchy layout
    def hierarchy_pos(G, root, width=1.0, vert_gap=0.2, vert_loc=0, xcenter=0.5, pos=None, parent=None, depth=0, max_depth=50):
        if depth > max_depth:
            return pos or {}
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
            if child not in pos:
                pos = hierarchy_pos(G, child, width=dx, vert_gap=vert_gap,
                                    vert_loc=vert_loc - vert_gap, xcenter=nextx,
                                    pos=pos, parent=root, depth=depth + 1, max_depth=max_depth)
        return pos

    # Draw graph
    try:
        pos = hierarchy_pos(subgraph, layout_root)
        if not pos:
            raise ValueError("Hierarchy layout failed, fallback triggered.")
        layout_type = "Tree layout"
    except Exception:
        pos = nx.spring_layout(subgraph, seed=42)
        layout_type = "Fallback layout"

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
    st.success(f"✅ Displayed using: {layout_type}")

import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import networkx as nx
import io

st.set_page_config(page_title="Edwards Family Tree", layout="wide")
st.title("Edwards Family Tree Viewer")

uploaded_file = st.file_uploader("Upload your Excel file", type=["xlsx"])

if uploaded_file:
    df_dict = pd.read_excel(uploaded_file, sheet_name=None)

    root_name = "Henrietta & Edmond"
    G = nx.DiGraph()
    G.add_node(root_name)

    all_people = set()
    family_map = {}

    # Extract the first sheet to determine the original children
    first_sheet = next(iter(df_dict.values()))
    original_children = []
    for i, row in first_sheet.iterrows():
        child = str(row[0]).strip()
        if pd.notna(child) and child.lower() not in ["note", "", "none"]:
            original_children.append(child)
            G.add_node(child)
            G.add_edge(root_name, child)
            family_map[child] = child  # Key for sidebar filtering

    # Process all sheets
    for sheet_name, df in df_dict.items():
        branch_name = sheet_name.strip()
        previous_person = None

        for i, row in df.iterrows():
            person = str(row[0]).strip()
            if pd.isna(person) or person.lower() in ["note", "", "none"]:
                continue

            all_people.add(person)
            if person not in G:
                G.add_node(person)
            if previous_person:
                G.add_edge(previous_person, person)
            elif branch_name in original_children:
                G.add_edge(branch_name, person)
            family_map[person] = branch_name
            previous_person = person

    st.sidebar.title("Filter")
    selected_branch = st.sidebar.selectbox("Select a branch to view", options=["All"] + original_children)

    # Filter nodes based on the selected branch
    nodes_to_display = set()
    edges_to_display = []

    if selected_branch == "All":
        nodes_to_display = set(G.nodes)
        edges_to_display = list(G.edges)
    else:
        nodes_to_display.add(root_name)
        nodes_to_display.add(selected_branch)
        for node in G.nodes:
            if family_map.get(node) == selected_branch:
                nodes_to_display.add(node)
        edges_to_display = [(u, v) for u, v in G.edges if u in nodes_to_display and v in nodes_to_display]

    subgraph = G.subgraph(nodes_to_display)

    def hierarchy_pos(G, root=None, width=1., vert_gap=0.2, vert_loc=0, xcenter=0.5, pos=None, parent=None):
        if pos is None:
            pos = {root: (xcenter, vert_loc)}
        else:
            pos[root] = (xcenter, vert_loc)
        children = list(G.successors(root))
        if len(children) != 0:
            dx = width / len(children)
            nextx = xcenter - width/2 - dx/2
            for child in children:
                nextx += dx
                pos = hierarchy_pos(G, root=child, width=dx, vert_gap=vert_gap,
                                    vert_loc=vert_loc - vert_gap, xcenter=nextx, pos=pos, parent=root)
        return pos

    pos = hierarchy_pos(subgraph, root=root_name)
    plt.figure(figsize=(20, 12))
    nx.draw(subgraph, pos, with_labels=True, node_size=3000, node_color="#d9f0f7", font_size=9, font_weight="bold", edge_color="#777")
    st.pyplot(plt.gcf())

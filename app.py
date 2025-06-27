
import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import networkx as nx
import io

st.set_page_config(page_title="Family Tree Builder", layout="wide")
st.title("📜 Edwards Family Tree Generator")

uploaded_file = st.file_uploader("Upload your Excel file", type=["xlsx"])

if uploaded_file:
    df_dict = pd.read_excel(uploaded_file, sheet_name=None)

    root_name = "Henrietta & Edmond"
    G = nx.DiGraph()
    G.add_node(root_name)

    for sheet_name, df in df_dict.items():
        # Get the tab name and assume that represents one of the children
        parent = sheet_name.strip()
        G.add_node(parent)
        G.add_edge(root_name, parent)

        for idx, row in df.iterrows():
            for val in row:
                if pd.notna(val) and isinstance(val, str):
                    val = val.strip()
                    if val and val.lower() != "nan":
                        G.add_node(val)
                        G.add_edge(parent, val)

    # Positioning the nodes using hierarchy
    pos = nx.nx_agraph.graphviz_layout(G, prog='dot')
    plt.figure(figsize=(20, 10))
    nx.draw(G, pos, with_labels=True, arrows=False, node_size=3000,
            node_color="#f9f2ec", font_size=9, font_weight="bold", edge_color="#aaaaaa")

    st.pyplot(plt)

    buf = io.BytesIO()
    plt.savefig(buf, format="png")
    st.download_button("Download Tree as Image", buf.getvalue(), "edwards_family_tree.png", "image/png")

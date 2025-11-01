import streamlit as st
import networkx as nx
from pyvis.network import Network
from engine.topic_expansion import expand_topic, get_short_description
from engine.graph_manager import GraphManager
import streamlit.components.v1 as components
import tempfile
import os
import random
import string

# -------------------------------------------------
# Session State Setup
# -------------------------------------------------
if "gm" not in st.session_state:
    st.session_state.gm = GraphManager()
if "initialized" not in st.session_state:
    st.session_state.initialized = False
if "current_topic" not in st.session_state:
    st.session_state.current_topic = None
if "current_description" not in st.session_state:
    st.session_state.current_description = ""
# (1) NEW: path of clicked topics
if "click_path" not in st.session_state:
    st.session_state.click_path = []

st.set_page_config(page_title="Themen-Spinnennetz", layout="wide")
st.title("Themen-Spinnennetz")

# -------------------------------------------------
# Online / Offline Umschalter
# -------------------------------------------------
online_mode = st.sidebar.checkbox("Online-Beschreibungen nutzen", value=True)


def make_tooltip(text: str, online: bool, max_len: int = 200) -> str:
    """Erzeugt den Tooltip-Text für einen Knoten."""
    if online:
        text = text or ""
        if len(text) > max_len:
            return text[:max_len].rstrip() + "..."
        return text
    else:
        length = min(max_len, 180)
        return "".join(random.choices(string.ascii_letters + string.digits, k=length))


# -------------------------------------------------
# 1. Startthema abfragen
# -------------------------------------------------
if not st.session_state.initialized:
    topic = st.text_input("Bitte Startthema eingeben:")
    if st.button("Starten") and topic.strip():
        desc = get_short_description(topic)
        subs = expand_topic(topic)
        st.session_state.gm.add_node(topic, subs, desc)

        st.session_state.initialized = True
        st.session_state.current_topic = topic
        st.session_state.current_description = desc

        # (2) NEW: start history with main topic
        st.session_state.click_path = [topic]

        st.rerun()

# -------------------------------------------------
# 2. Graph anzeigen
# -------------------------------------------------
else:
    g = nx.Graph()
    graph_data = st.session_state.gm.get_graph()

    for node, data in graph_data.items():
        node_desc = data.get("desc", "")
        tooltip = make_tooltip(node_desc, online_mode, max_len=200)

        g.add_node(node, title=tooltip)

        for child in data["children"]:
            if child in graph_data:
                child_desc = graph_data[child].get("desc", "")
                child_tooltip = make_tooltip(child_desc, online_mode, max_len=200)
            else:
                child_tooltip = make_tooltip("", online_mode, max_len=200)

            g.add_node(child, title=child_tooltip)
            g.add_edge(node, child)

    net = Network(height="600px", width="100%", bgcolor="#ffffff", font_color="black")
    net.from_nx(g)
    net.repulsion(node_distance=200, spring_length=150, spring_strength=0.05)

    with tempfile.NamedTemporaryFile(delete=False, suffix=".html") as tmp_file:
        net.write_html(tmp_file.name)
        tmp_file_path = tmp_file.name

    with open(tmp_file_path, "r", encoding="utf-8") as f:
        html_code = f.read()
    components.html(html_code, height=650, scrolling=True)

    # -------------------------------------------------
    # 3. Rechte Seite: aktuelles Thema + Buttons
    # -------------------------------------------------
    st.markdown("---")
    st.markdown(f"### Aktueller Aspekt: **{st.session_state.current_topic}**")
    st.markdown(st.session_state.current_description)

    current_children = st.session_state.gm.graph[st.session_state.current_topic]["children"]
    if current_children:
        cols = st.columns(len(current_children))
        for i, sub in enumerate(current_children):
            if cols[i].button(sub):
                desc = get_short_description(sub)
                subs = expand_topic(sub)
                st.session_state.gm.add_node(sub, subs, desc)

                st.session_state.current_topic = sub
                st.session_state.current_description = desc

                # (3) NEW: record the click
                st.session_state.click_path.append(sub)

                st.rerun()

    # -------------------------------------------------
    # 4. Download: Sitzungspfad als Textdatei
    # -------------------------------------------------
    st.markdown("### Sitzungsverlauf exportieren")

    # Build the text content
    lines = []
    for idx, topic_name in enumerate(st.session_state.click_path, start=1):
        node_data = st.session_state.gm.get_graph().get(topic_name, {})
        desc = node_data.get("desc", "")
        lines.append(f"{idx}. {topic_name}")
        if desc:
            lines.append(desc)
        lines.append("")  # blank line

    history_text = "\n".join(lines)

    st.download_button(
        label="⬇️ Download session_steps.txt",
        data=history_text,
        file_name="session_steps.txt",
        mime="text/plain",
    )

    # -------------------------------------------------
    # Neustart
    # -------------------------------------------------
    if st.button("Neustart"):
        st.session_state.clear()
        st.rerun()

    # Debug-Ansicht
    with st.expander("Interne Datenstruktur anzeigen"):
        for node, data in st.session_state.gm.get_graph().items():
            st.markdown(f"**{node}**: {data['desc']}")
            for child in data["children"]:
                st.markdown(f"→ {child}")

    os.remove(tmp_file_path)
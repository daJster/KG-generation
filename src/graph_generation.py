from pyvis.network import Network

def get_graph(kb):
    # create graph
    g = Network(height="100%", width="100%", bgcolor="#222222", font_color="white")
    g.barnes_hut()

    # add entities
    for e in kb.entities.items():
        g.add_node(e[0], label=e[0], color="#FFA500")

    # add relations
    for r in kb.relations:
        g.add_edge(r["head"], r["tail"], label=r["type"], color="#FFA500")
    g.save_graph("graph.html")
    return g
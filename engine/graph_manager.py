class GraphManager:
    def __init__(self):
        # {topic: {"desc": str, "children": [subtopics]}}
        self.graph = {}

    def add_node(self, parent: str, children: list[str], desc: str = ""):
        if parent not in self.graph:
            self.graph[parent] = {"desc": desc, "children": []}
        self.graph[parent]["children"].extend(children)

    def get_graph(self):
        return self.graph

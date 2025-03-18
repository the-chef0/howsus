import json
import subprocess
import io
import networkx as nx

path = "/mnt/NAS/School/TUD/SSE/requests/src/requests"

pydeps_subproc = subprocess.run(
    ["pydeps", "--show-deps", "--no-output", path],
    capture_output=True,
    text=True
)

result = json.loads(pydeps_subproc.stdout)

instabilities_sum = 0

for module, module_metrics in result.items():
    afferent_coupling = 0 # imported_by
    efferent_coupling = 0 # imports

    if 'imported_by' in module_metrics.keys():
        afferent_coupling = len(module_metrics['imported_by'])

    if 'imports' in module_metrics.keys():
        efferent_coupling = len(module_metrics['imports'])

    if not ((afferent_coupling == 0) and (efferent_coupling == 0)):
        instabilities_sum += efferent_coupling / (afferent_coupling + efferent_coupling)

avg_instability = instabilities_sum / len(result.keys())
print(f"Average instability: {avg_instability}")

pyreverse_subproc = subprocess.run(
    ["pyreverse", "--output", "puml", "--all-associated", path],
    capture_output=True,
    text=True
)

class_diagram_filename = "classes.puml"
inheritance_arrow = "--|>"
buffer = io.StringIO()

with open(class_diagram_filename, "r") as f:
    for line in f:
        if inheritance_arrow in line:
            buffer.write(line)

buffer.seek(0)
G = nx.DiGraph()

for line in buffer:
    line_split = line.split(inheritance_arrow)
    line_split = [l.strip() for l in line_split]
    G.add_edge(line_split[0], line_split[1])
buffer.close()

sink_nodes = [node for node in G.nodes if G.out_degree(node) == 0]

num_abstract_classes = len(sink_nodes)
num_concrete_classes = len(G.nodes)
avg_abstractness = num_abstract_classes / num_concrete_classes

print(f"Average abstractness: {avg_abstractness}")

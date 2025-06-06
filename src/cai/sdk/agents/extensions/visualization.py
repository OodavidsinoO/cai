from typing import Optional

import graphviz  # type: ignore

from cai.sdk.agents import Agent
from cai.sdk.agents.handoffs import Handoff
from cai.sdk.agents.tool import Tool


def get_main_graph(agent: Agent) -> str:
    """
    Generates the main graph structure in DOT format for the given agent.

    Args:
        agent (Agent): The agent for which the graph is to be generated.

    Returns:
        str: The DOT format string representing the graph.
    """
    parts = [
        """
    digraph G {
        graph [splines=true];
        node [fontname="Arial"];
        edge [penwidth=1.5];
    """
    ]
    parts.append(get_all_nodes(agent))
    parts.append(get_all_edges(agent))
    parts.append("}")
    return "".join(parts)


def get_all_nodes(agent: Agent, parent: Optional[Agent] = None) -> str:
    """
    Recursively generates the nodes for the given agent and its handoffs in DOT format.

    Args:
        agent (Agent): The agent for which the nodes are to be generated.

    Returns:
        str: The DOT format string representing the nodes.
    """
    parts = []

    # Start and end the graph
    parts.append(
        '"__start__" [label="__start__", shape=ellipse, style=filled, '
        "fillcolor=lightblue, width=0.5, height=0.3];"
        '"__end__" [label="__end__", shape=ellipse, style=filled, '
        "fillcolor=lightblue, width=0.5, height=0.3];"
    )
    # Ensure parent agent node is colored
    if not parent:
        parts.append(
            f'"{agent.name}" [label="{agent.name}", shape=box, style=filled, '
            "fillcolor=lightyellow, width=1.5, height=0.8];"
        )

    for tool in agent.tools:
        parts.append(
            f'"{tool.name}" [label="{tool.name}", shape=ellipse, style=filled, '
            f"fillcolor=lightgreen, width=0.5, height=0.3];"
        )

    for handoff in agent.handoffs:
        if isinstance(handoff, Handoff):
            parts.append(
                f'"{handoff.agent_name}" [label="{handoff.agent_name}", '
                f"shape=box, style=filled, style=rounded, "
                f"fillcolor=lightyellow, width=1.5, height=0.8];"
            )
        if isinstance(handoff, Agent):
            parts.append(
                f'"{handoff.name}" [label="{handoff.name}", '
                f"shape=box, style=filled, style=rounded, "
                f"fillcolor=lightyellow, width=1.5, height=0.8];"
            )
            parts.append(get_all_nodes(handoff))

    return "".join(parts)


def get_all_edges(agent: Agent, parent: Optional[Agent] = None) -> str:
    """
    Recursively generates the edges for the given agent and its handoffs in DOT format.

    Args:
        agent (Agent): The agent for which the edges are to be generated.
        parent (Agent, optional): The parent agent. Defaults to None.

    Returns:
        str: The DOT format string representing the edges.
    """
    parts = []

    if not parent:
        parts.append(f'"__start__" -> "{agent.name}";')

    for tool in agent.tools:
        parts.append(f"""
        "{agent.name}" -> "{tool.name}" [style=dotted, penwidth=1.5];
        "{tool.name}" -> "{agent.name}" [style=dotted, penwidth=1.5];""")

    for handoff in agent.handoffs:
        if isinstance(handoff, Handoff):
            parts.append(f"""
            "{agent.name}" -> "{handoff.agent_name}";""")
        if isinstance(handoff, Agent):
            parts.append(f"""
            "{agent.name}" -> "{handoff.name}";""")
            parts.append(get_all_edges(handoff, agent))

    if not agent.handoffs and not isinstance(agent, Tool):  # type: ignore
        parts.append(f'"{agent.name}" -> "__end__";')

    return "".join(parts)


def draw_graph(agent: Agent, filename: Optional[str] = None) -> graphviz.Source:
    """
    Draws the graph for the given agent and optionally saves it as a PNG file.

    Args:
        agent (Agent): The agent for which the graph is to be drawn.
        filename (str): The name of the file to save the graph as a PNG.

    Returns:
        graphviz.Source: The graphviz Source object representing the graph.
    """
    dot_code = get_main_graph(agent)
    graph = graphviz.Source(dot_code)

    if filename:
        graph.render(filename, format="png")

    return graph

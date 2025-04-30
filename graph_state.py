from langgraph.graph import StateGraph, END
from typing import TypedDict, Optional, Annotated
import operator
from agents import (
    idle_resource_detector_agent,
    human_feedback_agent,
    resource_deletion_agent
)

class AWSState(TypedDict):
    user_request: Optional[str]
    aws_access_key: Optional[str]
    aws_secret_key: Optional[str]
    aws_region: Optional[str]
    report: Annotated[Optional[str], operator.add]
    user_feedback: Optional[str]
    detected_resources: Optional[list]
    final_message: Optional[str]

def router(state: AWSState):
    request = state["user_request"].lower()
    if "idle" in request:
        return {"__next__": "idle_detector"}
    else:
        return {"__next__": END}

def build_graph():
    graph = StateGraph(AWSState)
    graph.add_node("router", router)
    graph.add_node("idle_detector", idle_resource_detector_agent)
    graph.add_node("human_feedback", human_feedback_agent)
    graph.add_node("resource_deletion", resource_deletion_agent)

    graph.set_entry_point("router")
    graph.add_edge("router", "idle_detector")
    graph.add_edge("idle_detector", "human_feedback")
    graph.add_conditional_edges("human_feedback", lambda x: "resource_deletion" if x.get("user_feedback") == "yes" else END)
    graph.add_edge("resource_deletion", END)

    return graph.compile()

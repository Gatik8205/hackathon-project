"""
Fraud Network Graph Intelligence service.
Place at: app/services/graph_service.py

Builds a graph linking fraud reports via shared phone numbers, device IDs,
bank accounts, and UPI IDs, then detects connected clusters as suspected
fraud rings. Uses in-memory networkx graph for hackathon simplicity —
swap for a persistent store (Neo4j) later if needed.
"""

import networkx as nx
import uuid
from datetime import datetime, timezone
from typing import List, Optional
from app.models.schemas import (
    FraudReportIngest,
    FraudNetworkResponse,
    GraphNode,
    GraphEdge,
)

# In-memory graph — resets on restart. Fine for demo; replace with DB-backed
# storage for production.
_graph = nx.Graph()
_auto_report_counter = 0


def ingest_report(report: FraudReportIngest) -> None:
    report_node = f"report:{report.report_id}"
    _graph.add_node(report_node, type="report", label=f"Report {report.report_id}")

    identifiers = {
        "phone": report.phone_number,
        "device": report.device_id,
        "account": report.bank_account,
        "upi": report.upi_id,
    }

    for id_type, value in identifiers.items():
        if value:
            node_id = f"{id_type}:{value}"
            _graph.add_node(node_id, type=id_type, label=value)
            _graph.add_edge(report_node, node_id, relation=f"has_{id_type}")


def ingest_batch(reports: List[FraudReportIngest]) -> None:
    for r in reports:
        ingest_report(r)


def auto_ingest_from_detection(
    phone_number: Optional[str],
    source: str,
    scam_type: Optional[str] = None,
    complaint_text: Optional[str] = None,
) -> Optional[str]:
    """
    Auto-generates and ingests a fraud report from a live detection event
    (Citizen Fraud Shield or Scam Session Detector), keyed on phone number.

    Only called when a request is classified as a likely/possible scam AND
    a phone number was provided — this is what connects the standalone
    detection tools into the fraud network graph in real time.

    Returns the generated report_id, or None if no phone number was given
    (nothing to link on, so we skip ingestion rather than creating an
    orphaned node).
    """
    global _auto_report_counter

    if not phone_number:
        return None

    _auto_report_counter += 1
    report_id = f"AUTO{_auto_report_counter:03d}"

    report = FraudReportIngest(
        report_id=report_id,
        phone_number=phone_number,
        complaint_text=complaint_text or f"Auto-detected via {source}" + (f" ({scam_type})" if scam_type else ""),
        date=datetime.now(timezone.utc).isoformat(),
    )
    ingest_report(report)
    return report_id


def get_network() -> FraudNetworkResponse:
    nodes = [
        GraphNode(id=n, type=data.get("type", "unknown"), label=data.get("label", n))
        for n, data in _graph.nodes(data=True)
    ]
    edges = [
        GraphEdge(source=u, target=v, relation=data.get("relation", "linked"))
        for u, v, data in _graph.edges(data=True)
    ]

    # Connected components with more than one report node = suspected shared
    # infrastructure fraud ring (e.g. same UPI ID used across multiple victims)
    high_risk_clusters = []
    for component in nx.connected_components(_graph):
        report_ids = [
            n.split("report:")[1] for n in component if n.startswith("report:")
        ]
        if len(report_ids) > 1:
            high_risk_clusters.append(report_ids)

    return FraudNetworkResponse(
        nodes=nodes,
        edges=edges,
        clusters_detected=nx.number_connected_components(_graph),
        high_risk_clusters=high_risk_clusters,
    )


def reset_graph() -> None:
    """Utility for demo resets between test runs."""
    global _graph
    _graph = nx.Graph()
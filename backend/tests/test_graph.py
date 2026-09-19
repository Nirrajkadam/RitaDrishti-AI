"""
Unit tests for Neo4j Knowledge Graph Connector
"""

import pytest
from backend.app.graph.knowledge_graph import Neo4jKnowledgeGraphEngine


def test_neo4j_cypher_ingestion_queries():
    kg = Neo4jKnowledgeGraphEngine()
    queries = kg.generate_cypher_ingestion_queries(
        company_name="Acme Cloud",
        domain="acmecloud.io",
        review_data={"rating": 4.5, "sentiment": "positive", "fake_prob": 0.02}
    )
    assert len(queries) == 2
    assert "MERGE (c:Company {domain: 'acmecloud.io'})" in queries[0]
    assert "CREATE (c)-[:HAS_REVIEW]->(r)" in queries[1]


def test_neo4j_correlation_graph():
    kg = Neo4jKnowledgeGraphEngine()
    res = kg.query_entity_correlation_graph("acmecloud.io")
    assert res["target_domain"] == "acmecloud.io"
    assert "Company" in res["graph_nodes"]

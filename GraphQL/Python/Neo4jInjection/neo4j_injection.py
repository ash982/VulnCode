@staticmethod
def _create_friendship(tx, name1, name2, relationship_type):
    query = (
        "MATCH (a:Person {name: $name1}) "
        "MATCH (b:Person {name: $name2}) "
        f"CREATE (a)-[r:{relationship_type}]->(b) "  # Vulnerable!
        "RETURN type(r) AS type"
    )
    result = tx.run(query, name1=name1, name2=name2)
    return result.single()["type"]



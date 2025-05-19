@staticmethod
def _create_friendship(tx, name1, name2, relationship_type):
    # Using the APOC library's apoc.create.relationship procedure which accepts a relationship type as a parameter
    query = (
        "MATCH (a:Person {name: $name1}) "
        "MATCH (b:Person {name: $name2}) "
        "CALL apoc.create.relationship(a, $relationship_type, {}, b) "
        "YIELD rel "
        "RETURN type(rel) AS type"
    )
    result = tx.run(query, name1=name1, name2=name2, relationship_type=relationship_type)
    return result.single()["type"]

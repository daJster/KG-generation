from neo4j import GraphDatabase
 
# Define correct URI and AUTH arguments (no AUTH by default)
URI = "bolt://localhost:7687"
AUTH = ("", "")
 
with GraphDatabase.driver(URI, auth=AUTH) as client:
    # Check the connection
    client.verify_connectivity()
    
    # import the database memgraph-export.cypherl
    # client.execute_query("CALL mg.import.cypher('memgraph-export.cypher')", database_="memgraph")    
    
    # Get all the nodes
    records, summary, keys = client.execute_query(
        "MATCH (n) RETURN n.name AS name;",
        database_="memgraph",
    )
    # print(records)
    
    
    # Get all the relations with type of relation
    records, summary, keys = client.execute_query(
        "MATCH (n)-[r]->(m) RETURN n.name AS name, m.name AS hobby, type(r) AS relation;",
        database_="memgraph",
    )
    
    print(records)
    

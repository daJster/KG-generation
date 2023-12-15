from neo4j import GraphDatabase
 
# Define correct URI and AUTH arguments (no AUTH by default)
URI = "bolt://localhost:7687"
AUTH = ("", "")
 
with GraphDatabase.driver(URI, auth=AUTH) as client:
    # Check the connection
    client.verify_connectivity()
    
    # clear the database
    client.execute_query("MATCH (n) DETACH DELETE n", database_="memgraph")
    
 
    # Create a user in the database
    records, summary, keys = client.execute_query(
        "CREATE (u:User {name: $name, password: $password}) RETURN u.name AS name;",
        name="John",
        password="pass",
        database_="memgraph",
    )
    
    # Create a user in the database
    records, summary, keys = client.execute_query(
        "CREATE (u:User {name: $name, password: $password}) RETURN u.name AS name;",
        name="Felicien",
        password="pass",
        database_="memgraph",
    )
    
    # Create a hobbies type of node in the database
    records, summary, keys = client.execute_query(
        "CREATE (h:Hobbies {name: $name}) RETURN h.name AS name;",
        name="Football",
        database_="memgraph",
    )
    
    # Create a hobbies type of node in the database
    records, summary, keys = client.execute_query(
        "CREATE (h:Hobbies {name: $name}) RETURN h.name AS name;",
        name="Technology",
        database_="memgraph",
    )
    
    # create a relationship between the John and Football nodes
    records, summary, keys = client.execute_query(
        "MATCH (u:User {name: $name}) MATCH (h:Hobbies {name: $hobby}) CREATE (u)-[r:LIKES]->(h) RETURN u.name AS name, h.name AS hobby;",
        name="John",
        hobby="Football",
        database_="memgraph",
    )
    
    # create a relationship between the Felicien and Technology nodes
    
    records, summary, keys = client.execute_query(
        "MATCH (u:User {name: $name}) MATCH (h:Hobbies {name: $hobby}) CREATE (u)-[r:LIKES]->(h) RETURN u.name AS name, h.name AS hobby;",
        name="Felicien",
        hobby="Technology",
        database_="memgraph",
    )
    
    
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

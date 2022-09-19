from sqlalchemy import create_engine, text
from sqlalchemy.orm import Session


engine = create_engine("sqlite+pysqlite:///:memory:", echo=True, future=True)
with engine.connect() as conn:
    result = conn.execute(text("select 'Hello World!'"))
    print(result.all())

# commit as you go
with engine.connect() as conn:
    conn.execute(text("CREATE TABLE table_name (x int, y int)"))
    conn.execute(
        text("INSERT INTO table_name (x, y) VALUES (:x, :y)"),
        [{"x": 1, "y": 1}, {"x": 2, "y": 4}],
    )
    conn.commit()

# begin once
with engine.begin() as conn:
    conn.execute(
        text("INSERT INTO table_name (x, y) VALUES (:x, :y)"),
        [{"x": 6, "y": 8}, {"x": 9, "y": 10}]
    )

# Attribute access - Tuple Assignment
with engine.connect() as conn:
    result = conn.execute(text("SELECT x, y FROM table_name"))
    print("Tuple Assignment")
    for x, y in result:
        print(f"x: {x} \t y: {y}")

# Attribute access - Integer Index
with engine.connect() as conn:
    result = conn.execute(text("SELECT x, y FROM table_name"))
    print("Integer Index")
    for row in result:
        print(f"x: {row[0]} \t y: {row[1]}")

# Attribute access - Attribute Name
with engine.connect() as conn:
    result = conn.execute(text("SELECT x, y FROM table_name"))
    print("Attribute Name")
    for row in result:
        print(f"x: {row.x} \t y: {row.y}")

# Attribute access - Mapping Access
with engine.connect() as conn:
    result = conn.execute(text("SELECT x, y FROM table_name"))
    print("Mapping Access")
    for row in result.mappings():
        print(f"x: {row['x']} \t y: {row['y']}")

# Sending Parameters
with engine.connect() as conn:
    result = conn.execute(
        text("SELECT x, y FROM table_name WHERE y > :y"),
        {"y": 2},
    )
    for row in result:
        print(f"x: {row.x} \t y: {row.y}")

# Sending Multiple Parameters
with engine.connect() as conn:
    conn.execute(
        text("INSERT INTO table_name (x, y) VALUES (:x, :y)"),
        [{"x": 11, "y": 12}, {"x": 13, "y": 14}],
    )
    conn.commit()

# Executing with an ORM Session
stmt = text("SELECT x, y FROM table_name WHERE y > :y ORDER BY x, y")
with Session(engine) as session:
    result = session.execute(stmt, {"y": 6})
    for row in result:
        print(f"x: {row.x} \t y: {row.y}")

# commit as you go with Session
with Session(engine) as session:
    result = session.execute(
        text("UPDATE table_name SET y=:y WHERE x=:x"),
        [{"x": 9, "y":11}, {"x": 13, "y": 15}]
    )
    session.commit()

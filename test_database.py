from tools.database_tool import execute_query


print("==============================")
print("DATABASE INSERT TEST")
print("==============================")


query = """
INSERT INTO users (name, email, password)
VALUES (%s, %s, %s)
"""


parameters = (
    "Sneha",
    "sneha@example.com",
    "test123"
)


result = execute_query(
    query,
    parameters
)


print("\nInsert Result:")
print(result)
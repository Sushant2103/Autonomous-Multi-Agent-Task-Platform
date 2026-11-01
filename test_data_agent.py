from agents.data.data_agent import run_data_agent


task = {
    "task_id": 1,
    "description": "Get all users from the database"
}


print("==============================")
print("DATA AGENT TEST")
print("==============================")


result = run_data_agent(task)


print("\nData Agent Result:")
print(result)
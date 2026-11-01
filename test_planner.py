from agents.planner.planner_agent import create_plan, get_dependency_id


def test_dependency_id_parsing():
    assert get_dependency_id("task_id_1") == 1
    assert get_dependency_id("task_id_2") == 2
    assert get_dependency_id("task-3") == 3
    assert get_dependency_id("task 4") == 4
    assert get_dependency_id(5) == 5


if __name__ == "__main__":
    test_dependency_id_parsing()
    print("dependency parsing test: OK")

    test_requests = [
        "Explain Artificial Intelligence in simple words.",

        "Find the latest trends in Artificial Intelligence.",

        "Calculate 25 percent of 800.",

        "Plan a 3-day Goa trip under Rs. 15000.",

        "Compare Java and Python.",

        "Create a college event plan for 100 students."
    ]

    for request in test_requests:

        print("\n" + "=" * 60)
        print("USER REQUEST:", request)

        try:
            plan = create_plan(request)

            print("\nFINAL GENERATED PLAN:")

            for task in plan.tasks:

                print("\nTask ID:", task.task_id)
                print("Description:", task.description)
                print("Agent:", task.assigned_agent)
                print("Priority:", task.priority)
                print("Dependencies:", task.depends_on)

        except Exception as error:

            print("TEST FAILED:", error)
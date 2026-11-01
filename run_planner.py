
from agents.planner.planner_agent import create_plan


def main():

    print("\n" + "=" * 55)
    print(" AUTONOMOUS MULTI-AGENT TASK EXECUTION PLATFORM")
    print("=" * 55)

    while True:

        user_request = input(
            "\nEnter your request (or type 'exit' to stop):\n> "
        ).strip()

        if user_request.lower() in ["exit", "quit"]:
            print("\nThank you for using the platform!")
            break

        if not user_request:
            print("\nPlease enter a valid request.")
            continue

        try:

            # Send user request to Planner Agent
            plan = create_plan(user_request)

            print("\n========== GENERATED PLAN ==========")

            print("\nGoal:", plan.goal)

            for task in plan.tasks:

                print("\nTask ID:", task.task_id)
                print("Description:", task.description)
                print("Agent:", task.assigned_agent)
                print("Priority:", task.priority)
                print("Dependencies:", task.depends_on)

            print("\n====================================")
            print("Planner Agent: SUCCESS")
            print("====================================")

        except Exception as error:

            print("\nUnable to create plan.")
            print("Error:", error)


if __name__ == "__main__":
    main()
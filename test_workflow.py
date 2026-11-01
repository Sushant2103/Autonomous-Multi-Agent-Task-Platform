
from agents.planner.planner_agent import create_plan
from orchestrator.graph import build_graph


def main():

    print("\n===== AUTONOMOUS MULTI-AGENT PLATFORM =====")

    user_request = input("\nEnter your request: ").strip()

    if not user_request:
        print("Please enter a valid request.")
        return

    try:
        # Step 1: Generate a plan.
        print("\nGenerating plan...")

        plan = create_plan(user_request)

        # Convert Pydantic Plan into a dictionary if required.
        if hasattr(plan, "model_dump"):
            plan = plan.model_dump()
        elif hasattr(plan, "dict"):
            plan = plan.dict()

        # Step 2: Build the multi-agent workflow.
        app = build_graph()

        # Step 3: Prepare initial workflow state.
        initial_state = {
            "user_request": user_request,
            "plan": plan,
            "results": [],
            "status": "started",
            "final_response": "",
            "error_message": ""
        }

        # Step 4: Execute the workflow.
        print("\nStarting agent execution...")

        final_state = app.invoke(
            initial_state,
            config={"recursion_limit": 50}
        )

        # Step 5: Display the final result.
        print("\n========== FINAL OUTPUT ==========")

        if final_state.get("status") == "failed":
            print("Workflow failed.")
            print(final_state.get("error_message", "Unknown error"))

        elif final_state.get("final_response"):
            print(final_state["final_response"])

        else:
            print("Workflow finished, but no final response was generated.")

        print("\n==================================")

    except Exception as error:
        print("\nUnable to execute workflow.")
        print("Error:", error)


if __name__ == "__main__":
    main()
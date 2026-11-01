from fastapi import APIRouter

router = APIRouter()


@router.get("/")
def get_agents():

    return {
        "status": "success",

        "agents": [

            {
                "name": "Planner Agent",
                "id": "planner_agent",
                "description": "Breaks complex goals into subtasks."
            },

            {
                "name": "Research Agent",
                "id": "research_agent",
                "description": "Searches real web information."
            },

            {
                "name": "Data Agent",
                "id": "data_agent",
                "description": "Analyzes and calculates data."
            },

            {
                "name": "Execution Agent",
                "id": "execution_agent",
                "description": "Performs actions using tools."
            },

            {
                "name": "Verification Agent",
                "id": "verification_agent",
                "description": "Validates agent results."
            },

            {
                "name": "Response Agent",
                "id": "response_agent",
                "description": "Creates the final response."
            }

        ]
    }
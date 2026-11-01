import os

from dotenv import load_dotenv
from langchain_ollama import ChatOllama
from langchain_core.prompts import ChatPromptTemplate

from agents.response.response_prompt import SYSTEM_PROMPT

load_dotenv()

def _get_llm():
    return ChatOllama(
        model=os.getenv("OLLAMA_MODEL", "qwen3:4b-instruct-2507-q4_K_M"),
        base_url=os.getenv("OLLAMA_BASE_URL", "http://localhost:11434"),
        temperature=0,
        num_ctx=int(os.getenv("OLLAMA_NUM_CTX", "4096")),
        num_predict=1200,
    )


def format_agent_results(results):
    """
    Convert agent results into readable context.

    Research dictionaries are unpacked so that the
    original search findings are available to the Response Agent.
    """

    if not results:
        return "No previous agent results are available."

    formatted_results = []

    for item in results:

        task_id = item.get("task_id", "Unknown")
        agent = item.get("agent", "Unknown")
        result = item.get("result", "")

        section = [
            f"TASK ID: {task_id}",
            f"AGENT: {agent}"
        ]

        if isinstance(result, dict):

            section.append(
                f"STATUS: {result.get('status', 'Unknown')}"
            )

            # Research or Data Agent summary.
            if result.get("data"):
                section.append(
                    "\nAGENT SUMMARY:\n" + str(result["data"])
                )

            # Original research evidence.
            raw_findings = result.get("raw_findings", [])

            if raw_findings:
                section.append("\nORIGINAL RESEARCH FINDINGS:")

                for finding in raw_findings:

                    section.append(
                        f"""
Source {finding.get('source_number', '')}
Title: {finding.get('title', '')}
URL: {finding.get('url', '')}
Content: {finding.get('content', '')}
"""
                    )

            # Source list.
            sources = result.get("sources", [])

            if sources:
                section.append("\nSOURCES:")

                for source in sources:
                    section.append(
                        f"- {source.get('title', '')}: "
                        f"{source.get('url', '')}"
                    )

            # Error or status message.
            if result.get("status") == "failed":
                section.append(
                    "ERROR: " + str(result.get("message", "Unknown error"))
                )

        else:
            section.append("RESULT:\n" + str(result))

        formatted_results.append("\n".join(section))

    return "\n\n============================\n\n".join(
        formatted_results
    )


prompt = ChatPromptTemplate.from_messages(
    [
        ("system", SYSTEM_PROMPT),
        (
            "human",
            """
USER REQUEST:
{user_request}

AGENT RESULTS:
{results}

Prepare the final answer using the information above.

Make the answer specific to the user's request.
Do not repeat source titles as if they were destinations.
Do not invent missing prices or details.
"""
        )
    ]
)

def run_response_agent(user_request, results):

    print("\nResponse Agent is preparing the final answer...")

    formatted_results = format_agent_results(results)

    response = (prompt | _get_llm()).invoke({
        "user_request": user_request,
        "results": formatted_results
    })

    final_answer = str(response.content).strip()

    if not final_answer:
        return "The Response Agent could not generate a final answer."

    return final_answer
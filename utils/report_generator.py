from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.enums import TA_CENTER
from reportlab.platypus import (
    SimpleDocTemplate,
    Paragraph,
    Spacer,
    Table,
    TableStyle,
    PageBreak
)

from datetime import datetime
from xml.sax.saxutils import escape
import os

def _safe_paragraph(value):
    return escape(str(value)).replace("\n", "<br/>")


# ============================================================
# GENERATE PDF REPORT
# ============================================================

def generate_pdf_report(user_request, plan, results):

    # --------------------------------------------------------
    # Create reports folder
    # --------------------------------------------------------

    os.makedirs(
        "reports",
        exist_ok=True
    )

    # --------------------------------------------------------
    # Create PDF filename
    # --------------------------------------------------------

    timestamp = datetime.now().strftime(
        "%Y-%m-%d_%H-%M-%S"
    )

    filename = (
        f"reports/execution_report_{timestamp}.pdf"
    )

    # --------------------------------------------------------
    # Create PDF document
    # --------------------------------------------------------

    document = SimpleDocTemplate(
        filename,
        pagesize=A4,
        rightMargin=40,
        leftMargin=40,
        topMargin=40,
        bottomMargin=40
    )

    # --------------------------------------------------------
    # Styles
    # --------------------------------------------------------

    styles = getSampleStyleSheet()

    title_style = ParagraphStyle(
        "TitleStyle",
        parent=styles["Title"],
        alignment=TA_CENTER,
        fontSize=20,
        leading=24,
        spaceAfter=20
    )

    heading_style = ParagraphStyle(
        "HeadingStyle",
        parent=styles["Heading2"],
        fontSize=14,
        leading=18,
        spaceBefore=15,
        spaceAfter=8
    )

    normal_style = ParagraphStyle(
        "NormalStyle",
        parent=styles["BodyText"],
        fontSize=10,
        leading=14
    )

    small_style = ParagraphStyle(
        "SmallStyle",
        parent=styles["BodyText"],
        fontSize=8,
        leading=11
    )

    story = []

    # ========================================================
    # 1. TITLE
    # ========================================================

    story.append(
        Paragraph(
            "AUTONOMOUS MULTI-AGENT<br/>"
            "TASK EXECUTION REPORT",
            title_style
        )
    )

    story.append(
        Paragraph(
            f"Generated: "
            f"{datetime.now().strftime('%d %B %Y, %I:%M %p')}",
            normal_style
        )
    )

    story.append(
        Spacer(1, 20)
    )

    # ========================================================
    # 2. USER REQUEST
    # ========================================================

    story.append(
        Paragraph(
            "1. USER REQUEST",
            heading_style
        )
    )

    # Escape HTML characters
    request_text = _safe_paragraph(user_request)

    story.append(
        Paragraph(
            request_text,
            normal_style
        )
    )

    story.append(
        Spacer(1, 10)
    )

    # ========================================================
    # 3. PLANNER AGENT
    # ========================================================

    story.append(
        Paragraph(
            "2. PLANNER AGENT",
            heading_style
        )
    )

    # --------------------------------------------------------
    # Get plan information
    # --------------------------------------------------------

    if hasattr(plan, "model_dump"):

        plan = plan.model_dump()

    goal = plan.get(
        "goal",
        user_request
    )

    goal_text = _safe_paragraph(goal)

    story.append(
        Paragraph(
            f"<b>Goal:</b> {goal_text}",
            normal_style
        )
    )

    story.append(
        Spacer(1, 8)
    )

    # --------------------------------------------------------
    # Get tasks
    # --------------------------------------------------------

    tasks = plan.get(
        "tasks",
        []
    )

    task_data = [
        [
            "Task ID",
            "Description",
            "Agent",
            "Priority",
            "Dependencies"
        ]
    ]

    for task in tasks:

        # Support both dictionary and Pydantic task
        if hasattr(task, "model_dump"):

            task = task.model_dump()

        description = _safe_paragraph(task.get("description", ""))

        task_data.append(
            [
                str(
                    task.get(
                        "task_id",
                        ""
                    )
                ),
                Paragraph(description, small_style),
                str(
                    task.get(
                        "assigned_agent",
                        ""
                    )
                ),
                str(
                    task.get(
                        "priority",
                        ""
                    )
                ),
                str(
                    task.get(
                        "depends_on",
                        []
                    )
                )
            ]
        )

    # --------------------------------------------------------
    # Planner table
    # --------------------------------------------------------

    task_table = Table(
        task_data,
        colWidths=[
            45,
            180,
            90,
            50,
            80
        ],
        repeatRows=1
    )

    task_table.setStyle(
        TableStyle(
            [
                (
                    "BACKGROUND",
                    (0, 0),
                    (-1, 0),
                    colors.lightgrey
                ),

                (
                    "TEXTCOLOR",
                    (0, 0),
                    (-1, 0),
                    colors.black
                ),

                (
                    "GRID",
                    (0, 0),
                    (-1, -1),
                    0.5,
                    colors.grey
                ),

                (
                    "FONTNAME",
                    (0, 0),
                    (-1, 0),
                    "Helvetica-Bold"
                ),

                (
                    "FONTSIZE",
                    (0, 0),
                    (-1, -1),
                    8
                ),

                (
                    "VALIGN",
                    (0, 0),
                    (-1, -1),
                    "TOP"
                ),

                (
                    "LEFTPADDING",
                    (0, 0),
                    (-1, -1),
                    5
                ),

                (
                    "RIGHTPADDING",
                    (0, 0),
                    (-1, -1),
                    5
                ),

                (
                    "TOPPADDING",
                    (0, 0),
                    (-1, -1),
                    5
                ),

                (
                    "BOTTOMPADDING",
                    (0, 0),
                    (-1, -1),
                    5
                )
            ]
        )
    )

    story.append(
        task_table
    )

    # ========================================================
    # 4. AGENT EXECUTION RESULTS
    # ========================================================

    story.append(
        PageBreak()
    )

    story.append(
        Paragraph(
            "3. AGENT EXECUTION RESULTS",
            heading_style
        )
    )

    if not results:

        story.append(
            Paragraph(
                "No agent execution results found.",
                normal_style
            )
        )

    else:

        for item in results:

            task_id = item.get(
                "task_id",
                ""
            )

            agent = item.get(
                "agent",
                ""
            )

            result = item.get(
                "result",
                ""
            )

            story.append(
                Paragraph(
                    f"Task {task_id} — "
                    f"{str(agent).upper()}",
                    heading_style
                )
            )

            result_text = _safe_paragraph(result)

            story.append(
                Paragraph(
                    result_text,
                    small_style
                )
            )

            story.append(
                Spacer(1, 12)
            )

    # ========================================================
    # 5. FINAL RESPONSE
    # ========================================================

    story.append(
        PageBreak()
    )

    story.append(
        Paragraph(
            "4. FINAL RESPONSE",
            heading_style
        )
    )

    final_response = ""

    for item in results:

        if item.get("agent") == "response":

            final_response = item.get(
                "result",
                ""
            )

    if final_response:

        final_response_text = _safe_paragraph(final_response)

        story.append(
            Paragraph(
                final_response_text,
                normal_style
            )
        )

    else:

        story.append(
            Paragraph(
                "Final response was not generated.",
                normal_style
            )
        )

    # ========================================================
    # 6. EXECUTION SUMMARY
    # ========================================================

    story.append(
        Paragraph(
            "5. EXECUTION SUMMARY",
            heading_style
        )
    )

    total_tasks = len(tasks)

    completed_tasks = sum(1 for item in results if item.get("status", "completed") == "completed")
    failed_tasks = sum(1 for item in results if item.get("status") == "failed")
    execution_status = "FAILED" if failed_tasks else ("COMPLETED" if completed_tasks == total_tasks else "PARTIAL")
    agents_used = ", ".join(sorted({str(item.get("agent", "unknown")) for item in results})) or "None"

    summary_data = [
        [
            "Total Tasks",
            str(total_tasks)
        ],

        [
            "Completed Tasks",
            str(completed_tasks)
        ],

        [
            "Failed Tasks",
            str(failed_tasks)
        ],

        [
            "Execution Status",
            execution_status
        ],

        [
            "Agents Used",
            agents_used
        ]
    ]

    summary_table = Table(
        summary_data,
        colWidths=[
            150,
            300
        ]
    )

    summary_table.setStyle(
        TableStyle(
            [
                (
                    "GRID",
                    (0, 0),
                    (-1, -1),
                    0.5,
                    colors.grey
                ),

                (
                    "FONTNAME",
                    (0, 0),
                    (0, -1),
                    "Helvetica-Bold"
                ),

                (
                    "FONTSIZE",
                    (0, 0),
                    (-1, -1),
                    9
                ),

                (
                    "VALIGN",
                    (0, 0),
                    (-1, -1),
                    "TOP"
                ),

                (
                    "LEFTPADDING",
                    (0, 0),
                    (-1, -1),
                    5
                ),

                (
                    "RIGHTPADDING",
                    (0, 0),
                    (-1, -1),
                    5
                )
            ]
        )
    )

    story.append(
        summary_table
    )

    story.append(
        Spacer(1, 20)
    )

    # ========================================================
    # FOOTER MESSAGE
    # ========================================================

    story.append(
        Paragraph(
            "This report was automatically generated by the "
            "Autonomous Multi-Agent Task Execution Platform v2.",
            normal_style
        )
    )

    # ========================================================
    # BUILD PDF
    # ========================================================

    document.build(
        story
    )

    return filename
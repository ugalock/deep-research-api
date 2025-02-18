import asyncio
import os

from deep_research import deep_research, write_final_report
from feedback import generate_feedback
from output_manager import OutputManager
from cli_style import ask_user, show_header

output = OutputManager()
log = output.log

async def run():
    show_header("Deep Research")
    initial_query = await asyncio.get_running_loop().run_in_executor(
        None,
        lambda: ask_user("What would you like to research?")
    )

    try:
        breadth_input = await asyncio.get_running_loop().run_in_executor(
            None,
            lambda: ask_user("Enter research breadth (recommended 2-10, default 4)")
        )
        breadth = int(breadth_input)
    except ValueError:
        breadth = 4

    try:
        depth_input = await asyncio.get_running_loop().run_in_executor(
            None,
            lambda: ask_user("Enter research depth (recommended 1-5, default 2)")
        )
        depth = int(depth_input)
    except ValueError:
        depth = 2

    log("Creating research plan...")
    follow_up_questions = await generate_feedback(query=initial_query)

    log("\nTo better understand your research needs, please answer these follow-up questions:")
    answers = []
    for question in follow_up_questions:
        answer = await asyncio.get_running_loop().run_in_executor(None, lambda: ask_user(question))
        answers.append(answer)

    combined_query = (
        f"Initial Query: {initial_query}\n"
        "Follow-up Questions and Answers:\n" +
        "\n".join(f"Q: {q}\nA: {a}" for q, a in zip(follow_up_questions, answers))
    )

    log("\nResearching your topic...")
    log("\nStarting research with progress tracking...\n")
    result = await deep_research(
        query=combined_query,
        breadth=breadth,
        depth=depth,
        on_progress=output.update_progress
    )
    output.stop_progress()

    learnings = result.get("learnings", [])
    visited_urls = result.get("visited_urls", [])

    log(f"\nLearnings:\n{chr(10).join(learnings)}")
    log(f"\nVisited URLs ({len(visited_urls)}):\n{chr(10).join(visited_urls)}")
    log("Writing final report...")

    report = await write_final_report(
        prompt=combined_query,
        learnings=learnings,
        visited_urls=visited_urls
    )

    with open("output.md", "w", encoding="utf-8") as f:
        f.write(report)

    log("\nFinal Report:\n")
    log(report)
    log("\nReport has been saved to output.md")

if __name__ == "__main__":
    asyncio.run(run())

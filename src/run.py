import asyncio

from deep_research import deep_research, write_final_report
from feedback import generate_feedback
from output_manager import OutputManager

output = OutputManager()

def log(*args):
    output.log(*args)

async def ask_question(prompt: str) -> str:
    loop = asyncio.get_running_loop()
    return await loop.run_in_executor(None, lambda: input(prompt))

async def run():
    initial_query = await ask_question("What would you like to research? ")

    try:
        breadth = int(await ask_question("Enter research breadth (recommended 2-10, default 4): "))
    except ValueError:
        breadth = 4

    try:
        depth = int(await ask_question("Enter research depth (recommended 1-5, default 2): "))
    except ValueError:
        depth = 2

    log("Creating research plan...")
    follow_up_questions = await generate_feedback(query=initial_query)

    log("\nTo better understand your research needs, please answer these follow-up questions:")
    answers = []
    for question in follow_up_questions:
        answer = await ask_question(f"\n{question}\nYour answer: ")
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

    # Corrected key to match the internal dictionary structure
    learnings = result.get("learnings", [])
    visited_urls = result.get("visited_urls", [])

    log(f"\n\nLearnings:\n\n{chr(10).join(learnings)}")
    log(f"\n\nVisited URLs ({len(visited_urls)}):\n\n{chr(10).join(visited_urls)}")
    log("Writing final report...")

    report = await write_final_report(
        prompt=combined_query,
        learnings=learnings,
        visited_urls=visited_urls
    )

    with open("output.md", "w", encoding="utf-8") as f:
        f.write(report)

    print(f"\n\nFinal Report:\n\n{report}")
    print("\nReport has been saved to output.md")

if __name__ == "__main__":
    asyncio.run(run())

import asyncio
import os
from dataclasses import dataclass
from typing import Any, Callable, Dict, List, Optional

from ai.ai import generate_object
from ai.providers import o3MiniModel, trim_prompt, firecrawl_search
from prompt import system_prompt
from output_manager import OutputManager
from pydantic import BaseModel

output = OutputManager()

def log(*args: Any) -> None:
    output.log(*args)

class SerpQuery(BaseModel):
    query: str
    researchGoal: str

class SerpQueriesSchema(BaseModel):
    queries: List[SerpQuery]

class SerpResultSchema(BaseModel):
    learnings: List[str]
    followUpQuestions: List[str]

class FinalReportSchema(BaseModel):
    reportMarkdown: str

@dataclass
class ResearchProgress:
    current_depth: int
    total_depth: int
    current_breadth: int
    total_breadth: int
    current_query: Optional[str] = None
    total_queries: int = 0
    completed_queries: int = 0

CONCURRENCY_LIMIT = 2

async def generate_serp_queries(
    query: str,
    learnings: Optional[List[str]] = None,
    num_queries: int = 3
) -> List[Dict[str, Any]]:
    extra = ""
    if learnings:
        extra = (
            "Here are some learnings from previous research. "
            "Use them to generate more specific queries:\n" 
            + "\n".join(learnings)
        )

    # Added explicit JSON format instructions:
    prompt_text = (
        f"Given the following prompt from the user, generate a list of SERP queries to research the topic.\n\n"
        f"Return your result in JSON format with the shape:\n"
        f'{{ "queries": [ {{ "query": "string", "researchGoal": "string" }} ] }}\n\n'
        f"Return a maximum of {num_queries} queries, but feel free to return less if the original prompt is clear.\n"
        f"Make sure each query is unique and not similar to each other.\n\n"
        f"<prompt>{query}</prompt>\n\n{extra}"
    )

    res = await generate_object(
        model=o3MiniModel,
        system=system_prompt(),
        prompt=prompt_text,
        schema=SerpQueriesSchema
    )
    log(f"Created {len(res['object'].queries)} queries", res["object"].queries)
    return res["object"].queries[:num_queries]

async def process_serp_result(
    query: str,
    result: Dict[str, Any],
    num_learnings: int = 3,
    num_follow_up_questions: int = 3
) -> Any:
    contents = []
    for item in result.get("data", []):
        if "markdown" in item:
            contents.append(trim_prompt(item["markdown"], 25000))

    log(f"Ran {query}, found {len(contents)} contents")

    contents_wrapped = "\n".join(f"<content>\n{c}\n</content>" for c in contents)
    # Added explicit JSON format instructions:
    prompt_text = (
        f"Given the following contents from a SERP search for <query>{query}</query>, generate a list of learnings.\n"
        f"Return your result in JSON format with the shape:\n"
        f'{{ "learnings": ["..."], "followUpQuestions": ["..."] }}\n\n'
        f"Return a maximum of {num_learnings} learnings, but feel free to return less if the contents are clear.\n"
        f"Make sure each learning is unique and not similar to each other, including any relevant entities or numbers.\n\n"
        f"<contents>{contents_wrapped}</contents>"
    )

    res = await generate_object(
        model=o3MiniModel,
        system=system_prompt(),
        prompt=prompt_text,
        schema=SerpResultSchema
    )
    log(f"Created {len(res['object'].learnings)} learnings", res["object"].learnings)
    return res["object"]

async def deep_research(
    query: str,
    breadth: int,
    depth: int,
    learnings: Optional[List[str]] = None,
    visited_urls: Optional[List[str]] = None,
    on_progress: Optional[Callable[[ResearchProgress], None]] = None
) -> Dict[str, Any]:
    if learnings is None:
        learnings = []
    if visited_urls is None:
        visited_urls = []

    progress = ResearchProgress(
        current_depth=depth,
        total_depth=depth,
        current_breadth=breadth,
        total_breadth=breadth,
        total_queries=0,
        completed_queries=0
    )
    def report_progress(update: Dict[str, Any]) -> None:
        for k, v in update.items():
            setattr(progress, k, v)
        if on_progress:
            on_progress(progress)

    serp_queries = await generate_serp_queries(query, learnings, num_queries=breadth)
    report_progress({
        "total_queries": len(serp_queries),
        "current_query": serp_queries[0].query if serp_queries else None
    })

    loop = asyncio.get_running_loop()
    sem = asyncio.Semaphore(CONCURRENCY_LIMIT)

    async def process_query(serpQ: SerpQuery) -> Dict[str, Any]:
        async with sem:
            try:
                log(f"Processing SERP query: {serpQ}")
                result = await loop.run_in_executor(
                    None,
                    lambda: firecrawl_search(
                        serpQ.query,
                        timeout=15000,
                        limit=5,
                    )
                )
                log(f"Search results received for query '{serpQ.query}': {result}")
                if not result.get("data"):
                    log(f"No results found for query: {serpQ.query}")
                    return {"learnings": [], "visited_urls": []}

                new_learnings_obj = await process_serp_result(
                    serpQ.query,
                    result,
                    num_learnings=breadth // 2,
                    num_follow_up_questions=breadth // 2
                )
                new_urls = []
                for item in result.get("data", []):
                    url = (
                        item.get("url") or
                        item.get("metadata", {}).get("sourceURL") or
                        item.get("metadata", {}).get("pageUrl") or
                        item.get("metadata", {}).get("finalUrl") or
                        item.get("metadata", {}).get("url")
                    )
                    if url:
                        new_urls.append(url)

                all_learnings = learnings + new_learnings_obj.learnings
                all_urls = visited_urls + new_urls
                new_depth = depth - 1
                if new_depth > 0:
                    log(f"Researching deeper, breadth: {breadth // 2}, depth: {new_depth}")
                    report_progress({
                        "current_depth": new_depth,
                        "current_breadth": breadth // 2,
                        "completed_queries": progress.completed_queries + 1,
                        "current_query": serpQ.query,
                    })
                    next_query = (
                        f"Previous research goal: {serpQ.researchGoal}\n"
                        f"Follow-up research directions: {chr(10).join(new_learnings_obj.followUpQuestions)}"
                    ).strip()
                    return await deep_research(
                        query=next_query,
                        breadth=breadth // 2,
                        depth=new_depth,
                        learnings=all_learnings,
                        visited_urls=all_urls,
                        on_progress=on_progress
                    )
                else:
                    report_progress({
                        "current_depth": 0,
                        "completed_queries": progress.completed_queries + 1,
                        "current_query": serpQ.query,
                    })
                    return {"learnings": all_learnings, "visited_urls": all_urls}
            except Exception as e:
                log(f"Error running query: {serpQ.query}: {e}")
                return {"learnings": [], "visited_urls": []}

    tasks = [process_query(q) for q in serp_queries]
    results = await asyncio.gather(*tasks)

    final_learnings = list({l for r in results for l in r["learnings"]})
    final_urls = list({u for r in results for u in r["visited_urls"]})
    return {"learnings": final_learnings, "visited_urls": final_urls}

async def write_final_report(
    prompt: str,
    learnings: List[str],
    visited_urls: List[str]
) -> str:
    learnings_wrapped = "\n".join(f"<learning>\n{l}\n</learning>" for l in learnings)
    trimmed_learnings = trim_prompt(learnings_wrapped, 150_000)
    full_prompt = (
        f"Given the following prompt from the user, write a final report on the topic using the learnings from research. "
        f"Make it as detailed as possible, aim for 3 or more pages, and include ALL the learnings from research. "
        f"Return your result in JSON format with the following structure:\n"
        f'{{ "reportMarkdown": <your report markdown> }}.\n\n'
        f"<prompt>{prompt}</prompt>\n\n"
        f"Here are all the learnings from previous research:\n\n"
        f"<learnings>\n{trimmed_learnings}\n</learnings>"
    )
    res = await generate_object(
        model=o3MiniModel,
        system=system_prompt(),
        prompt=full_prompt,
        schema=FinalReportSchema
    )
    report = res["object"].reportMarkdown
    sources_section = "\n\n## Sources\n\n" + "\n".join(f"- {u}" for u in visited_urls)
    return report + sources_section

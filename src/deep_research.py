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

# --- Pydantic Schemas ---
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
# -----------------------------

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
        extra = "Here are some learnings from previous research, use them to generate more specific queries: " + "\n".join(learnings)
    prompt_text = (
        f"Given the following prompt from the user, generate a list of SERP queries to research the topic. "
        f"Return a maximum of {num_queries} queries, but feel free to return less if the original prompt is clear. "
        f"Make sure each query is unique and not similar to each other: <prompt>{query}</prompt>\n\n{extra}"
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
    contents = [
        trim_prompt(item.get("markdown", ""), 25000)
        for item in result.get("data", [])
        if "markdown" in item
    ]
    log(f"Ran {query}, found {len(contents)} contents")
    contents_wrapped = "\n".join(f"<content>\n{content}\n</content>" for content in contents)
    prompt_text = (
        f"Given the following contents from a SERP search for the query <query>{query}</query>, generate a list of learnings from the contents. "
        f"Return a maximum of {num_learnings} learnings, but feel free to return less if the contents are clear. "
        f"Ensure each learning is unique and information-dense; include entities like people, places, companies, products, metrics, numbers, or dates. "
        f"These learnings will be used to guide further research.\n\n<contents>{contents_wrapped}</contents>"
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
        for key, value in update.items():
            setattr(progress, key, value)
        if on_progress:
            on_progress(progress)
    
    serp_queries = await generate_serp_queries(query, learnings, num_queries=breadth)
    report_progress({
        "total_queries": len(serp_queries),
        "current_query": serp_queries[0].query if serp_queries else None
    })
    
    loop = asyncio.get_running_loop()
    semaphore = asyncio.Semaphore(CONCURRENCY_LIMIT)
    
    async def process_query(serpQuery: Any) -> Dict[str, Any]:
        async with semaphore:
            try:
                result = await loop.run_in_executor(
                    None,
                    lambda: firecrawl_search(
                        serpQuery.query,
                        timeout=15000,
                        limit=5,
                        scrape_options={"formats": ["markdown"]}
                    )
                )
                new_learnings_obj = await process_serp_result(
                    serpQuery.query,
                    result,
                    num_learnings=breadth // 2,
                    num_follow_up_questions=breadth // 2
                )
                new_urls = [item.get("url") for item in result.get("data", []) if item.get("url")]
                all_learnings = learnings + new_learnings_obj.learnings
                all_urls = visited_urls + new_urls
                new_depth = depth - 1
                if new_depth > 0:
                    log(f"Researching deeper, breadth: {breadth // 2}, depth: {new_depth}")
                    report_progress({
                        "current_depth": new_depth,
                        "current_breadth": breadth // 2,
                        "completed_queries": progress.completed_queries + 1,
                        "current_query": serpQuery.query,
                    })
                    next_query = (
                        f"Previous research goal: {serpQuery.researchGoal}\n"
                        f"Follow-up research directions: {chr(10).join(new_learnings_obj.followUpQuestions)}"
                    ).strip()
                    return await deep_research(
                        query=next_query,
                        breadth=breadth // 2,
                        depth=new_depth,
                        learnings=all_learnings,
                        visited_urls=all_urls,
                        on_progress=on_progress,
                    )
                else:
                    report_progress({
                        "current_depth": 0,
                        "completed_queries": progress.completed_queries + 1,
                        "current_query": serpQuery.query,
                    })
                    return {"learnings": all_learnings, "visited_urls": all_urls}
            except Exception as e:
                err_msg = str(e)
                if "Timeout" in err_msg:
                    log(f"Timeout error running query: {serpQuery.query}: {e}")
                else:
                    log(f"Error running query: {serpQuery.query}: {e}")
                return {"learnings": [], "visited_urls": []}
    
    tasks = [process_query(q) for q in serp_queries]
    results = await asyncio.gather(*tasks)
    final_learnings = list({learning for res in results for learning in res.get("learnings", [])})
    final_urls = list({url for res in results for url in res.get("visited_urls", [])})
    return {"learnings": final_learnings, "visited_urls": final_urls}

async def write_final_report(prompt: str, learnings: List[str], visited_urls: List[str]) -> str:
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
    urls_section = "\n\n## Sources\n\n" + "\n".join(f"- {url}" for url in visited_urls)
    return report + urls_section

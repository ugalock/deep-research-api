- [x] **Complete the `ai` module**
  - [x] Implement `generate_object` in `ai.py` to mimic TS's `generateObject`.
  - [x] Ensure it sends the system prompt, user prompt, and handles OpenAI responses.
  - [x] Return typed data consistent with the TS version.

- [x] **Finish the Firecrawl integration**
  - [x] Verify the existence of a Python Firecrawl library or create a stub.
  - [x] Implement the `.search(...)` method to match the expected TS output.
  - [x] Ensure returned results follow the same structure as in the TS version.

- [x] **Fill in missing pieces in `deep_research.py`**
  - [x] Complete the asynchronous logic (e.g., using `asyncio.gather` and semaphores) for handling SERP queries concurrently.
  - [x] Finalize the `process_serp_result` function to extract learnings and follow-up questions.
  - [x] Ensure recursion for deeper research (breadth and depth) is properly implemented.

- [x] **Implement `write_final_report`**
  - [x] Create the function to generate the final markdown report.
  - [x] Ensure it calls OpenAI with the proper prompt and compiles the learnings and sources.
  - [x] Append the visited URLs section to the report as in the TS version.

- [x] **Fix any leftover placeholders**
  - [x] Replace schema placeholders (e.g., `schema={"queries": list}`) with actual validation (using a library like Pydantic if needed) or remove them.
  - [x] Confirm that all placeholder logic is replaced or appropriately handled.

- [ ] **Check environment variables**
  - [ ] Verify `.env.local` contains all required keys (`OPENAI_KEY`, `FIRECRAWL_KEY`, etc.).
  - [ ] Ensure the Python code loads these variables using `os.getenv` correctly.
  - [ ] Confirm consistency between variable names in the TS and Python versions.

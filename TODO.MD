- [x] **Environment Variable Consistency**
  - [x] Confirm all env variables used in TS (OPENAI_KEY, FIRECRAWL_KEY, OPENAI_ENDPOINT, OPENAI_MODEL, CONTEXT_SIZE) are mirrored in Python.
  - [x] Verify fallback values and ensure .env/.env.local loading logic matches TS defaults.

- [ ] **API Model Configuration Parity**
  - [ ] Ensure Python’s OpenAI model call includes any additional parameters (e.g., reasoningEffort, structuredOutputs) if needed.
  - [ ] Compare model configuration between TS and Python versions for consistency.

- [ ] **JSON Parsing and Validation**
  - [ ] Map all TS zod schemas to equivalent Pydantic models.
  - [ ] Verify that every TS schema (for SERP queries, final report, etc.) has a matching Python model with identical fields.

- [ ] **Progress Manager and Output Manager**
  - [ ] Ensure Python’s OutputManager and ProgressManager replicate the TS console output behavior (cursor movement, clearing lines, redrawing progress).
  - [ ] Test that progress updates and final output match the TS user experience.

- [ ] **Concurrency and Timeouts**
  - [ ] Confirm that Python’s concurrency (using asyncio.Semaphore) and timeout values (e.g., 15-second search timeout) match TS defaults.
  - [ ] Verify that the CONCURRENCY_LIMIT is consistent between both versions.

- [ ] **Search and Scrape Options**
  - [ ] Ensure Python’s Firecrawl search parameters (limit, scrapeOptions with formats ["markdown"]) mirror the TS implementation.
  - [ ] Validate that the structure of the Firecrawl response (extracting markdown, url) is handled identically.

- [ ] **Additional Testing**
  - [ ] Extend Python tests to cover providers, feedback, and integration flows—not just text-splitter.
  - [ ] Ensure that the test coverage in Python matches the TS version.

- [ ] **Report Output Differences**
  - [ ] Verify that the final report (output.md) is generated and formatted exactly like the TS version.
  - [ ] Confirm that sources (visited URLs) are appended correctly to the report.

- [ ] **Deployment and Docker Configuration**
  - [ ] Ensure the Python Dockerfile and docker-compose.yml replicate the TS container setup (correct environment mounting, working directory, etc.).
  - [ ] Validate that container naming and startup commands provide a consistent experience.

- [ ] **README and Documentation**
  - [ ] Update the README to reflect any Python-specific setup while mirroring TS instructions.
  - [ ] Document environment setup, usage instructions, and configuration changes to match the TS version.

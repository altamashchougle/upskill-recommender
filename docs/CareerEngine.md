# Career Engine & Taxonomy

UpskillAI relies on a dual-layer career intelligence system to map users to appropriate learning resources.

## 1. The Core Taxonomy
A hardcoded knowledge graph mapping exact job titles (e.g., "Software Engineer", "Data Scientist") to their respective domain requirements, core skills, and natural career progressions.
*   **Aliases:** Handles common variations (e.g., "SDE", "Dev").
*   **Skill Weighting:** Differentiates between critical "domain" skills and secondary "tooling" skills.

## 2. Dynamic Role Expansion (Gemini)
When a user inputs a highly specific or entirely new role (e.g., "Prompt Engineer" or "Mojo Developer"), the system intercepts the request before failing.
1.  **Heuristics Check:** Validates that the input is a plausible technology role.
2.  **LLM Parsing:** Asks Gemini to break down the unknown role into standard skills, categorize its domain, and establish a logical roadmap.
3.  **Persistence:** Saves this newly discovered role into the `expanded_roles.json` file. Subsequent requests for this role bypass the LLM and use the cached local taxonomy natively.

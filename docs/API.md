# API Documentation

The FastAPI backend exposes the following primary REST endpoints:

## GET `/career_path/{job_role}`
Validates a target career role and returns structural metadata.
*   **Parameters:** `job_role` (Path parameter)
*   **Returns:** Detailed roadmap, required skills, and role validation confidence.
*   **Notes:** If the role is entirely unknown, Gemini is invoked to dynamically expand the taxonomy.

## GET `/recommendations`
Fetches a highly customized list of courses ranked by skill gap reduction.
*   **Query Parameters:**
    *   `job_role`: Current role.
    *   `goal`: Target role.
    *   `user_skills`: Comma-separated list of current skills.
    *   `use_ai`: Boolean to enable LLM-enhanced ranking explanations.
    *   `top_n`: Number of results to return.
*   **Returns:** Ranked list of course objects, skill gap analysis, and coverage metrics.

## GET `/skills`
Returns the complete list of available technical skills in the taxonomy for frontend autocomplete.

## GET `/job_roles`
Returns the complete list of known roles in the taxonomy for frontend autocomplete.

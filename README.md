Creating a coding interview prep platform that simulates the technical rounds of an interview process as closely as possible.

Commands:

- `uvicorn app.manin:app --reload`to view endpoints _MUST be in /backend_
  - /docs: FastAPI APIs
- `.venv/bin/python -m pip install <package>`to download any packages
- `docker exec -it ai_interviewer_db psql -U postgres -d ai_interviewer` To view db via command line

TODOS:

- ProblemPageEditor/ProblemPageTerminal can be shorter. Move functions to utils
- Home page should be a public landing page for users who are not signed up/logged in.
- If the auth token is expired/invalid, treat the user as logged out (especially on returning to Home) and clear local auth state to prevent false "logged in" UI and 401 loops.

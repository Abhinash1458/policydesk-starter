# Prompt cheat-sheet — AI-Powered SDLC Workshop

Use these with ChatGPT / Claude / Gemini or Copilot Chat. Always **validate** the answer: run it, test it, read it line by line.

## The pattern: Role · Context · Task · Constraints · Format

```
You are a senior Python backend engineer.                                  ← role
We are building PolicyDesk, a FastAPI + SQLModel insurance app.            ← context
Here is app/models.py: <paste>                                             ← context
Write the /api/quotes POST endpoint that calculates a premium.             ← task
Constraints: use the rules in pricing.py, return 422 on invalid input,     ← constraints
no new dependencies, keep it under 40 lines.
Return only the code, with a 2-line explanation after it.                  ← format
```

## By SDLC phase

**Requirements (Lab 2)**
> Act as a business analyst. From this problem statement, write 8 user stories in "As a … I want … so that …" form, each with 3 acceptance criteria in Given/When/Then. Then list 5 assumptions you made and 5 edge cases we should ask the client about.

**Design (Lab 3)**
> Produce a Mermaid `erDiagram` for these entities: … Include cardinality. Then list the REST endpoints as a table: method, path, request body, response, error codes.

**Explain code (Lab 4)**
> Explain this function line by line to a second-year student. Point out one thing that could go wrong at runtime.

**Generate code (Lab 4)**
> Implement `calculate_premium` in app/services/pricing.py so that all of these tests pass: <paste tests>. Do not change the tests.

**Tests (Lab 5)**
> Write pytest tests for this function. Cover: every branch, boundary values (24/25, 45/46, 60/61), invalid input, and one property that must always hold. Use `@pytest.mark.parametrize`.

**Find edge cases (Lab 5)**
> List 10 inputs that might break this function. For each, say what you expect and why.

**Debug (Lab 6)**
> Here is a traceback and the function it points to. Explain the root cause in 2 sentences, then give the minimal fix. Do not rewrite the whole function.

**Code review (Lab 6)**
> Review this file as a strict senior engineer. Check: correctness, error handling, naming, duplication, security (input validation, injection), performance (N+1 queries). Output a table: line, severity, issue, suggested fix.

**Refactor (Lab 6)**
> Refactor this function for readability without changing behaviour. Keep the public signature. Explain each change in one line.

**Docs (Lab 7)**
> Write a README for this repo: what it does, how to run it, how to test it, API table, project layout. Use the actual file names from this tree: <paste `tree` output>.

**Logs (Lab 7)**
> These are the deployment logs from Render. What failed, why, and what is the exact change to fix it?

## "Validate the AI" checklist

- [ ] Did it invent a file, function, library or flag that does not exist?
- [ ] Does it run? Does `pytest` pass?
- [ ] Did it silently change a requirement (e.g. rounding, a boundary, a status code)?
- [ ] Can you explain every line? If not, ask it to explain — then verify.
- [ ] Would you be comfortable putting your name on this in a code review?

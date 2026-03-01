# Claude Code Best Practices

> Sourced from Greg Isenberg's "Claude Code Clearly Explained (and how to use it)" featuring Ross Mike.
> Video: https://www.youtube.com/watch?v=zxMjOqM7DFs

---

## Core Philosophy

Claude Code is only as good as the instructions you give it. The model is not the bottleneck — your planning is. Treat every session like you're onboarding a talented but context-free junior developer.

As Ross Mike puts it: **"Slop in, slop out."** The models have crossed a capability threshold — instruction clarity is now the bottleneck, not intelligence.

---

## Best Practices

### 1. Planning Is Paramount

Write a detailed PRD (Product Requirements Document) before touching code. Define concrete features, not vague descriptions.

Use Claude's `ask_user_question` tool as your **primary planning technique**. Before writing any code, prompt Claude to interview you about technical implementation, UI/UX concerns, and trade-offs. This forces you to make decisions upfront — database choices, layout details, cost handling, edge cases — instead of letting Claude guess. When Claude guesses on multiple decisions simultaneously, errors compound: one wrong assumption feeds into the next, creating hundreds of downstream issues (compound guessing errors).

- Bad: "Build me a dashboard"
- Good: "Build a portfolio summary page that shows total holdings value, daily P&L, and a pie chart of allocation by sector. Use the existing `/api/portfolio/summary` endpoint."

### 2. Build Manually First

Don't reach for automation tools (RAFL, scaffolders, boilerplate generators) until you've deployed the project manually at least once. You need to understand the full build-deploy cycle yourself before you can effectively direct Claude through it.

### 3. Feature-by-Feature Development

Build one feature at a time. Get it working and tested before moving to the next. This keeps sessions focused, context windows clean, and bugs isolated.

**Workflow:**
1. Define the feature clearly
2. Implement it
3. Test it (manually and with automated tests)
4. Commit
5. Move on to the next feature

### 4. Manage the Context Window

Never let context usage exceed ~50%. When it gets heavy:
- Start a fresh session
- Provide a concise summary of where you left off
- Reference specific files and line numbers rather than re-explaining architecture

Signs you need a fresh session:
- Claude starts forgetting earlier instructions
- Responses become slower or less precise
- You've been in the same session for a long chain of features

### 5. Input Quality = Output Quality

If Claude produces bad output, the first thing to examine is your input. Poor results almost always trace back to vague instructions, missing context, or unclear acceptance criteria — not model limitations.

Before blaming the tool, ask:
- Did I specify what "done" looks like?
- Did I provide the relevant file paths and context?
- Did I break the task into a small enough scope?

### 6. Don't Over-Optimize Early

Master the fundamentals before adding complexity:
- Get comfortable with basic prompting and file editing first
- MCP servers, custom skills, hooks, and advanced tooling come later
- Premature optimization of your workflow adds confusion without proportional benefit

**Priority order:**
1. Clear instructions and planning
2. Consistent project structure (CLAUDE.md, organized code)
3. Good testing habits
4. Advanced tooling (MCPs, hooks, skills)

### 7. Design With Taste

Claude can write code, but architecture, UX decisions, and aesthetic judgment still require human thought. You are the product designer and architect — Claude is the implementer.

- Make layout and UX decisions yourself
- Review generated code for structural quality, not just correctness
- Don't accept the first output if it doesn't feel right

### 8. Test Before You Build the Next Feature

Write a test for each feature before advancing to the next one. Broken foundations compound exponentially in complexity and cost. Don't build feature two on top of an untested feature one.

- Write at least one test per feature that validates core behavior
- Run the full test suite before starting the next feature
- A failing test now is 10x cheaper than a failing test three features later

---

## Session Workflow Checklist

- [ ] Write or update your PRD / feature spec before starting
- [ ] Check that `CLAUDE.md` is up to date with project context
- [ ] Define the single feature you're building this session
- [ ] Keep prompts specific: file paths, function names, expected behavior
- [ ] Test the feature before moving on
- [ ] Commit working code frequently
- [ ] Start a new session when context gets heavy (~50%)

---

## Common Pitfalls

| Pitfall | Fix |
|---|---|
| Vague prompts ("make it better") | Specify exactly what to change and what the result should look like |
| Trying to build everything in one session | One feature per session, commit, move on |
| Ignoring context window limits | Watch usage, start fresh proactively |
| Jumping to advanced tooling | Master basic prompting and planning first |
| Accepting output without review | Always read and test generated code |
| No CLAUDE.md or outdated CLAUDE.md | Keep project instructions current — it's Claude's onboarding doc |
| Automating before understanding | Deploy manually first, automate second |

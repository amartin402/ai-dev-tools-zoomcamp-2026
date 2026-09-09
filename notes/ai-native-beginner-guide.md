# AI-Native Development: Beginner's Guide

A quick-reference workflow for turning a raw idea into a working project with AI coding agents. Based on the four core concepts: **spec-driven development, context engineering, loop engineering, and graph engineering**.

---

## Tooling Landscape

**AI Coding Assistants / IDE Integrations**
Embedded directly into your editor to give inline code suggestions, generate tests, and make multi-file edits as you work — best for tight, in-context help while coding.

**Project Bootstrappers**
Generate an entire starter project from a single natural-language prompt. Great for quick prototyping, not a substitute for the spec-driven process below.

**Agents**
Autonomous coding helpers that pair an LLM with tools — reading/writing files, running commands, managing tasks — so they can carry out multi-step work with minimal supervision. This guide is built around using agents this way.

---

## The Four Concepts

**Spec-driven development**
Before any code is written, the vague idea is turned into a precise, written specification — who it's for, what it does, how it behaves. The agent builds from the spec, not from a guess.
*Implement it by:* brainstorming with a chat assistant one question at a time, then exporting the result as `_docs/plan.md`.

**Context engineering**
Controls what an agent already knows *before* a session starts (commands, rules, roles, prior decisions) instead of re-explaining it every time.
*Implement it by:* keeping a root `AGENTS.md` (read by most agents) that links to supporting docs in `_docs/`.

**Loop engineering**
Instead of prompting an agent step by step, you give it a checkable stop condition ("all issues groomed", "all tests pass") and let the harness re-run it automatically until the condition is true.
*Implement it by:* using a `/goal <condition>` command instead of a one-off prompt.

**Graph engineering**
Multiple specialized agents (e.g. PM, Engineer, QA) each with one job, orchestrated so work flows from one to the next automatically instead of you copy-pasting between them.
*Implement it by:* defining role files in `_docs/team/` and an orchestrator lifecycle in `_docs/process.md`.

---

## Step-by-Step Guide

### 1. Brainstorm the spec (chat assistant, not the coding agent)

Talk your vague idea through in any chat app before touching code.

```
I want to build [ONE-LINE IDEA].

Help me set the scope for this project precisely. I want to brainstorm with
you and understand how the tool should work. Give me options.

Ask me one question at a time and keep your output short.
```

When done:

```
Save everything to a markdown file that I can download.
```

Save the download as `plan.md`.

### 2. Bootstrap the project

**One-time machine setup** (skip if already done — you only do this once, not per project):

Check if Git is installed:
```bash
git --version
```
If missing: `brew install git` (macOS), install from git-scm.com (Windows), or `sudo apt install git` (Linux).

Tell Git who you are (attached to your commits, works fully offline):
```bash
git config --global user.name "Your Name"
git config --global user.email "you@example.com"
```

`git init` and `git commit` need nothing else — no GitHub account required yet, everything so far is local history.

GitHub only comes into play once you want to **push** the repo or have the agent create issues (Step 4). For that, install the GitHub CLI and authenticate once per machine:
```bash
gh auth login
```
This opens a browser login and stores credentials so both `gh` and `git push` work afterward without repeated logins.

| Action | Needs GitHub auth? |
|---|---|
| `git init`, `git add`, `git commit` | No — local only |
| `gh auth login` (one-time) | Yes |
| `gh repo create` / pushing to a remote | Yes |
| Agent creating issues via `gh issue create` | Yes |

**Per-project steps** (repeat for every new project):

```bash
mkdir project-name && cd project-name
git init
mkdir -p _docs
mv ~/Downloads/plan.md _docs/plan.md
git add _docs/plan.md
git commit -m "Add project plan"
```

Commit after every meaningful step — it gives you a clean rollback point.

At this point the repo is still local-only. The actual GitHub repo gets created in Step 4, when you ask the agent to run it (it uses your already-authenticated `gh` CLI under the hood):
```
Create a public GitHub repo for this project.
Move each task from _docs/tasks.md into a GitHub issue.
```

### 3. Choose the stack

In your coding agent:

```
Read _docs/plan.md. Propose multiple options for the tech stack and
explain each option.

Don't write code yet.
```

Pick the one you can review comfortably, or let the agent decide.

### 4. Turn the spec into a backlog

```
Create a backlog with tasks in _docs/tasks.md.

Each task should be small enough to finish in one session, and independent
enough that I could hand it to someone who has not read the others.

Use this template for each task:

## <number>. <title>
Goal: <one line>
Description: <two or three sentences on what the task involves>

The first task should be setting up an empty project with a passing test.

Don't write code yet.
```

Review the tasks. Merge, split, or cut anything outside your MVP.

Push to GitHub Issues (requires authenticated `gh` CLI):

```
Create a public GitHub repo for this project.
Move each task from _docs/tasks.md into a GitHub issue.
```

From here, GitHub Issues is the only backlog — `_docs/tasks.md` is retired.

> **Note on Steps 5–7:** Write this content yourself (or paste it into a prompt) rather than asking the agent to invent it from scratch. These files encode *your* decisions — commands, rules, role behavior — so they're your context to write, not something to delegate. You can still have the agent do the mechanical file-writing: `Create AGENTS.md at the project root with exactly this content: <paste>`. Just don't ask it to guess the content.

### 5. Set up context — `AGENTS.md`

Create at the project root:

```markdown
# AGENTS.md

## Commands
- `<install cmd>` - install dependencies
- `<test cmd>` - run the whole test suite

## Rules
- Dependencies are added in `<manifest file>`. Do not add one without asking.

## Documents
- `_docs/process.md` - how work is organized
- Before writing tests, read `_docs/testing-guidelines.md`
- For anything touching the UI, read `_docs/design-system.md`
```

If you also use Claude Code, add a one-line `CLAUDE.md`:

```
@AGENTS.md
```

### 6. Define `_docs/process.md`

```markdown
# process.md

- Tasks are GitHub issues, one at a time
- Read the acceptance criteria before starting and before closing
- Commit regularly

## Roles
- PM - grooms a task before anyone implements it, follows _docs/team/pm.md
- Engineer - implements one groomed task, follows _docs/team/software-engineer.md
- QA - checks the result against acceptance criteria, follows _docs/team/qa-engineer.md

## Orchestrator
The main session is the orchestrator. It launches the PM, the engineer and
QA as subagents. It does not groom, implement or test itself.

Lifecycle:
1. Pick the next open issue from the backlog
2. PM grooms it
3. Engineer implements it
4. QA verifies it
5. On FAIL, back to step 3 with the QA comment as input
6. On PASS, close the issue
7. Repeat until the backlog is empty

Rules:
- Do not skip step 2
- The engineer does not close the issue
- QA does not fix the code, only outputs PASS or FAIL
- The orchestrator closes the issue only after QA outputs PASS
```

### 7. Define the three agent roles (`_docs/team/`)

**`_docs/team/pm.md`**
```markdown
You're a Product Manager. You groom a task before anyone implements it.

- Read the issue as written
- Rewrite it using the template in _docs/task-template.md
- Make acceptance criteria checkable
- Think about edge cases the original author missed
- Do not write any code

Definition of done:
- Goal, Acceptance Criteria, Out of Scope, and Constraints are all filled in
- Every criterion can be checked by looking at the result
- Anything moved out of scope links to a follow-up issue
```

**`_docs/team/software-engineer.md`**
```markdown
You're a Software Engineer. You implement one groomed task at a time.

- Implement against the acceptance criteria, do not change them
- Stay inside the files and constraints the issue names
- Write tests for what you built
- Do not close the issue
- Commit regularly
```

**`_docs/team/qa-engineer.md`**
```markdown
You're a QA Engineer. You check finished work against the issue that
specified it.

- Check each acceptance criterion against what the code actually does
- Run the tests and report which ones you ran
- Do not fix anything you find — report it as a comment
- Output a verdict: PASS or FAIL (FAIL if a single criterion fails)

Ignore what the implementation claims it does. Only the acceptance
criteria and the running code count.
```

**`_docs/task-template.md`**
```markdown
## Goal
One or two sentences on what should be true when this is done.

## Acceptance criteria
- [ ] A checkable statement

## Out of scope
- Something moved to #TASK-NUMBER

## Constraints
- Files, libraries, or guidelines to follow
```

### 8. Run it — grooming, building, testing, looping

Groom one issue:
```
Groom issue #4
```

Groom everything without manual continuation prompts (loop engineering):
```
/goal groom all issues
```

Implement a groomed issue:
```
Implement issue #2
```

Test it:
```
Test issue #2
```

If QA returns FAIL, don't just say "fix it" — open a **new session** (end the current chat/terminal session and start a fresh one, same tool) and feed it the QA comment directly. A fresh session has no memory of the engineer's earlier assumptions or its belief that the code already worked — it only knows what's in `AGENTS.md` and what you paste in, so it works from the actual failure instead of defending prior work:

```
Read the QA comment on issue #2. Fix the issues it raises without
changing the acceptance criteria. Commit when done.
```

Then re-run QA on the same issue:
```
Test issue #2
```

Repeat this **Engineer → QA** cycle — new engineer session with the latest QA comment as input, then a fresh QA pass — until you get PASS. Each round should only need to happen a couple of times; if it's looping more than 3–4 times, the issue itself may be poorly groomed (go back to Step 8's grooming prompt and refine it) rather than an engineering problem.

### 9. Run the full graph automatically

Once all three roles and the orchestrator lifecycle exist, run the whole backlog end-to-end:

```
/goal work through the backlog
```

The agent reads `AGENTS.md` → `process.md` → the role files, and cycles PM → Engineer → QA → close, issue by issue, until the backlog is empty.

---

## Quick-Reference Prompt Cheat Sheet

| Stage | Prompt |
|---|---|
| Brainstorm spec | `Help me set the scope... Ask me one question at a time and keep your output short.` |
| Save spec | `Save everything to a markdown file that I can download.` |
| Pick stack | `Read _docs/plan.md. Propose multiple options for the tech stack... Don't write code yet.` |
| Build backlog | `Create a backlog with tasks in _docs/tasks.md... Don't write code yet.` |
| Push to GitHub | `Create a public GitHub repo... Move each task into a GitHub issue.` |
| Groom one | `Groom issue #N` |
| Groom all (loop) | `/goal groom all issues` |
| Implement | `Implement issue #N` |
| Test | `Test issue #N` |
| Full graph (loop) | `/goal work through the backlog` |
| Update docs from corrections | `Based on the corrections I made, find the relevant documents and update them. Commit the current work before changing the documents.` |

---

## Small Projects: Simplified Flow

The full three-agent graph (PM → Engineer → QA → Orchestrator) costs more time and tokens than a single engineer loop. For small projects, use **Steps 1–6 only**, skip the PM and QA agent roles (Steps 7 and 9), and replace them with your own judgment. You still groom and test — you just do it yourself in one pass per issue instead of delegating each to a separate agent.

**What changes:** no `_docs/team/` role files, no orchestrator, no `/goal work through the backlog`. Instead: write clear issues upfront, implement one at a time, and review each yourself before closing it.

### Step-by-step flow for one issue

1. **Write the issue with enough detail up front** (during Step 4's backlog creation) — since there's no PM agent to groom it later, give it a clear goal and 2–3 concrete acceptance criteria when you create the backlog.

2. **Implement + self-verify in a single prompt:**
   ```
   Implement issue #2. Write tests for what you build, run the full
   test suite, and report the results before you finish.
   ```

3. **You review it** — this replaces the QA agent:
   - Read the diff against the issue's acceptance criteria
   - Check the test output actually passed
   - Skim the tests themselves to confirm they cover the real behavior, not just the happy path

4. **If something's off, correct it in the same or a fresh session:**
   ```
   This doesn't handle <X>. Fix it and re-run the tests.
   ```

5. **Once you're satisfied, close the issue and commit.**

6. **Move to the next issue and repeat.**

For a handful of issues, this is faster than standing up the full role/orchestrator setup. Switch to the full graph (Steps 7–9) once the backlog is big enough, or the project matters enough, that you want a second pass catching what you might miss reviewing alone.

Source: [AI-Native Development: Specifications, Loop and Graph Engineering](https://aishippingblog.com/p/ai-native-development-specifications) — Alexey Grigorev, AI Dev Tools Zoomcamp.

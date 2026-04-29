# PawPal+

A smart pet care planning assistant that builds a prioritized daily schedule for busy pet owners — factoring in time budgets, task priorities, per-pet fairness, recurring care routines, and evidence-based care guidelines retrieved from a pet knowledge base.

---

## Origin

This project extends **ai110-module2-show-pawpal-starter**, a course starter template that introduced the concept of a single-owner, single-pet task planner. The original scaffold demonstrated basic task tracking (walks, feeding, meds) with a simple time constraint, and asked students to design a UML, implement Python classes, and wire logic into a Streamlit UI. PawPal+ expands on that foundation by supporting multiple pets, per-pet task ownership, frequency-based recurrence, round-robin scheduling fairness, a complete automated test suite, an AI-powered chat assistant using an agentic workflow, and a Retrieval-Augmented Generation (RAG) system that grounds task recommendations in a pet care knowledge base.

---

## What It Does

PawPal+ helps a pet owner answer: *"Given the time I have today, what should I do for each of my pets, and when?"*

The owner sets a daily time budget, registers their pets (with optional special needs), and assigns tasks with priorities, durations, and frequencies. The scheduler builds a fair daily plan — not just a sorted list, but a real schedule with assigned time slots, conflict detection, and explanations for why tasks were included or skipped. Recurring tasks auto-regenerate when completed so the plan stays current without manual upkeep.

The AI assistant lets owners describe their pets in plain English. The agent retrieves evidence-based care guidelines from a knowledge base (RAG), then automatically sets up pets and tasks with parameters informed by those guidelines — not just generic defaults. For example, describing an 8-year-old arthritic dog will produce shorter walks and a high-priority joint supplement task, because the knowledge base specifically calls for those adjustments.

---

## Architecture Overview

```
Human Input (Streamlit manual forms)
    └─▶ Owner / Pet / Task objects
            └─▶ Scheduler.generate_plan()
                    ├─▶ ① Retrieve due tasks per pet
                    ├─▶ ② Sort by priority, then shortest duration
                    ├─▶ ③ Round-robin across pets, fit time budget
                    ├─▶ ④ Assign sequential time slots from 8:00 AM
                    └─▶ ⑤ Detect overlapping time slots
                            └─▶ Schedule table + conflict warnings + explanation
                                    └─▶ Human reviews → marks complete → plan updates

Natural Language Input (AI chat)
    └─▶ PawPalAgent.chat()
            └─▶ Gemini LLM (function calling loop)
                    ├─▶ get_pet_care_info → KnowledgeBase.retrieve() [RAG]
                    │       └─▶ returns species/age/condition-specific guidelines
                    ├─▶ add_pet  → Owner / Pet objects (same as manual)
                    ├─▶ add_task → Task objects, informed by retrieved guidelines
                    └─▶ generate_schedule → Scheduler (same engine as manual)
```

The system has seven components:

| Component | Role |
|---|---|
| **Streamlit UI** (`app.py`) | Collects manual input and chat input, renders schedule and warnings |
| **Data Model** (`pawpal_system.py`) | Owner → Pet → Task ownership hierarchy |
| **Scheduler** (`pawpal_system.py`) | Core scheduling engine — retrieve, sort, pack, assign, detect |
| **PawPalAgent** (`agent.py`) | Gemini-powered agent with tool use; orchestrates RAG + data model calls |
| **Knowledge Base** (`knowledge_base.py`) | 12 tagged pet care entries; `retrieve()` matches species/age/condition tags |
| **Human Review Loop** | Owner marks tasks complete, adjusts budget, regenerates |
| **pytest suite** (`tests/test_pawpal.py`) | 20 automated tests validating scheduler correctness |

See [`system_diagram.md`](system_diagram.md) for the full Mermaid flowchart and [`uml_diagram.md`](uml_diagram.md) for the class diagram.

---

## Setup

**Requirements:** Python 3.10+

```bash
# 1. Clone the repo
git clone <your-repo-url>
cd applied-ai-system-final

# 2. Create and activate a virtual environment
python -m venv .venv
source .venv/bin/activate        # macOS / Linux
.venv\Scripts\activate           # Windows

# 3. Install dependencies
pip install -r requirements.txt

# 4. (Optional) Set Gemini API key to enable the AI assistant
#    Get a free key at https://aistudio.google.com/apikey
export GEMINI_API_KEY=your_key_here   # macOS / Linux
set GEMINI_API_KEY=your_key_here      # Windows cmd
$env:GEMINI_API_KEY="your_key_here"   # Windows PowerShell

# 5. Run the Streamlit app
python -m streamlit run app.py

# 6. (Optional) Run the demo script in the terminal
python main.py

# 7. (Optional) Run the test suite
python -m pytest
```

The app opens at `http://localhost:8501`. The AI Assistant section requires a Gemini API key; the manual forms work without one.

---

## Sample Interactions

### Example 1 — Basic single-pet schedule

**Input:**
- Owner: Alex, 60 minutes available
- Pet: Mochi, Shiba Inu, age 3
- Tasks: Morning walk (20 min, high), Feeding (10 min, high), Teeth brushing (15 min, medium), Enrichment puzzle (30 min, low)

**Output:**
```
Schedule generated — 45/60 minutes used

#   Time        Task              Duration   Priority   Category
1   08:00 AM    Morning walk      20 min     HIGH       walk
2   08:20 AM    Feeding           10 min     HIGH       feeding
3   08:30 AM    Teeth brushing    15 min     MEDIUM     grooming

No scheduling conflicts detected.

Skipped (1 task didn't fit the time budget):
  - Enrichment puzzle (30 min, low)
```

---

### Example 2 — Multiple pets with special needs

**Input:**
- Owner: Jordan, 90 minutes available
- Pet 1: Mochi (dog), special need: "joint supplement"
- Pet 2: Luna (cat), special need: "insulin"

**Output:**
```
Auto-created meds tasks for: joint supplement
Auto-created meds tasks for: insulin

Schedule generated — 80/90 minutes used

#   Time        Task                Pet     Duration   Priority
1   08:00 AM    Morning walk        Mochi   30 min     HIGH
2   08:30 AM    Feeding             Luna    10 min     HIGH
3   08:40 AM    joint supplement    Mochi   5 min      HIGH
4   08:45 AM    insulin             Luna    5 min      HIGH
5   08:50 AM    Playtime            Mochi   20 min     MEDIUM
6   09:10 AM    Litter box          Luna    10 min     MEDIUM
```

---

### Example 3 — Completing a task and seeing recurrence

**Input:** Owner marks "Morning walk" (daily) as complete.

**Output:**
```
Completed: Morning walk
Next occurrence auto-created, due: 2026-04-30
```

---

### Example 4 — AI Assistant with RAG

**User types in chat:** *"My 8-year-old Labrador Max has arthritis. Set him up with walks, feeding, and a joint supplement."*

**What the agent does internally:**
1. Calls `get_pet_care_info(species="dog", age=8, conditions=["arthritis"])` — retrieves Senior Dog Care + Joint Issues guidelines from the knowledge base
2. Reads guidelines: *"shorter walks 10-15 min, avoid high-impact activity, joint supplements daily high priority, orthopedic bedding"*
3. Calls `add_pet(name="Max", species="dog", breed="Labrador", age=8)`
4. Calls `add_task` for morning walk with **15 min** duration (guidelines override the 20 min default)
5. Calls `add_task` for feeding
6. Calls `add_task` for joint supplement (high priority, daily, 5 min)
7. Calls `generate_schedule`

**AI response:**
```
I've set Max up based on senior dog and arthritis care guidelines.
His walks are shortened to 15 min (gentle pace recommended for arthritic dogs),
and his joint supplement is marked high priority daily.

Schedule: 30/60 min used
1. 08:00 AM [HIGH] Morning walk — Max (15 min)
2. 08:15 AM [HIGH] Feeding — Max (10 min)
3. 08:25 AM [HIGH] Joint supplement — Max (5 min)
```

The tasks appear immediately in the manual forms and schedule below the chat — the AI and the manual UI share the same live state.

---

## Design Decisions

**Tasks live inside Pet, not in a global list.**
The initial design had a flat task list on the Scheduler. Moving tasks to be owned by their Pet makes ownership explicit — you're not going to mix up which dog needs meds and which cat needs grooming. It also enables per-pet fairness naturally.

**Greedy algorithm over optimal packing.**
The scheduler uses a greedy approach: sort by priority and duration, pack tasks until the budget is full. A true knapsack solution would find globally optimal combinations but grows expensive with task count and is harder to explain. For a daily pet care schedule (typically under 20 tasks), greedy is fast, predictable, and produces results the owner can reason about.

**Round-robin fairness across pets.**
A pure greedy sort would let one pet's high-priority tasks consume the entire budget. The round-robin ensures each pet gets a turn before any pet gets a second slot.

**Tag-based RAG over semantic search.**
The knowledge base uses tag matching instead of vector embeddings. Each entry has explicit tags (`["dog", "senior", "arthritis"]`), and the retriever builds a query tag set from the pet's species, age group, and condition keywords. For a bounded domain like pet care (12 entries, well-defined categories), tag matching is deterministic, requires no embedding model or vector database, and produces the same results every run — making it easier to test and reason about. The trade-off is that it won't handle phrasing variations the tags don't cover (e.g., "bad hips" vs. "arthritis"), but condition keywords are normalized by splitting on spaces, which handles most cases.

**Agentic workflow with tool use over a single prompt.**
The AI assistant uses a multi-turn function-calling loop rather than a one-shot prompt. This lets the agent inspect current state before acting (`get_current_state`), retrieve knowledge before setting parameters (`get_pet_care_info`), and make multiple targeted changes (`add_pet`, `add_task`) rather than trying to produce a full JSON config in one response. It also means partial progress is visible — if the agent adds pets but runs out of budget reasoning about tasks, the owner can see what was done and continue manually.

**No data persistence.**
All state lives in Streamlit session state. Refreshing the browser clears everything. This was an intentional scope decision — adding a database layer would be the right next step, but it would significantly increase complexity without changing the scheduling or AI logic, which are the core of the project.

**Special needs auto-generate meds tasks.**
Rather than making the owner manually create a medication task for each condition, the system generates one automatically with sensible defaults (5 min, high priority, daily). This reduces setup friction for the most safety-critical task type.

---

## Testing Summary

I ran 20 pytest tests covering six areas: task basics, budget constraints, sorting, recurrence, fairness, and conflict detection.

What worked well: the tests caught real bugs during development. When I first wrote the recurrence logic, weekly tasks were getting tomorrow's date instead of +7 days — the test caught that immediately. The fairness tests also revealed that my initial round-robin had an off-by-one error where the last pet's queue would sometimes get skipped.

What I would improve: the test suite covers the rule-based scheduler comprehensively but has no automated tests for the AI layer. The agentic loop and RAG retrieval are tested manually (by running the app and sending messages). Adding tests that mock the Gemini API and verify that the agent calls the right tools in the right order would increase confidence significantly.

Confidence level: **4/5**. The core scheduling logic is solid and well-covered. The missing star is for the untested AI layer and edge cases like tasks past midnight or rapid UI interactions.

---

## Reflection

The biggest thing this project taught me is that the initial design is never the final design — and that's fine. I started with a UML that had four basic classes and an obvious limitation: it only supported one pet. That sketch felt incomplete, but getting it down first made everything easier. Each time I added a feature, the design naturally revealed what it needed next.

Adding the AI layer late in the process also taught me something about integration. The agentic workflow and RAG features only felt real when they were wired into the same live objects as the manual UI — not a separate demo, but the same `Owner` and `Pet` instances the scheduler uses. That constraint (full integration, shared state) forced cleaner tool design than I would have done otherwise.

---

## Project Structure

```
applied-ai-system-final/
├── app.py                  # Streamlit web UI (manual forms + AI chat)
├── pawpal_system.py        # Core classes: Task, Pet, Owner, Scheduler
├── agent.py                # PawPalAgent: Gemini tool-use agentic loop
├── knowledge_base.py       # RAG data: 12 pet care entries + retrieve()
├── main.py                 # Terminal demo script
├── requirements.txt        # Dependencies
├── system_diagram.md       # Runtime data flow diagram (Mermaid)
├── uml_diagram.md          # Class diagram (Mermaid)
├── uml_final.png           # Class diagram image
├── demo.png                # App screenshot
├── reflection.md           # Project reflection
└── tests/
    └── test_pawpal.py      # 20 pytest test cases
```

---

## Dependencies

```
streamlit>=1.30
pytest>=7.0
google-genai>=1.0.0
```

The `google-genai` package is required for the AI assistant. The rest of the app works without a Gemini API key.

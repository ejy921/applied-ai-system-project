# PawPal+

A smart pet care planning assistant that builds a prioritized daily schedule for busy pet owners — factoring in time budgets, task priorities, per-pet fairness, and recurring care routines.

---

## Origin

This project extends **ai110-module2-show-pawpal-starter**, a course starter template that introduced the concept of a single-owner, single-pet task planner. The original scaffold demonstrated basic task tracking (walks, feeding, meds) with a simple time constraint, and asked students to design a UML, implement Python classes, and wire logic into a Streamlit UI. PawPal+ expands on that foundation by supporting multiple pets, per-pet task ownership, frequency-based recurrence, round-robin scheduling fairness, conflict detection, and a complete automated test suite.

---

## What It Does

PawPal+ helps a pet owner answer: *"Given the time I have today, what should I do for each of my pets, and when?"*

The owner sets a daily time budget, registers their pets (with optional special needs), and assigns tasks with priorities, durations, and frequencies. The scheduler builds a fair daily plan — not just a sorted list, but a real schedule with assigned time slots, conflict detection, and explanations for why tasks were included or skipped. Recurring tasks auto-regenerate when completed so the plan stays current without manual upkeep.

---

## Architecture Overview

```
Human Input (Streamlit)
    └─▶ Owner / Pet / Task objects
            └─▶ Scheduler.generate_plan()
                    ├─▶ ① Retrieve due tasks per pet
                    ├─▶ ② Sort by priority, then shortest duration
                    ├─▶ ③ Round-robin across pets, fit time budget
                    ├─▶ ④ Assign sequential time slots from 8:00 AM
                    └─▶ ⑤ Detect overlapping time slots
                            └─▶ Schedule table + conflict warnings + explanation
                                    └─▶ Human reviews → marks complete → plan updates
```

The system has five components:

| Component | Role |
|---|---|
| **Streamlit UI** (`app.py`) | Collects input, renders schedule and warnings |
| **Data Model** (`pawpal_system.py`) | Owner → Pet → Task ownership hierarchy |
| **Scheduler** (`pawpal_system.py`) | Core scheduling engine — retrieve, sort, pack, assign, detect |
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

# 4. Run the Streamlit app
streamlit run app.py

# 5. (Optional) Run the demo script in the terminal
python main.py

# 6. (Optional) Run the test suite
python -m pytest
```

The app opens at `http://localhost:8501`.

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

The scheduler fills the budget with the two high-priority tasks first, then fits the medium-priority grooming task, and correctly skips the low-priority enrichment task that would push the total to 75 minutes.

---

### Example 2 — Multiple pets with special needs

**Input:**
- Owner: Jordan, 90 minutes available
- Pet 1: Mochi (dog), special need: "joint supplement"
- Pet 2: Luna (cat), special need: "insulin"
- Tasks added to Mochi: Morning walk (30 min, high), Playtime (20 min, medium)
- Tasks added to Luna: Feeding (10 min, high), Litter box (10 min, medium)

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

The round-robin ensures both pets are represented before any pet receives a second task. High-priority meds tasks (auto-generated from special needs) are slotted before medium-priority tasks regardless of which pet they belong to.

---

### Example 3 — Completing a task and seeing recurrence

**Input:** Owner marks "Morning walk" (daily) as complete.

**Output:**
```
Completed: Morning walk
Next occurrence auto-created, due: 2026-04-29
```

The original task is marked done, and a new `Task` object is automatically added to Mochi's task list with `due_date = today + 1 day`. The next time the owner generates a plan, the walk reappears in the schedule without any manual re-entry.

---

## Design Decisions

**Tasks live inside Pet, not in a global list.**
The initial design had a flat task list on the Scheduler. Moving tasks to be owned by their Pet makes ownership explicit — you're not going to mix up which dog needs meds and which cat needs grooming. It also enables per-pet fairness naturally.

**Greedy algorithm over optimal packing.**
The scheduler uses a greedy approach: sort by priority and duration, pack tasks until the budget is full. A true knapsack solution would find globally optimal combinations but grows expensive with task count and is harder to explain. For a daily pet care schedule (typically under 20 tasks), greedy is fast, predictable, and produces results the owner can reason about. The trade-off is that the scheduler can miss combinations that would fit more tasks — but the owner can always adjust manually.

**Round-robin fairness across pets.**
A pure greedy sort would let one pet's high-priority tasks consume the entire budget. The round-robin ensures each pet gets a turn before any pet gets a second slot, so a two-dog household doesn't mean the older dog's tasks always crowd out the younger one.

**No data persistence.**
All state lives in Streamlit session state. Refreshing the browser clears everything. This was an intentional scope decision — adding a database layer would be the right next step, but it would significantly increase complexity without changing the scheduling logic, which is the core of the project.

**Special needs auto-generate meds tasks.**
Rather than making the owner manually create a medication task for each condition, the system generates one automatically with sensible defaults (5 min, high priority, daily). This reduces setup friction for the most safety-critical task type.

---

## Testing Summary

I ran 20 pytest tests covering six areas: task basics, budget constraints, sorting, recurrence, fairness, and conflict detection.

What worked well: the tests caught real bugs during development. When I first wrote the recurrence logic, weekly tasks were getting tomorrow's date instead of +7 days — the test caught that immediately. The fairness tests also revealed that my initial round-robin had an off-by-one error where the last pet's queue would sometimes get skipped. I wouldn't have caught either of those just by eyeballing the Streamlit output.

What I would improve: the test suite has gaps at the edges. I haven't tested task lists with 100+ items, tasks that push the schedule past midnight, or rapid Streamlit interactions (like clicking "Generate" while a previous plan is still visible). The UI layer is only testable manually, which means I'm relying on judgment there. If I were to continue this project, I'd add a few integration tests using `streamlit.testing.v1` and stress tests for the scheduler with large inputs.

Confidence level: **4/5**. The core logic is solid and the important paths are covered. The missing star is for those untested edges.

---

## Reflection

The biggest thing this project taught me is that the initial design is never the final design — and that's fine. I started with a UML that had four basic classes and an obvious limitation: it only supported one pet. That sketch felt incomplete, but getting it down first made everything easier. Each time I added a feature, the design naturally revealed what it needed next. Trying to design the perfect system upfront would have wasted time I didn't have.

Working with AI throughout the build taught me something I didn't expect: the value isn't in accepting whatever the AI generates. It's in having a real back-and-forth where you describe what you want, evaluate what comes back, and push back when something doesn't fit. When AI suggested seven improvements to the scheduler, I pushed back and asked which three would actually matter. That conversation produced better results than blindly implementing all seven or ignoring the suggestions entirely.

On the technical side, I learned how quickly a "simple" scheduling problem gains real complexity once you factor in time budgets, priorities, fairness, recurrence, and conflict detection. Each constraint is easy in isolation; making them work together without any one of them overriding the others requires deliberate design. That's the kind of problem I want to keep working on.

---

## Project Structure

```
applied-ai-system-final/
├── app.py                  # Streamlit web UI
├── pawpal_system.py        # Core classes: Task, Pet, Owner, Scheduler
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
```

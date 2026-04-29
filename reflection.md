# PawPal+ Project Reflection

## 1. System Design

- adding user information, including available time and preferences
- adding tasks to do, including duration, priority, and frequency
- seeing today's tasks that is given by the program

**a. Initial design**

My first UML had four classes but they were pretty simple compared to what I ended up with.

Owner just had name, available time, and preferences. It could only handle one pet which looking back was kind of limiting. Pet stored basic info like species, breed, age, and special needs but didn't actually hold any tasks. Task had the core stuff like name, category, duration, priority, and frequency. And Scheduler took in an owner, a single pet, and a separate task list to build the plan.

Honestly the initial design was more of a rough sketch. I knew I needed these four pieces but I hadn't thought through how they'd actually connect to each other in a meaningful way.

**b. Design changes**

Yeah the design changed a lot actually. The biggest one was moving tasks to live inside Pet instead of being a separate floating list. That made way more sense because in real life each pet has their own tasks — you're not going to mix up which dog needs meds vs which cat needs grooming.

I also changed Owner to hold a list of pets instead of just one. The original 1-to-1 relationship didn't make sense for anyone who has more than one pet, which is pretty common. And because of that change, Scheduler got simplified — it only takes an Owner now and pulls tasks through the pets, instead of needing everything passed in separately.

The other big addition was all the date/time stuff. Originally Task didn't track when it was last completed or when its next due, so there was no way to handle recurring tasks properly. Adding last_completed, due_date, and scheduled_time made the whole frequency system actually work.

The final additions were the AI layer: PawPalAgent (an agentic loop powered by Gemini with function calling) and KnowledgeBase (a RAG retrieval module with 12 tagged pet care entries). These sit on top of the existing data model — the agent creates the same Owner, Pet, and Task objects as the manual UI, so both paths share live state.

---

## 2. Scheduling Logic and Tradeoffs

**a. Constraints and priorities**

The scheduler looks at three main things: time budget, task priority, and frequency.

Time budget is the hard limit — if you only have 60 minutes, it won't schedule 90 minutes of tasks. Priority decides what gets in first: high priority tasks always beat medium and low. And frequency filtering makes sure weekly tasks don't show up every day, only when they're actually due.

I decided time and priority mattered most because that felt like how you'd actually think about it as a pet owner. Like if I only have an hour, I'm definitely feeding my dog before I brush him. The frequency thing came later when I realized the scheduler was putting weekly flea meds on the schedule every single day which was obviously wrong.

There's also a fairness component — the scheduler round-robins between pets so if you have three animals, one doesn't hog all the time slots. I added that after realizing the greedy sort would just favor whichever pet had the most high-priority tasks.

**b. Tradeoffs**

The scheduler uses a greedy algorithm — it sorts tasks by priority and duration, then packs them into the time budget one by one until it runs out of room. This means it always picks the "best-looking" next task, but it can miss a better overall combination. A true optimal solution would require checking every possible combination (a knapsack problem), which gets expensive fast. The greedy approach is a reasonable tradeoff here because pet care schedules are small (typically under 20 tasks), the stakes are low if a low-priority task gets bumped, and the owner can always adjust manually.

---

## 3. AI Features

**a. Agentic workflow**

The AI assistant uses Gemini (gemini-2.0-flash) with a multi-turn function-calling loop. When an owner describes their pet in plain English, the agent doesn't try to produce everything in one shot. Instead it calls tools in sequence: first checking current state, then retrieving care guidelines, then adding the pet, then adding tasks one by one, then generating the schedule. Each tool call returns real data from the live system, so the agent's next decision is based on what was actually done rather than what it assumed.

The key design decision was wiring the agent's tools directly to the same Owner, Pet, and Task objects used by the manual UI — not a separate copy. That means anything the agent creates instantly appears in the schedule section and the filter/complete section below the chat. There's no sync step because there's nothing to sync.

**b. Retrieval-Augmented Generation (RAG)**

Before the agent decides what tasks to create for a pet, it calls get_pet_care_info, which runs KnowledgeBase.retrieve(). That function builds a tag set from the pet's species, age group, and any condition keywords, then returns all knowledge base entries whose tags intersect. The retrieved text is sent back to Gemini, which uses it to set task parameters — so a senior dog with arthritis gets 15-minute walks instead of the 20-minute default, because the knowledge base says "10-15 min gentle walks" for that case.

The knowledge base uses tag matching instead of vector embeddings. For a bounded domain like pet care (12 entries, well-defined categories), tag matching is deterministic and requires no external model. The tradeoff is that unusual phrasings not covered by the tags won't match, but condition keywords are split on spaces so "hip dysplasia" and "arthritis" both resolve to known tags.

---

## 4. Testing and Verification

**a. What you tested**

I tested 20 different behaviors across six categories:

- Basic stuff like marking tasks complete and adding them to pets
- Budget edge cases like zero time, tasks too big for the budget, and exact fits
- Sorting to make sure priority tiebreakers work and single-item lists don't crash
- Recurrence to confirm daily tasks get tomorrow's date, weekly get +7 days, and unknown frequencies don't create phantom tasks
- Fairness to verify three pets all get represented in the plan
- Conflict detection for both clean plans and manually overlapping time slots

These tests matter because the scheduler has a lot of moving parts. Without them I wouldn't trust that changing one thing (like the sorting logic) didn't break something else (like the fairness round-robin).

**b. What isn't tested**

The automated test suite covers the rule-based scheduler but not the AI layer. The agentic loop and RAG retrieval are tested manually by running the app and sending messages. Automated tests for the AI would need to mock the Gemini API and assert that the agent calls tools in the right order with the right parameters. That's a meaningful gap — if I extended this project, that would be the first thing I'd add.

**c. Confidence**

I'd say 4 out of 5. The core scheduling logic is solid and the important paths are covered. The missing star is for the untested AI layer and edge cases like a very large task list or tasks that push past midnight.

---

## 5. Reflection

**a. What went well**

I'm most happy with how the scheduling algorithm came together. The combination of priority sorting, round-robin fairness, frequency filtering, and time slot assignment makes the output feel like a real daily plan rather than just a sorted list.

The AI integration also came out better than expected. The moment it clicked was when I realized the agent should share the same live objects as the manual UI rather than operating in isolation. Once that was true, the chat section stopped feeling like a separate demo and started feeling like a natural alternate input path.

The RAG design was cleaner than I expected for how little infrastructure it required. Twelve entries with explicit tags, a set intersection lookup, and the retrieved text flows directly into the LLM's context. No vector database, no embeddings, and the results are fully deterministic — which makes it easy to reason about and test manually.

**b. What you would improve**

The time slot system is pretty rigid right now — everything starts at 8 AM and goes sequentially. Letting the owner set preferred times for certain categories would make it more practical.

I'd also add automated tests for the AI layer — a mock Gemini client that asserts the agent calls get_pet_care_info before add_task, and that the retrieved guidelines actually change the task parameters.

Data persistence is the other obvious gap. Refreshing the browser loses everything because all state lives in Streamlit session state.

**c. Key takeaway**

The biggest thing I learned is that the initial design is never the final design, and that's fine. I started with a simple UML that had obvious flaws (single pet, no task ownership, no dates) but getting that rough version down first made it easier to iterate. Each time I added a feature, the design naturally evolved to show what it needed next.

Adding the AI features taught me that integration matters as much as the features themselves. The agentic workflow and RAG only became genuinely useful when they were wired into the same state as the rest of the app. A standalone AI demo that doesn't affect the schedule would have been interesting but not actually helpful. The constraint of full integration forced cleaner design than I would have done with more freedom.

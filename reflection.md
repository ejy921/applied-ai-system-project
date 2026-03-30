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

---

## 2. Scheduling Logic and Tradeoffs

**a. Constraints and priorities**

The scheduler looks at three main things: time budget, task priority, and frequency.

Time budget is the hard limit — if you only have 60 minutes, it won't schedule 90 minutes of tasks. Priority decides what gets in first: high priority tasks always beat medium and low. And frequency filtering makes sure weekly tasks don't show up every day, only when they're actually due.

I decided time and priority mattered most because that felt like how you'd actually think about it as a pet owner. Like if I only have an hour, I'm definitely feeding my dog before I brush him. The frequency thing came later when I realized the scheduler was putting weekly flea meds on the schedule every single day which was obviously wrong.

There's also a fairness component — the scheduler round-robins between pets so if you have three animals, one doesn't hog all the time slots. I added that after realizing the greedy sort would just favor whichever pet had the most high-priority tasks.

**b. Tradeoffs**

The scheduler uses a greedy algorithm — it sorts tasks by priority and duration, then packs them into the time budget one by one until it runs out of room. This means it always picks the "best-looking" next task, but it can miss a better overall combination. For example, if there are 20 minutes left and the next candidate is a 25-minute medium-priority task, the scheduler skips it — even though dropping a 10-minute task already in the plan and swapping in both a 15-minute and a 10-minute task might cover more ground. A true optimal solution would require checking every possible combination (a knapsack problem), which gets expensive fast. The greedy approach is a reasonable tradeoff here because pet care schedules are small (typically under 20 tasks), the stakes are low if a low-priority task gets bumped, and the owner can always adjust manually.

---

## 3. AI Collaboration

**a. How you used AI**

I used AI pretty heavily throughout. At the start I had it review my skeleton classes and point out what was missing — that's how I caught that Pet needed to own its tasks and Owner needed to support multiple pets. Those weren't things I had thought about in my initial UML.

For implementation I'd describe what I wanted (like "add frequency filtering" or "make the scheduler fair across pets") and let it write the code, then I'd read through it to make sure I understood what it did. The most helpful prompts were when I asked it to suggest improvements and then asked which ones actually mattered. It gave me seven ideas but helped me narrow down to the three that would make the biggest difference instead of trying to do everything.

I also had it generate all my tests. I asked "what are the most important edge cases" first, reviewed the list, and then told it to turn them into actual pytest cases. That was faster than writing them from scratch and it caught things I probably wouldn't have thought of like the "complete same task twice" case.

**b. Judgment and verification**

When AI suggested seven improvements to the scheduler, I didn't just implement all of them. I pushed back and asked which ones would actually make a significant difference. It narrowed it down to three — frequency filtering, per-pet fairness, and special needs auto-tasks — and explained why the others were either cosmetic or scope creep. That felt right to me so I went with those three.

I also verified things by running the code after every change. Like after adding the recurrence logic, I checked main.py output to make sure the due dates were correct and that task counts actually increased. If something looked off in the terminal output I'd go back and read the code more carefully before moving on.

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

**b. Confidence**

I'd say 4 out of 5. The core logic is solid and the tests cover the important paths. But there are gaps — I haven't tested what happens with a really large number of tasks (like 100+), tasks that run past midnight, or edge cases with the Streamlit UI like rapid button clicking. Those would be next if I had more time.

---

## 5. Reflection

**a. What went well**

I'm most happy with how the scheduling algorithm came together. The combination of priority sorting, round-robin fairness, frequency filtering, and time slot assignment makes the output feel like a real daily plan rather than just a sorted list. When I run main.py and see the schedule with actual times and clear explanations for why things were skipped, it feels like something that could actually be useful.

The test suite also came out better than expected. Having 20 tests that all pass gives me confidence to make changes without worrying about breaking things.

**b. What you would improve**

The time slot system is pretty rigid right now — everything starts at 8 AM and goes sequentially. In reality you might want to walk the dog at 7 AM and give meds at 9 PM. Letting the owner set preferred times for certain categories would make it way more practical.

I'd also want to clean up the Streamlit UI more. It works but it's not the prettiest thing. And the data doesn't persist between sessions since everything lives in session state, so refreshing the browser loses everything.

**c. Key takeaway**

The biggest thing I learned is that the initial design is never the final design, and that's fine. I started with a simple UML that had obvious flaws (single pet, no task ownership, no dates) but getting that rough version down first made it way easier to iterate. Each time I added a feature, the design naturally evolved. Trying to design the perfect system upfront would have been a waste of time because I didn't know what I needed until I started building it.

Working with AI taught me that the value isn't in blindly accepting code — it's in having a conversation where you describe what you want, evaluate what comes back, and push back when something doesn't fit. The AI suggested stuff I wouldn't have thought of, but I still had to decide what was worth building and verify it actually worked.

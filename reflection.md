# PawPal+ Project Reflection

## 1. System Design

- adding user information, including available time and preferences
- adding tasks to do, including duration, priority, and frequency
- seeing today's tasks that is given by the program

**a. Initial design**

- Briefly describe your initial UML design.
- What classes did you include, and what responsibilities did you assign to each?

Object: Owner
Attributes: name, available time, preferences
Methods: set availability, get availability, add preference, get preferences

Object: Pet
Attributes: name, species, breed, age, special needs (list of any health or care notes)
Methods: get info, add special need, get special needs

Object: Task
Attributes: name, category (walk, feeding, grooming, meds, enrichment), duration (minutes), priority (high/medium/low), frequency (daily, weekly, etc.)
Methods: add task, edit task, get task, mark complete

Object: Scheduler (Plan Generator)
Attributes: owner (Owner object), pet (Pet object), tasks (list of Task objects), total time budget (from owner availability)
Methods: generate plan — sorts/filters tasks by priority and fits them into available time, get plan summary — returns the daily plan as output, explain plan — gives reasoning for why tasks were chosen/ordered

**b. Design changes**

- Did your design change during implementation?
- If yes, describe at least one change and why you made it.

---

## 2. Scheduling Logic and Tradeoffs

**a. Constraints and priorities**

- What constraints does your scheduler consider (for example: time, priority, preferences)?
- How did you decide which constraints mattered most?

**b. Tradeoffs**

- Describe one tradeoff your scheduler makes.
- Why is that tradeoff reasonable for this scenario?

---

## 3. AI Collaboration

**a. How you used AI**

- How did you use AI tools during this project (for example: design brainstorming, debugging, refactoring)?
- What kinds of prompts or questions were most helpful?

**b. Judgment and verification**

- Describe one moment where you did not accept an AI suggestion as-is.
- How did you evaluate or verify what the AI suggested?

---

## 4. Testing and Verification

**a. What you tested**

- What behaviors did you test?
- Why were these tests important?

**b. Confidence**

- How confident are you that your scheduler works correctly?
- What edge cases would you test next if you had more time?

---

## 5. Reflection

**a. What went well**

- What part of this project are you most satisfied with?

**b. What you would improve**

- If you had another iteration, what would you improve or redesign?

**c. Key takeaway**

- What is one important thing you learned about designing systems or working with AI on this project?

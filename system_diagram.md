# PawPal+ System Diagram

```mermaid
flowchart TD
    subgraph INPUT["Human Input  ·  app.py / Streamlit (manual forms)"]
        A["Owner\nname · time budget (minutes/day)"]
        B["Pet\nspecies · breed · age · special needs"]
        C["Task\ntitle · category · duration · priority · frequency"]
    end

    subgraph AI["AI Layer  ·  agent.py + knowledge_base.py"]
        direction TB
        AI_A["User chat message\n(natural language)"]
        AI_B["PawPalAgent.chat()\nGemini gemini-2.0-flash"]
        AI_C["Tool call: get_pet_care_info\nspecies · age · conditions"]
        AI_D["KnowledgeBase.retrieve()\n12 tagged entries · tag-set intersection"]
        AI_E["Tool calls: add_pet · add_task\ngenerate_schedule"]
        AI_A --> AI_B
        AI_B -- "① RAG lookup" --> AI_C
        AI_C --> AI_D
        AI_D -- "care guidelines text" --> AI_B
        AI_B -- "② create objects" --> AI_E
    end

    subgraph DATA["Data Model  ·  pawpal_system.py"]
        D[(Owner)]
        E[(Pet)]
        F[(Task)]
    end

    subgraph SCHEDULER["Scheduler  ·  Core Engine"]
        direction TB
        G["① Retrieve\ncollect all tasks due today per pet"]
        H["② Sort\npriority high → low, then shortest first"]
        I["③ Schedule\nround-robin across pets, fit time budget"]
        J["④ Assign\nsequential time slots from 8:00 AM"]
        K["⑤ Detect\nflag any overlapping time slots"]
        G --> H --> I --> J --> K
    end

    subgraph OUTPUT["Output  ·  Streamlit UI"]
        L["Daily schedule table\n(time · task · duration · priority)"]
        M["Conflict warnings\n(overlapping slots)"]
        N["Skipped tasks list\n(didn't fit budget)"]
        O["Plan explanation\n('Why these tasks?')"]
    end

    subgraph REVIEW["Human Review Loop"]
        P["Owner reviews schedule"]
        Q["Mark task complete\n→ auto-creates next occurrence"]
        R["Adjust budget or add tasks\n→ regenerate plan"]
    end

    subgraph TESTING["Testing Layer  ·  pytest"]
        S["20 automated tests\ntests/test_pawpal.py"]
        T["Covers: budget constraints · fairness\nrecurrence · conflict detection · sorting"]
        S --> T
    end

    A --> D
    B --> E
    C --> F
    D -- "owns" --> E
    E -- "owns" --> F

    AI_E -- "adds pets & tasks\n(same objects as manual)" --> D

    F --> G

    K --> L
    K --> M
    K --> N
    K --> O

    L --> P
    M --> P
    N --> P
    O --> P

    P --> Q
    P --> R
    Q -- "new Task added to Pet" --> F
    R -- "re-triggers" --> G

    SCHEDULER -. "unit tested by" .-> S
```

## Component Summary

| Component | Role | Type |
|---|---|---|
| **Streamlit UI** (`app.py`) | Collects human input and chat messages, renders output | Human interface |
| **Owner / Pet / Task** (`pawpal_system.py`) | Holds all state — time budget, pet profiles, task list | Data model |
| **Scheduler** (`pawpal_system.py`) | Retrieves, sorts, schedules, assigns times, detects conflicts | Processing engine |
| **PawPalAgent** (`agent.py`) | Gemini-powered agent; orchestrates RAG retrieval and data model tool calls | AI layer |
| **KnowledgeBase** (`knowledge_base.py`) | 12 tagged pet care entries; `retrieve()` matches species, age group, and condition tags | RAG retrieval |
| **Human Review Loop** | Owner reads the plan, marks tasks done, tweaks inputs, reruns | Human-in-the-loop |
| **pytest suite** (`tests/test_pawpal.py`) | Verifies scheduler logic across 20 edge cases | Automated testing |

## Data Flow

```
Manual input
    └─▶ Owner / Pet / Task objects
            └─▶ Scheduler.generate_plan()
                    ├─▶ filter due tasks per pet
                    ├─▶ sort by priority + duration
                    ├─▶ round-robin pack into time budget
                    ├─▶ assign 8 AM time slots
                    └─▶ detect conflicts
                            └─▶ Schedule table + warnings + explanation
                                    └─▶ Human reviews
                                            ├─▶ mark complete → new Task → back to Scheduler
                                            └─▶ adjust inputs → regenerate plan

Natural language input (AI chat)
    └─▶ PawPalAgent (Gemini function-calling loop)
            ├─▶ get_pet_care_info → KnowledgeBase.retrieve(species, age, conditions)
            │       └─▶ returns evidence-based guidelines (e.g. shorter walks for senior arthritic dog)
            ├─▶ add_pet  → same Owner/Pet objects as manual path
            ├─▶ add_task → Task parameters informed by retrieved guidelines
            └─▶ generate_schedule → same Scheduler engine as manual path
```

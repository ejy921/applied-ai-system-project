# PawPal+ System Diagram

```mermaid
flowchart TD
    subgraph INPUT["Human Input  ·  app.py / Streamlit"]
        A["Owner\nname · time budget (minutes/day)"]
        B["Pet\nspecies · breed · age · special needs"]
        C["Task\ntitle · category · duration · priority · frequency"]
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
| **Streamlit UI** (`app.py`) | Collects human input, renders output | Human interface |
| **Owner / Pet / Task** (`pawpal_system.py`) | Holds all state — time budget, pet profiles, task list | Data model |
| **Scheduler** (`pawpal_system.py`) | Retrieves, sorts, schedules, assigns times, detects conflicts | Processing engine |
| **Human Review Loop** | Owner reads the plan, marks tasks done, tweaks inputs, reruns | Human-in-the-loop |
| **pytest suite** (`tests/test_pawpal.py`) | Verifies scheduler logic across 20 edge cases | Automated testing |

## Data Flow

```
Human input
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
```

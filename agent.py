import os
import anthropic
from pawpal_system import Owner, Pet, Task, Scheduler

TOOLS = [
    {
        "name": "get_current_state",
        "description": "Get the current list of pets and their tasks. Call this to understand what is already set up before making changes.",
        "input_schema": {
            "type": "object",
            "properties": {},
            "required": [],
        },
    },
    {
        "name": "add_pet",
        "description": "Add a new pet to the owner's profile.",
        "input_schema": {
            "type": "object",
            "properties": {
                "name": {"type": "string"},
                "species": {"type": "string", "enum": ["dog", "cat", "other"]},
                "breed": {"type": "string", "description": "Pet's breed, e.g. 'Shiba Inu'"},
                "age": {"type": "integer"},
                "special_needs": {
                    "type": "array",
                    "items": {"type": "string"},
                    "description": "Medical conditions or medications, e.g. ['insulin', 'joint supplement']",
                },
            },
            "required": ["name", "species", "breed", "age"],
        },
    },
    {
        "name": "add_task",
        "description": (
            "Add a care task to a specific pet. "
            "Use sensible defaults: walks=20min/high/daily, feeding=10min/high/daily, "
            "grooming=15min/medium/weekly, meds=5min/high/daily, enrichment=20min/low/daily."
        ),
        "input_schema": {
            "type": "object",
            "properties": {
                "pet_name": {"type": "string"},
                "task_name": {"type": "string"},
                "category": {
                    "type": "string",
                    "enum": ["walk", "feeding", "grooming", "meds", "enrichment"],
                },
                "duration": {"type": "integer", "description": "Duration in minutes"},
                "priority": {"type": "string", "enum": ["high", "medium", "low"]},
                "frequency": {"type": "string", "enum": ["daily", "weekly", "monthly"]},
            },
            "required": ["pet_name", "task_name", "category", "duration", "priority", "frequency"],
        },
    },
    {
        "name": "generate_schedule",
        "description": "Generate today's care schedule. Always call this after adding pets and tasks.",
        "input_schema": {
            "type": "object",
            "properties": {},
            "required": [],
        },
    },
]

_SYSTEM_PROMPT = """You are PawPal+, an AI assistant that helps pet owners plan their daily pet care schedule.

When users describe their situation, proactively set up their pets and tasks — don't ask for every detail. Use these defaults:
- Walks: 20 min, high priority, daily
- Feeding: 10 min, high priority, daily
- Grooming: 15 min, medium priority, weekly
- Meds/supplements: 5 min, high priority, daily
- Enrichment/play: 20 min, low priority, daily

Always call generate_schedule at the end so the user can see their plan. Keep responses brief and conversational."""


class PawPalAgent:
    def __init__(self, owner: Owner):
        self.owner = owner
        self.client = anthropic.Anthropic()
        self.history = []

    def _execute_tool(self, name: str, tool_input: dict) -> str:
        if name == "get_current_state":
            if not self.owner.pets:
                return "No pets registered yet."
            lines = []
            for pet in self.owner.pets:
                active = [t for t in pet.tasks if not t.completed]
                task_str = (
                    ", ".join(f"{t.name} ({t.duration}min, {t.priority})" for t in active)
                    or "no tasks"
                )
                needs = ", ".join(pet.get_special_needs()) or "none"
                lines.append(
                    f"{pet.name} ({pet.species}, age {pet.age}): "
                    f"tasks=[{task_str}], special_needs=[{needs}]"
                )
            return "\n".join(lines) + f"\nTime budget: {self.owner.available_time} min"

        if name == "add_pet":
            existing = next(
                (p for p in self.owner.pets if p.name.lower() == tool_input["name"].lower()),
                None,
            )
            if existing:
                return f"Pet '{tool_input['name']}' already exists."
            pet = Pet(
                name=tool_input["name"],
                species=tool_input["species"],
                breed=tool_input.get("breed", "Unknown"),
                age=tool_input.get("age", 0),
            )
            for need in tool_input.get("special_needs", []):
                pet.add_special_need(need)
            pet.generate_needs_tasks()
            self.owner.add_pet(pet)
            needs_msg = (
                f" Auto-created meds tasks for: {', '.join(pet.get_special_needs())}."
                if pet.get_special_needs()
                else ""
            )
            return f"Added {pet.get_info()}.{needs_msg}"

        if name == "add_task":
            pet_name = tool_input["pet_name"]
            pet = next(
                (p for p in self.owner.pets if p.name.lower() == pet_name.lower()), None
            )
            if pet is None:
                return f"Pet '{pet_name}' not found. Add the pet first."
            if any(t.name.lower() == tool_input["task_name"].lower() for t in pet.tasks):
                return f"Task '{tool_input['task_name']}' already exists for {pet_name}."
            task = Task(
                name=tool_input["task_name"],
                category=tool_input["category"],
                duration=tool_input["duration"],
                priority=tool_input["priority"],
                frequency=tool_input.get("frequency", "daily"),
            )
            pet.add_task(task)
            return (
                f"Added '{task.name}' to {pet.name} "
                f"({task.duration} min, {task.priority}, {task.frequency})."
            )

        if name == "generate_schedule":
            scheduler = Scheduler(self.owner)
            plan = scheduler.generate_plan()
            if not plan:
                return "No tasks are due today, or no pets/tasks exist yet."
            total = sum(t.duration for t in plan)
            budget = self.owner.get_availability()
            lines = [f"Schedule: {total}/{budget} min used"]
            for i, task in enumerate(plan, 1):
                time_str = (
                    task.scheduled_time.strftime("%I:%M %p")
                    if task.scheduled_time
                    else "??"
                )
                pet_name = next(
                    (p.name for p in self.owner.pets if task in p.tasks), "?"
                )
                lines.append(
                    f"  {i}. {time_str} [{task.priority.upper()}] "
                    f"{task.name} — {pet_name} ({task.duration} min)"
                )
            conflicts = scheduler.detect_conflicts()
            if conflicts:
                lines.append(f"⚠ {len(conflicts)} time conflict(s) detected!")
            skipped = [t for t in scheduler.gather_tasks() if t not in plan and not t.completed]
            if skipped:
                lines.append(
                    f"Skipped (didn't fit budget): {', '.join(t.name for t in skipped)}"
                )
            return "\n".join(lines)

        return f"Unknown tool: {name}"

    def chat(self, user_message: str) -> str:
        self.history.append({"role": "user", "content": user_message})

        while True:
            response = self.client.messages.create(
                model="claude-haiku-4-5",
                max_tokens=1024,
                system=[
                    {
                        "type": "text",
                        "text": _SYSTEM_PROMPT,
                        "cache_control": {"type": "ephemeral"},
                    },
                    {
                        "type": "text",
                        "text": (
                            f"Owner: {self.owner.name}, "
                            f"time budget: {self.owner.available_time} min today."
                        ),
                    },
                ],
                tools=TOOLS,
                messages=self.history,
            )

            self.history.append({"role": "assistant", "content": response.content})

            if response.stop_reason == "end_turn":
                for block in response.content:
                    if hasattr(block, "text"):
                        return block.text
                return "Done."

            if response.stop_reason == "tool_use":
                tool_results = []
                for block in response.content:
                    if block.type == "tool_use":
                        result = self._execute_tool(block.name, block.input)
                        tool_results.append(
                            {
                                "type": "tool_result",
                                "tool_use_id": block.id,
                                "content": result,
                            }
                        )
                self.history.append({"role": "user", "content": tool_results})
            else:
                break

        return "Something went wrong with the AI response."

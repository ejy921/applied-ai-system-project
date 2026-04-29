import os
from google import genai
from google.genai import types
from pawpal_system import Owner, Pet, Task, Scheduler
import knowledge_base

_SYSTEM_PROMPT = """You are PawPal+, an AI assistant that helps pet owners plan their daily pet care schedule.

When a user mentions a pet, follow this order:
1. Call get_pet_care_info with the pet's species, age, and any conditions to retrieve evidence-based care guidelines.
2. Call add_pet to register the pet.
3. Call add_task for each task — using the retrieved guidelines to set appropriate durations and priorities.
4. Call generate_schedule so the user can see the final plan.

Default task values (override with guidelines when available):
- Walks: 20 min, high priority, daily
- Feeding: 10 min, high priority, daily
- Grooming: 15 min, medium priority, weekly
- Meds/supplements: 5 min, high priority, daily
- Enrichment/play: 20 min, low priority, daily

Keep responses brief and conversational."""

_TOOLS = [
    types.Tool(
        function_declarations=[
            types.FunctionDeclaration(
                name="get_current_state",
                description="Get the current list of pets and their tasks. Call this first to understand what is already set up.",
            ),
            types.FunctionDeclaration(
                name="add_pet",
                description="Add a new pet to the owner's profile.",
                parameters=types.Schema(
                    type=types.Type.OBJECT,
                    properties={
                        "name": types.Schema(type=types.Type.STRING),
                        "species": types.Schema(
                            type=types.Type.STRING,
                            enum=["dog", "cat", "other"],
                        ),
                        "breed": types.Schema(type=types.Type.STRING),
                        "age": types.Schema(type=types.Type.INTEGER),
                        "special_needs": types.Schema(
                            type=types.Type.ARRAY,
                            items=types.Schema(type=types.Type.STRING),
                            description="Medical conditions or medications, e.g. ['insulin']",
                        ),
                    },
                    required=["name", "species", "breed", "age"],
                ),
            ),
            types.FunctionDeclaration(
                name="add_task",
                description=(
                    "Add a care task to a specific pet. "
                    "Defaults: walks=20min/high/daily, feeding=10min/high/daily, "
                    "grooming=15min/medium/weekly, meds=5min/high/daily."
                ),
                parameters=types.Schema(
                    type=types.Type.OBJECT,
                    properties={
                        "pet_name": types.Schema(type=types.Type.STRING),
                        "task_name": types.Schema(type=types.Type.STRING),
                        "category": types.Schema(
                            type=types.Type.STRING,
                            enum=["walk", "feeding", "grooming", "meds", "enrichment"],
                        ),
                        "duration": types.Schema(
                            type=types.Type.INTEGER,
                            description="Duration in minutes",
                        ),
                        "priority": types.Schema(
                            type=types.Type.STRING,
                            enum=["high", "medium", "low"],
                        ),
                        "frequency": types.Schema(
                            type=types.Type.STRING,
                            enum=["daily", "weekly", "monthly"],
                        ),
                    },
                    required=["pet_name", "task_name", "category", "duration", "priority", "frequency"],
                ),
            ),
            types.FunctionDeclaration(
                name="generate_schedule",
                description="Generate today's care schedule. Always call this after adding pets and tasks.",
            ),
            types.FunctionDeclaration(
                name="get_pet_care_info",
                description=(
                    "Retrieve evidence-based care guidelines for a pet from the knowledge base. "
                    "Call this before adding tasks for any new pet so task durations and priorities "
                    "are informed by the pet's species, age, and conditions."
                ),
                parameters=types.Schema(
                    type=types.Type.OBJECT,
                    properties={
                        "species": types.Schema(
                            type=types.Type.STRING,
                            description="Pet species, e.g. 'dog' or 'cat'",
                        ),
                        "age": types.Schema(
                            type=types.Type.INTEGER,
                            description="Pet age in years",
                        ),
                        "conditions": types.Schema(
                            type=types.Type.ARRAY,
                            items=types.Schema(type=types.Type.STRING),
                            description="Medical conditions or special needs, e.g. ['arthritis', 'insulin']",
                        ),
                    },
                    required=["species", "age", "conditions"],
                ),
            ),
        ]
    )
]


class PawPalAgent:
    def __init__(self, owner: Owner):
        self.owner = owner
        self._client = genai.Client(api_key=os.environ.get("GEMINI_API_KEY"))
        self._chat = self._client.chats.create(
            model="gemini-2.0-flash",
            config=types.GenerateContentConfig(
                system_instruction=_SYSTEM_PROMPT,
                tools=_TOOLS,
            ),
        )

    def _execute_tool(self, name: str, args: dict) -> str:
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
                (p for p in self.owner.pets if p.name.lower() == args["name"].lower()),
                None,
            )
            if existing:
                return f"Pet '{args['name']}' already exists."
            pet = Pet(
                name=args["name"],
                species=args["species"],
                breed=args.get("breed", "Unknown"),
                age=args.get("age", 0),
            )
            for need in args.get("special_needs", []):
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
            pet_name = args["pet_name"]
            pet = next(
                (p for p in self.owner.pets if p.name.lower() == pet_name.lower()), None
            )
            if pet is None:
                return f"Pet '{pet_name}' not found. Add the pet first."
            if any(t.name.lower() == args["task_name"].lower() for t in pet.tasks):
                return f"Task '{args['task_name']}' already exists for {pet_name}."
            task = Task(
                name=args["task_name"],
                category=args["category"],
                duration=args["duration"],
                priority=args["priority"],
                frequency=args.get("frequency", "daily"),
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
            skipped = [
                t for t in scheduler.gather_tasks() if t not in plan and not t.completed
            ]
            if skipped:
                lines.append(
                    f"Skipped (didn't fit budget): {', '.join(t.name for t in skipped)}"
                )
            return "\n".join(lines)

        if name == "get_pet_care_info":
            return knowledge_base.retrieve(
                species=args.get("species", ""),
                age=args.get("age", 0),
                conditions=args.get("conditions", []),
            )

        return f"Unknown tool: {name}"

    def chat(self, user_message: str) -> str:
        response = self._chat.send_message(user_message)

        while True:
            fn_calls = [
                p for p in response.candidates[0].content.parts
                if p.function_call and p.function_call.name
            ]

            if not fn_calls:
                text_parts = [
                    p.text for p in response.candidates[0].content.parts
                    if p.text
                ]
                return " ".join(text_parts) if text_parts else "Done."

            results = []
            for part in fn_calls:
                result = self._execute_tool(
                    part.function_call.name,
                    dict(part.function_call.args),
                )
                results.append(
                    types.Part(
                        function_response=types.FunctionResponse(
                            name=part.function_call.name,
                            response={"result": result},
                        )
                    )
                )

            response = self._chat.send_message(results)

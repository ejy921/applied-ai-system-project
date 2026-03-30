from dataclasses import dataclass, field

PRIORITY_RANK = {"high": 0, "medium": 1, "low": 2}


@dataclass
class Task:
    """Represents a single pet-care activity."""
    name: str
    category: str  # walk, feeding, grooming, meds, enrichment
    duration: int  # minutes
    priority: str  # high, medium, low
    frequency: str = "daily"  # daily, weekly, etc.
    completed: bool = False

    def edit_task(self, **kwargs):
        """Update one or more task attributes by keyword."""
        for key, value in kwargs.items():
            if hasattr(self, key):
                setattr(self, key, value)

    def get_task(self) -> dict:
        """Return a dictionary snapshot of the task's attributes."""
        return {
            "name": self.name,
            "category": self.category,
            "duration": self.duration,
            "priority": self.priority,
            "frequency": self.frequency,
            "completed": self.completed,
        }

    def mark_complete(self):
        """Mark the task as completed."""
        self.completed = True


@dataclass
class Pet:
    """Stores pet details and owns a list of tasks."""
    name: str
    species: str
    breed: str
    age: int
    special_needs: list[str] = field(default_factory=list)
    tasks: list[Task] = field(default_factory=list)

    def get_info(self) -> str:
        """Return a formatted summary string of the pet."""
        return f"{self.name} ({self.species}, {self.breed}, age {self.age})"

    def add_special_need(self, need: str):
        """Add a special need if it isn't already listed."""
        if need not in self.special_needs:
            self.special_needs.append(need)

    def get_special_needs(self) -> list[str]:
        """Return a copy of the pet's special needs list."""
        return list(self.special_needs)

    def add_task(self, task: Task):
        """Append a task to this pet's task list."""
        self.tasks.append(task)

    def get_tasks(self) -> list[Task]:
        """Return a copy of this pet's task list."""
        return list(self.tasks)


@dataclass
class Owner:
    """Manages multiple pets and provides access to all their tasks."""
    name: str
    available_time: int  # minutes per day
    preferences: list[str] = field(default_factory=list)
    pets: list[Pet] = field(default_factory=list)

    def set_availability(self, minutes: int):
        """Set the owner's daily available time in minutes."""
        self.available_time = minutes

    def get_availability(self) -> int:
        """Return the owner's daily available time in minutes."""
        return self.available_time

    def add_preference(self, preference: str):
        """Add a care preference if it isn't already listed."""
        if preference not in self.preferences:
            self.preferences.append(preference)

    def get_preferences(self) -> list[str]:
        """Return a copy of the owner's preference list."""
        return list(self.preferences)

    def add_pet(self, pet: Pet):
        """Register a pet under this owner."""
        self.pets.append(pet)

    def get_all_tasks(self) -> list[Task]:
        """Aggregate and return tasks from all owned pets."""
        all_tasks = []
        for pet in self.pets:
            all_tasks.extend(pet.get_tasks())
        return all_tasks


class Scheduler:
    """The brain — retrieves, organizes, and manages tasks across all pets."""

    def __init__(self, owner: Owner):
        self.owner = owner
        self.plan: list[Task] = []

    def gather_tasks(self) -> list[Task]:
        """Collect all tasks from every pet the owner has."""
        return self.owner.get_all_tasks()

    def generate_plan(self) -> list[Task]:
        """Build a prioritized schedule that fits the owner's time budget."""
        all_tasks = [t for t in self.gather_tasks() if not t.completed]
        # Sort by priority (high first), then by duration (shorter first)
        all_tasks.sort(key=lambda t: (PRIORITY_RANK.get(t.priority, 99), t.duration))

        budget = self.owner.get_availability()
        self.plan = []
        used = 0
        for task in all_tasks:
            if used + task.duration <= budget:
                self.plan.append(task)
                used += task.duration
        return list(self.plan)

    def get_plan_summary(self) -> str:
        """Return a numbered, formatted list of scheduled tasks."""
        if not self.plan:
            return "No plan generated yet. Call generate_plan() first."
        total = sum(t.duration for t in self.plan)
        budget = self.owner.get_availability()
        lines = [f"Plan for {self.owner.name} — {total}/{budget} min used"]
        for i, task in enumerate(self.plan, 1):
            lines.append(f"  {i}. [{task.priority.upper()}] {task.name} ({task.duration} min)")
        return "\n".join(lines)

    def explain_plan(self) -> str:
        """Explain why each task was included and list any that were skipped."""
        if not self.plan:
            return "No plan to explain. Call generate_plan() first."
        budget = self.owner.get_availability()
        lines = [f"With {budget} minutes available, here's why each task was chosen:\n"]
        for task in self.plan:
            reason = (
                f"• {task.name} — priority is {task.priority}, takes {task.duration} min, "
                f"scheduled {task.frequency}"
            )
            lines.append(reason)
        skipped = [t for t in self.gather_tasks() if t not in self.plan and not t.completed]
        if skipped:
            lines.append(f"\nSkipped ({len(skipped)} tasks didn't fit the time budget):")
            for task in skipped:
                lines.append(f"  - {task.name} ({task.duration} min, {task.priority})")
        return "\n".join(lines)

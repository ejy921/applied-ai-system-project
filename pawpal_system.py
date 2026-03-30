from dataclasses import dataclass, field
from datetime import date, timedelta

PRIORITY_RANK = {"high": 0, "medium": 1, "low": 2}

FREQUENCY_DAYS = {"daily": 1, "weekly": 7, "monthly": 30}


@dataclass
class Task:
    """Represents a single pet-care activity."""
    name: str
    category: str  # walk, feeding, grooming, meds, enrichment
    duration: int  # minutes
    priority: str  # high, medium, low
    frequency: str = "daily"  # daily, weekly, monthly
    completed: bool = False
    last_completed: date | None = None
    due_date: date | None = None

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
            "last_completed": str(self.last_completed) if self.last_completed else None,
            "due_date": str(self.due_date) if self.due_date else None,
        }

    def mark_complete(self) -> "Task | None":
        """Mark the task as completed and return a new Task for the next occurrence."""
        self.completed = True
        self.last_completed = date.today()
        interval = FREQUENCY_DAYS.get(self.frequency)
        if interval is None:
            return None
        next_due = date.today() + timedelta(days=interval)
        return Task(
            name=self.name,
            category=self.category,
            duration=self.duration,
            priority=self.priority,
            frequency=self.frequency,
            due_date=next_due,
        )

    def is_due_today(self) -> bool:
        """Check if enough days have passed since last completion for this task to be due."""
        if self.last_completed is None:
            return True
        interval = FREQUENCY_DAYS.get(self.frequency, 1)
        return (date.today() - self.last_completed) >= timedelta(days=interval)


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

    def generate_needs_tasks(self):
        """Auto-create a meds task for each special need that lacks one."""
        existing_names = {t.name.lower() for t in self.tasks}
        for need in self.special_needs:
            if need.lower() not in existing_names:
                self.tasks.append(Task(
                    name=need, category="meds",
                    duration=5, priority="high", frequency="daily",
                ))


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

    def mark_task_complete(self, task: Task):
        """Mark a task complete and add its next occurrence to the owning pet."""
        next_task = task.mark_complete()
        if next_task is not None:
            for pet in self.owner.pets:
                if task in pet.tasks:
                    pet.add_task(next_task)
                    return next_task
        return None

    def gather_tasks(self) -> list[Task]:
        """Collect all tasks from every pet the owner has."""
        return self.owner.get_all_tasks()

    def filter_tasks(self, completed: bool | None = None, pet_name: str | None = None) -> list[Task]:
        """Filter tasks by completion status and/or pet name."""
        results = []
        for pet in self.owner.pets:
            if pet_name is not None and pet.name.lower() != pet_name.lower():
                continue
            for task in pet.get_tasks():
                if completed is not None and task.completed != completed:
                    continue
                results.append(task)
        return results

    def sort_tasks(self, tasks: list[Task]) -> list[Task]:
        """Sort tasks by priority (high first), then duration (shortest first)."""
        return sorted(tasks, key=lambda t: (PRIORITY_RANK.get(t.priority, 99), t.duration))

    def generate_plan(self) -> list[Task]:
        """Build a prioritized, fair schedule that fits the owner's time budget."""
        # Per-pet task queues, filtered by due today and not completed
        pet_queues: list[list[Task]] = []
        for pet in self.owner.pets:
            queue = [t for t in pet.get_tasks() if not t.completed and t.is_due_today()]
            queue.sort(key=lambda t: (PRIORITY_RANK.get(t.priority, 99), t.duration))
            if queue:
                pet_queues.append(queue)

        # Round-robin across pets so no pet gets starved
        budget = self.owner.get_availability()
        self.plan = []
        used = 0
        while pet_queues:
            exhausted = []
            for i, queue in enumerate(pet_queues):
                while queue:
                    task = queue.pop(0)
                    if used + task.duration <= budget:
                        self.plan.append(task)
                        used += task.duration
                        break  # move to next pet
                else:
                    exhausted.append(i)
            for i in reversed(exhausted):
                pet_queues.pop(i)
            if not pet_queues:
                break

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

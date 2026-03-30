from datetime import date, timedelta
from pawpal_system import Owner, Pet, Task, Scheduler

# --- Owner ---
owner = Owner(name="Jordan", available_time=60)
owner.add_preference("outdoor activities")

# --- Pets (tasks added out of order on purpose) ---
mochi = Pet(name="Mochi", species="dog", breed="Shiba Inu", age=3)
mochi.add_special_need("joint supplement")
mochi.add_task(Task(name="Brush coat", category="grooming", duration=15, priority="low"))
mochi.add_task(Task(name="Morning walk", category="walk", duration=25, priority="high"))
mochi.add_task(Task(name="Breakfast", category="feeding", duration=10, priority="high"))

whiskers = Pet(name="Whiskers", species="cat", breed="Tabby", age=5)
whiskers.add_task(Task(name="Play with laser", category="enrichment", duration=15, priority="medium"))
whiskers.add_task(Task(name="Feed wet food", category="feeding", duration=5, priority="high"))
whiskers.add_task(Task(
    name="Flea medication", category="meds", duration=5, priority="high",
    frequency="weekly", last_completed=date.today() - timedelta(days=3),
))

# Auto-generate tasks from special needs
mochi.generate_needs_tasks()
whiskers.generate_needs_tasks()

owner.add_pet(mochi)
owner.add_pet(whiskers)

# --- Schedule ---
scheduler = Scheduler(owner)
scheduler.generate_plan()

print("=" * 40)
print("       Today's Schedule")
print("=" * 40)
print(scheduler.get_plan_summary())
print()
print(scheduler.explain_plan())

# --- Mark tasks complete via Scheduler to demo auto-recurrence ---
walk_task = mochi.tasks[1]  # Morning walk (daily)
next_walk = scheduler.mark_task_complete(walk_task)

print()
print("=" * 40)
print("  Auto-Recurrence Demo")
print("=" * 40)
print(f"\nCompleted: {walk_task.name} (daily)")
print(f"  -> Next occurrence auto-created, due: {next_walk.due_date}")

feed_task = whiskers.tasks[1]  # Feed wet food (daily)
next_feed = scheduler.mark_task_complete(feed_task)
print(f"\nCompleted: {feed_task.name} (daily)")
print(f"  -> Next occurrence auto-created, due: {next_feed.due_date}")

print(f"\nMochi now has {len(mochi.tasks)} tasks (was 4, +1 from recurrence)")
print(f"Whiskers now has {len(whiskers.tasks)} tasks (was 3, +1 from recurrence)")

# --- Filter & Sort demos ---
print()
print("=" * 40)
print("  Filtering & Sorting Demo")
print("=" * 40)

print("\n-- Incomplete tasks (all pets) --")
for t in scheduler.sort_tasks(scheduler.filter_tasks(completed=False)):
    print(f"  [{t.priority.upper()}] {t.name} ({t.duration} min)")

print("\n-- Completed tasks (all pets) --")
for t in scheduler.filter_tasks(completed=True):
    print(f"  [DONE] {t.name}")

print("\n-- Whiskers' tasks only (sorted) --")
for t in scheduler.sort_tasks(scheduler.filter_tasks(pet_name="Whiskers")):
    print(f"  [{t.priority.upper()}] {t.name} ({t.duration} min)")

print("\n-- Mochi's incomplete tasks (sorted) --")
for t in scheduler.sort_tasks(scheduler.filter_tasks(completed=False, pet_name="Mochi")):
    print(f"  [{t.priority.upper()}] {t.name} ({t.duration} min)")

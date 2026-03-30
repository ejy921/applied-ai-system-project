from pawpal_system import Owner, Pet, Task, Scheduler

# --- Owner ---
owner = Owner(name="Jordan", available_time=60)
owner.add_preference("outdoor activities")

# --- Pets ---
mochi = Pet(name="Mochi", species="dog", breed="Shiba Inu", age=3)
mochi.add_special_need("joint supplement")
mochi.add_task(Task(name="Morning walk", category="walk", duration=25, priority="high"))
mochi.add_task(Task(name="Breakfast", category="feeding", duration=10, priority="high"))
mochi.add_task(Task(name="Brush coat", category="grooming", duration=15, priority="low"))

whiskers = Pet(name="Whiskers", species="cat", breed="Tabby", age=5)
whiskers.add_task(Task(name="Feed wet food", category="feeding", duration=5, priority="high"))
whiskers.add_task(Task(name="Play with laser", category="enrichment", duration=15, priority="medium"))
whiskers.add_task(Task(name="Flea medication", category="meds", duration=5, priority="high", frequency="weekly"))

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

import os
import streamlit as st
from pawpal_system import Owner, Pet, Task, Scheduler

st.set_page_config(page_title="PawPal+", page_icon="🐾", layout="centered")

st.title("🐾 PawPal+")
st.caption("A smart pet care planning assistant")

st.divider()

# --- Persist core objects across reruns ---
if "owner" not in st.session_state:
    st.session_state.owner = Owner(name="Jordan", available_time=60)
if "scheduler" not in st.session_state:
    st.session_state.scheduler = None
if "agent" not in st.session_state:
    st.session_state.agent = None
if "chat_messages" not in st.session_state:
    st.session_state.chat_messages = []

owner = st.session_state.owner

# =====================
# OWNER SETUP
# =====================
st.subheader("Owner Setup")
col_name, col_time = st.columns(2)
with col_name:
    owner_name = st.text_input("Owner name", value=owner.name)
    owner.name = owner_name
with col_time:
    available_time = st.number_input(
        "Available time (minutes)", min_value=1, max_value=480,
        value=owner.available_time,
    )
    owner.set_availability(int(available_time))

st.divider()

# =====================
# AI ASSISTANT
# =====================
st.subheader("AI Assistant")
st.caption("Describe your pets and their care needs in plain English")

_api_key = os.environ.get("GEMINI_API_KEY", "")
if not _api_key:
    st.warning(
        "Set the `GEMINI_API_KEY` environment variable to enable the AI assistant. "
        "You can still use the manual forms below."
    )
else:
    from agent import PawPalAgent

    if st.session_state.agent is None:
        st.session_state.agent = PawPalAgent(owner)

    for msg in st.session_state.chat_messages:
        with st.chat_message(msg["role"]):
            st.markdown(msg["content"])

    if user_input := st.chat_input("e.g. 'My dog Max needs a walk and feeding, I have 45 minutes'"):
        st.session_state.chat_messages.append({"role": "user", "content": user_input})
        with st.chat_message("user"):
            st.markdown(user_input)
        with st.chat_message("assistant"):
            with st.spinner("Planning..."):
                reply = st.session_state.agent.chat(user_input)
            st.markdown(reply)
        st.session_state.chat_messages.append({"role": "assistant", "content": reply})
        st.rerun()

st.divider()

# =====================
# ADD A PET
# =====================
st.subheader("Pets")
pet_col1, pet_col2, pet_col3 = st.columns(3)
with pet_col1:
    pet_name = st.text_input("Pet name", value="Mochi")
with pet_col2:
    species = st.selectbox("Species", ["dog", "cat", "other"])
with pet_col3:
    breed = st.text_input("Breed", value="Shiba Inu")

col_age, col_needs = st.columns(2)
with col_age:
    pet_age = st.number_input("Age (years)", min_value=0, max_value=30, value=3)
with col_needs:
    special_needs = st.text_input("Special needs (comma-separated)", value="")

if st.button("Add pet"):
    new_pet = Pet(name=pet_name, species=species, breed=breed, age=int(pet_age))
    for need in [n.strip() for n in special_needs.split(",") if n.strip()]:
        new_pet.add_special_need(need)
    new_pet.generate_needs_tasks()
    owner.add_pet(new_pet)
    st.success(f"Added {new_pet.get_info()}")
    if new_pet.get_special_needs():
        st.info(f"Auto-created meds tasks for: {', '.join(new_pet.get_special_needs())}")

if owner.pets:
    pet_data = []
    for pet in owner.pets:
        pet_data.append({
            "Name": pet.name,
            "Species": pet.species,
            "Breed": pet.breed,
            "Age": pet.age,
            "Special Needs": ", ".join(pet.get_special_needs()) or "None",
            "Tasks": len(pet.tasks),
        })
    st.table(pet_data)
else:
    st.info("No pets yet. Add one above.")

st.divider()

# =====================
# ADD A TASK
# =====================
st.subheader("Tasks")
if owner.pets:
    pet_names = [p.name for p in owner.pets]
    selected_pet_name = st.selectbox("Assign to pet", pet_names)

    col1, col2 = st.columns(2)
    with col1:
        task_title = st.text_input("Task title", value="Morning walk")
        category = st.selectbox("Category", ["walk", "feeding", "grooming", "meds", "enrichment"])
    with col2:
        duration = st.number_input("Duration (minutes)", min_value=1, max_value=240, value=20)
        priority = st.selectbox("Priority", ["high", "medium", "low"])
    frequency = st.selectbox("Frequency", ["daily", "weekly", "monthly"])

    if st.button("Add task"):
        selected_pet = next(p for p in owner.pets if p.name == selected_pet_name)
        new_task = Task(
            name=task_title, category=category,
            duration=int(duration), priority=priority, frequency=frequency,
        )
        selected_pet.add_task(new_task)
        st.success(f"Added '{task_title}' to {selected_pet.name}")

    # Show all tasks sorted by priority
    scheduler = Scheduler(owner)
    all_tasks = scheduler.sort_tasks(
        [t for t in owner.get_all_tasks() if not t.completed]
    )
    if all_tasks:
        st.markdown("**All active tasks** (sorted by priority)")
        task_rows = []
        for t in all_tasks:
            # Find which pet owns this task
            pet_owner = ""
            for p in owner.pets:
                if t in p.tasks:
                    pet_owner = p.name
                    break
            task_rows.append({
                "Pet": pet_owner,
                "Task": t.name,
                "Category": t.category,
                "Duration": f"{t.duration} min",
                "Priority": t.priority.upper(),
                "Frequency": t.frequency,
            })
        st.table(task_rows)
    else:
        st.info("No active tasks. Add some above.")
else:
    st.info("Add a pet first, then you can assign tasks.")

st.divider()

# =====================
# GENERATE SCHEDULE
# =====================
st.subheader("Today's Schedule")
if st.button("Generate schedule"):
    if not owner.get_all_tasks():
        st.warning("No tasks to schedule. Add pets and tasks first.")
    else:
        scheduler = Scheduler(owner)
        plan = scheduler.generate_plan()
        st.session_state.scheduler = scheduler

        if not plan:
            st.warning("No tasks are due today or all tasks are completed.")
        else:
            # Schedule table
            total = sum(t.duration for t in plan)
            budget = owner.get_availability()
            st.success(f"Schedule generated — {total}/{budget} minutes used")

            plan_rows = []
            for i, task in enumerate(plan, 1):
                time_str = task.scheduled_time.strftime("%I:%M %p") if task.scheduled_time else "—"
                plan_rows.append({
                    "#": i,
                    "Time": time_str,
                    "Task": task.name,
                    "Duration": f"{task.duration} min",
                    "Priority": task.priority.upper(),
                    "Category": task.category,
                })
            st.table(plan_rows)

            # Conflict detection
            conflicts = scheduler.detect_conflicts()
            if conflicts:
                st.warning(f"Scheduling conflicts detected ({len(conflicts)}):")
                for a, b in conflicts:
                    st.write(f"  - **{a.name}** overlaps with **{b.name}**")
            else:
                st.success("No scheduling conflicts detected.")

            # Explanation
            with st.expander("Why these tasks?"):
                for task in plan:
                    st.markdown(
                        f"- **{task.name}** — priority is {task.priority}, "
                        f"takes {task.duration} min, scheduled {task.frequency}"
                    )

            # Skipped tasks
            skipped = [t for t in scheduler.gather_tasks() if t not in plan and not t.completed]
            if skipped:
                with st.expander(f"Skipped tasks ({len(skipped)})"):
                    st.warning("These tasks didn't fit the time budget:")
                    for task in skipped:
                        st.write(f"- {task.name} ({task.duration} min, {task.priority})")

st.divider()

# =====================
# FILTER & COMPLETE
# =====================
if owner.pets and owner.get_all_tasks():
    st.subheader("Filter & Manage Tasks")

    filter_col1, filter_col2 = st.columns(2)
    with filter_col1:
        filter_pet = st.selectbox(
            "Filter by pet", ["All pets"] + [p.name for p in owner.pets],
            key="filter_pet",
        )
    with filter_col2:
        filter_status = st.selectbox(
            "Filter by status", ["Incomplete", "Completed", "All"],
            key="filter_status",
        )

    scheduler = Scheduler(owner)
    pet_filter = None if filter_pet == "All pets" else filter_pet
    status_filter = {"Incomplete": False, "Completed": True, "All": None}[filter_status]
    filtered = scheduler.sort_tasks(
        scheduler.filter_tasks(completed=status_filter, pet_name=pet_filter)
    )

    if filtered:
        for t in filtered:
            pet_label = ""
            for p in owner.pets:
                if t in p.tasks:
                    pet_label = p.name
                    break
            status = "Done" if t.completed else t.priority.upper()
            st.write(f"[{status}] **{t.name}** — {pet_label} — {t.duration} min, {t.frequency}")
    else:
        st.info("No tasks match the current filter.")

    # Mark complete
    st.markdown("---")
    incomplete = [t for t in owner.get_all_tasks() if not t.completed]
    if incomplete:
        task_options = [f"{t.name} ({t.duration} min)" for t in incomplete]
        selected_complete = st.selectbox("Mark a task complete", task_options, key="complete_task")
        if st.button("Mark complete"):
            idx = task_options.index(selected_complete)
            task_to_complete = incomplete[idx]
            scheduler = Scheduler(owner)
            next_task = scheduler.mark_task_complete(task_to_complete)
            st.success(f"Completed: {task_to_complete.name}")
            if next_task:
                st.info(f"Next occurrence auto-created, due: {next_task.due_date}")

import streamlit as st
from pawpal_system import Owner, Pet, Task, Scheduler

st.set_page_config(page_title="PawPal+", page_icon="🐾", layout="centered")

st.title("🐾 PawPal+")

st.markdown(
    """
Welcome to the PawPal+ starter app.

This file is intentionally thin. It gives you a working Streamlit app so you can start quickly,
but **it does not implement the project logic**. Your job is to design the system and build it.

Use this app as your interactive demo once your backend classes/functions exist.
"""
)

with st.expander("Scenario", expanded=True):
    st.markdown(
        """
**PawPal+** is a pet care planning assistant. It helps a pet owner plan care tasks
for their pet(s) based on constraints like time, priority, and preferences.

You will design and implement the scheduling logic and connect it to this Streamlit UI.
"""
    )

with st.expander("What you need to build", expanded=True):
    st.markdown(
        """
At minimum, your system should:
- Represent pet care tasks (what needs to happen, how long it takes, priority)
- Represent the pet and the owner (basic info and preferences)
- Build a plan/schedule for a day that chooses and orders tasks based on constraints
- Explain the plan (why each task was chosen and when it happens)
"""
    )

st.divider()

# --- Persist core objects across reruns ---
if "owner" not in st.session_state:
    st.session_state.owner = Owner(name="Jordan", available_time=60)

st.subheader("Owner Setup")
owner_name = st.text_input("Owner name", value=st.session_state.owner.name)
st.session_state.owner.name = owner_name

available_time = st.number_input(
    "Available time (minutes)", min_value=1, max_value=480,
    value=st.session_state.owner.available_time,
)
st.session_state.owner.set_availability(int(available_time))

# --- Add a Pet ---
st.markdown("### Add a Pet")
pet_col1, pet_col2, pet_col3 = st.columns(3)
with pet_col1:
    pet_name = st.text_input("Pet name", value="Mochi")
with pet_col2:
    species = st.selectbox("Species", ["dog", "cat", "other"])
with pet_col3:
    breed = st.text_input("Breed", value="Shiba Inu")
pet_age = st.number_input("Age (years)", min_value=0, max_value=30, value=3)

if st.button("Add pet"):
    new_pet = Pet(name=pet_name, species=species, breed=breed, age=int(pet_age))
    st.session_state.owner.add_pet(new_pet)
    st.success(f"Added {new_pet.get_info()}")

if st.session_state.owner.pets:
    st.write("Registered pets:")
    for pet in st.session_state.owner.pets:
        st.write(f"- {pet.get_info()}")
else:
    st.info("No pets yet. Add one above.")

st.divider()

# --- Add a Task to a Pet ---
st.markdown("### Add a Task")
if st.session_state.owner.pets:
    pet_names = [p.name for p in st.session_state.owner.pets]
    selected_pet_name = st.selectbox("Assign to pet", pet_names)

    col1, col2, col3 = st.columns(3)
    with col1:
        task_title = st.text_input("Task title", value="Morning walk")
    with col2:
        duration = st.number_input("Duration (minutes)", min_value=1, max_value=240, value=20)
    with col3:
        priority = st.selectbox("Priority", ["low", "medium", "high"], index=2)
    category = st.selectbox("Category", ["walk", "feeding", "grooming", "meds", "enrichment"])

    if st.button("Add task"):
        selected_pet = next(p for p in st.session_state.owner.pets if p.name == selected_pet_name)
        new_task = Task(
            name=task_title, category=category,
            duration=int(duration), priority=priority,
        )
        selected_pet.add_task(new_task)
        st.success(f"Added '{task_title}' to {selected_pet.name}")

    all_tasks = st.session_state.owner.get_all_tasks()
    if all_tasks:
        st.write("All tasks:")
        st.table([t.get_task() for t in all_tasks])
else:
    st.info("Add a pet first, then you can assign tasks.")

st.divider()

# --- Generate Schedule ---
st.subheader("Build Schedule")
if st.button("Generate schedule"):
    if not st.session_state.owner.get_all_tasks():
        st.warning("No tasks to schedule. Add pets and tasks first.")
    else:
        scheduler = Scheduler(st.session_state.owner)
        scheduler.generate_plan()
        st.text(scheduler.get_plan_summary())
        with st.expander("Why these tasks?"):
            st.text(scheduler.explain_plan())

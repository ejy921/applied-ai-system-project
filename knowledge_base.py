from __future__ import annotations

ENTRIES = [
    # --- Dogs by age ---
    {
        "tags": ["dog", "puppy"],
        "title": "Puppy Care (under 1 year)",
        "content": (
            "Puppies need 3-4 small meals per day instead of 1-2. "
            "Short, frequent play sessions (5 min per month of age, up to 30 min) are better than long walks to protect developing joints. "
            "Socialization and basic training sessions (10-15 min, daily) are critical at this stage. "
            "Puppies need more sleep than adult dogs — 16-18 hours per day is normal."
        ),
    },
    {
        "tags": ["dog", "adult"],
        "title": "Adult Dog Care (1-6 years)",
        "content": (
            "Adult dogs generally need 2 meals per day. "
            "Most breeds need 30-60 minutes of exercise daily — walks, fetch, or free play. "
            "Teeth brushing 2-3 times per week significantly reduces dental disease risk. "
            "Annual vet checkup recommended."
        ),
    },
    {
        "tags": ["dog", "senior"],
        "title": "Senior Dog Care (7+ years)",
        "content": (
            "Senior dogs tire more easily — shorter, more frequent walks (15-20 min, 2-3 times daily) are better than one long walk. "
            "Avoid high-impact activities like jumping or running on hard surfaces. "
            "Feed a senior-formula food in 2 smaller meals. "
            "Dental hygiene becomes more important — brush teeth daily if possible. "
            "Vet checkups every 6 months instead of annually. "
            "Watch for signs of cognitive decline, stiffness, or reduced appetite."
        ),
    },
    # --- Cats by age ---
    {
        "tags": ["cat", "kitten"],
        "title": "Kitten Care (under 1 year)",
        "content": (
            "Kittens need 3-4 small meals per day of kitten-formula food. "
            "Interactive play sessions (10-15 min, 2-3 times daily) build coordination and prevent boredom. "
            "Litter box should be cleaned at least once daily — kittens are sensitive to dirty boxes. "
            "Begin grooming habits early so the cat tolerates brushing as an adult."
        ),
    },
    {
        "tags": ["cat", "adult"],
        "title": "Adult Cat Care (1-10 years)",
        "content": (
            "Adult cats do well with 2 measured meals per day to prevent obesity. "
            "Interactive play (wand toys, laser) for 10-15 min once or twice daily satisfies hunting instincts. "
            "Brush short-haired cats weekly, long-haired cats daily to reduce hairballs. "
            "Clean litter box at least once daily."
        ),
    },
    {
        "tags": ["cat", "senior"],
        "title": "Senior Cat Care (10+ years)",
        "content": (
            "Senior cats may need more frequent, smaller meals (2-3 per day). "
            "Gentle interactive play is still important but keep sessions short (5-10 min). "
            "Provide easy access to litter box — low-sided or ramp-equipped for cats with mobility issues. "
            "Brush regularly as senior cats groom themselves less effectively. "
            "Vet checkups every 6 months."
        ),
    },
    # --- Conditions ---
    {
        "tags": ["joint", "arthritis", "hip dysplasia", "mobility", "limping"],
        "title": "Joint Issues / Arthritis",
        "content": (
            "Reduce walk duration by 30-50% and keep pace slow — 10-15 min gentle walks 2-3 times daily are better than one long walk. "
            "Avoid stairs, jumping, or running on hard surfaces. "
            "Joint supplements (glucosamine, fish oil) given daily can reduce inflammation — always 5 min, high priority. "
            "Provide orthopedic bedding. "
            "Hydrotherapy or gentle swimming is ideal exercise for arthritic pets."
        ),
    },
    {
        "tags": ["insulin", "diabetes", "diabetic"],
        "title": "Diabetes / Insulin Management",
        "content": (
            "Insulin injections must be given at exactly the same time every day, ideally with meals — mark as high priority, daily, 5 min. "
            "Feed at consistent times (2 meals, 12 hours apart) to stabilize blood sugar. "
            "Monitor for hypoglycemia signs: weakness, trembling, disorientation. "
            "Moderate, consistent exercise is beneficial — avoid intense or irregular activity that spikes glucose. "
            "Vet rechecks every 1-3 months while regulating dose."
        ),
    },
    {
        "tags": ["dental", "teeth", "gum", "periodontal"],
        "title": "Dental Disease",
        "content": (
            "Daily tooth brushing is the single most effective preventive measure — 5-10 min, high priority. "
            "Use pet-safe toothpaste only (human toothpaste is toxic to pets). "
            "Dental chews can supplement brushing but don't replace it. "
            "Signs of dental pain: dropping food, pawing at mouth, bad breath, reduced appetite. "
            "Professional dental cleaning under anesthesia may be needed annually."
        ),
    },
    {
        "tags": ["overweight", "obese", "weight", "diet"],
        "title": "Weight Management",
        "content": (
            "Measure food portions precisely — even a small daily excess causes significant weight gain over months. "
            "Increase exercise gradually: add 5 min per walk each week. "
            "Replace high-calorie treats with low-calorie alternatives (carrots for dogs, cooked chicken for cats). "
            "Weigh pet monthly and adjust portions accordingly. "
            "Target 1-2% body weight loss per week."
        ),
    },
    {
        "tags": ["anxiety", "stress", "fear", "separation"],
        "title": "Anxiety / Separation Stress",
        "content": (
            "Enrichment activities (puzzle feeders, scent games, interactive toys) reduce anxiety — 20 min daily. "
            "Consistent daily routine is the most effective anxiety reducer — keep feeding, walk, and play times predictable. "
            "Short, positive training sessions build confidence (10-15 min daily). "
            "Avoid long stretches alone — if unavoidable, provide background sound (TV or radio). "
            "Calming supplements (melatonin, L-theanine) may help — discuss with vet."
        ),
    },
    {
        "tags": ["kidney", "renal", "ckd"],
        "title": "Kidney Disease (CKD)",
        "content": (
            "Fresh water must always be available — hydration is critical for kidney function. "
            "Feed a prescription renal diet as directed by vet — do not free-feed. "
            "Smaller, more frequent meals (3 per day) are easier on the kidneys. "
            "Medication administration times are critical — mark as high priority, daily. "
            "Vet rechecks every 1-3 months to monitor kidney values."
        ),
    },
    {
        "tags": ["supplement", "medication", "medicine", "meds", "prescription"],
        "title": "General Medication / Supplements",
        "content": (
            "All prescribed medications should be marked high priority and administered at consistent times daily. "
            "Set a 5-min task for each medication. "
            "Never skip doses or adjust dosing without vet guidance. "
            "Some medications must be given with food — coordinate med tasks with feeding tasks."
        ),
    },
]


def retrieve(species: str, age: int, conditions: list[str]) -> str:
    """Return the most relevant care guidelines for this pet as a single string."""
    query_tags: set[str] = set()

    query_tags.add(species.lower())

    if species.lower() == "dog":
        if age < 1:
            query_tags.add("puppy")
        elif age < 7:
            query_tags.add("adult")
        else:
            query_tags.add("senior")
    elif species.lower() == "cat":
        if age < 1:
            query_tags.add("kitten")
        elif age < 10:
            query_tags.add("adult")
        else:
            query_tags.add("senior")

    for condition in conditions:
        query_tags.update(condition.lower().split())

    matched = []
    for entry in ENTRIES:
        if query_tags.intersection(entry["tags"]):
            matched.append(entry)

    if not matched:
        return "No specific guidelines found. Use standard care defaults."

    sections = [f"**{e['title']}**\n{e['content']}" for e in matched]
    return "\n\n".join(sections)

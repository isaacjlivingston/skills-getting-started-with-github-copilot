"""
High School Management System API

A super simple FastAPI application that allows students to view and sign up
for extracurricular activities at Mergington High School.
"""

from fastapi import FastAPI, HTTPException
from fastapi.staticfiles import StaticFiles
from fastapi.responses import RedirectResponse
import os
from pathlib import Path

app = FastAPI(title="Mergington High School API",
              description="API for viewing and signing up for extracurricular activities")

# Mount the static files directory
current_dir = Path(__file__).parent
app.mount("/static", StaticFiles(directory=os.path.join(Path(__file__).parent,
          "static")), name="static")

# In-memory activity database
activities = {
    "Chess Club": {
        "description": "Learn strategies and compete in chess tournaments",
        "schedule": "Fridays, 3:30 PM - 5:00 PM",
        "max_participants": 12,
        "participants": ["michael@mergington.edu", "daniel@mergington.edu"]
    },
    "Programming Class": {
        "description": "Learn programming fundamentals and build software projects",
        "schedule": "Tuesdays and Thursdays, 3:30 PM - 4:30 PM",
        "max_participants": 20,
        "participants": ["emma@mergington.edu", "sophia@mergington.edu"]
    },
    "Gym Class": {
        "description": "Physical education and sports activities",
        "schedule": "Mondays, Wednesdays, Fridays, 2:00 PM - 3:00 PM",
        "max_participants": 30,
        "participants": ["john@mergington.edu", "olivia@mergington.edu"]
    },
    "Basketball": {
        "description": "Practice team drills, conditioning, and competitive play",
        "schedule": "Mondays, Tuesdays, Thursdays, 3:30 PM - 5:30 PM",
        "max_participants": 15,
        "participants": ["liam@mergington.edu", "ava@mergington.edu"]
    },
    "Soccer": {
        "description": "Develop soccer skills through practice, scrimmages, and matches",
        "schedule": "Mondays, Wednesdays, Fridays, 3:45 PM - 5:15 PM",
        "max_participants": 18,
        "participants": ["noah@mergington.edu", "mia@mergington.edu"]
    },
    "Drama Club": {
        "description": "Rehearse plays, build stage presence, and perform school productions",
        "schedule": "Tuesdays and Thursdays, 3:30 PM - 5:00 PM",
        "max_participants": 25,
        "participants": ["charlotte@mergington.edu", "elijah@mergington.edu"]
    },
    "Art Club": {
        "description": "Explore drawing, painting, and mixed media projects",
        "schedule": "Wednesdays, 3:30 PM - 5:00 PM",
        "max_participants": 16,
        "participants": ["amelia@mergington.edu", "lucas@mergington.edu"]
    },
    "Debate Team": {
        "description": "Practice public speaking, argumentation, and competitive debate",
        "schedule": "Mondays and Thursdays, 3:30 PM - 5:00 PM",
        "max_participants": 14,
        "participants": ["harper@mergington.edu", "henry@mergington.edu"]
    },
    "Science Olympiad": {
        "description": "Prepare for science competitions through labs, study sessions, and team events",
        "schedule": "Tuesdays and Fridays, 3:30 PM - 5:00 PM",
        "max_participants": 18,
        "participants": ["evelyn@mergington.edu", "jackson@mergington.edu"]
    }
}


@app.get("/")
def root():
    return RedirectResponse(url="/static/index.html")


@app.get("/activities")
def get_activities():
    return activities


@app.post("/activities/{activity_name}/signup")
def signup_for_activity(activity_name: str, email: str):
    """Sign up a student for an activity"""
    # Validate activity exists
    if activity_name not in activities:
        raise HTTPException(status_code=404, detail="Activity not found")

    # Get the specific activity
    activity = activities[activity_name]

    normalized_email = email.strip().lower()
    existing_emails = {participant.strip().lower() for participant in activity["participants"]}

    if normalized_email in existing_emails:
        raise HTTPException(status_code=409, detail="Student is already signed up for this activity")

    if len(activity["participants"]) >= activity["max_participants"]:
        raise HTTPException(status_code=400, detail="Activity is full")

    # Add student
    activity["participants"].append(normalized_email)
    return {"message": f"Signed up {normalized_email} for {activity_name}"}


@app.delete("/activities/{activity_name}/signup")
def remove_from_activity(activity_name: str, email: str):
    """Remove a student from an activity"""
    if activity_name not in activities:
        raise HTTPException(status_code=404, detail="Activity not found")

    activity = activities[activity_name]
    normalized_email = email.strip().lower()

    # Normalize stored emails before searching so mixed-case entries are matched correctly
    stored_email = next(
        (p for p in activity["participants"] if p.strip().lower() == normalized_email),
        None,
    )
    if stored_email is None:
        raise HTTPException(status_code=404, detail="Student is not signed up for this activity")

    activity["participants"].remove(stored_email)
    return {"message": f"Removed {normalized_email} from {activity_name}"}

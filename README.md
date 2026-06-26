# DisasterAid — Relief Resource Management Platform

A centralized platform to coordinate disaster relief resources during floods, landslides, and cyclones. Volunteers, NGOs, and authorities can register resources and manage aid distribution. Affected people can submit requests for help.

## Features

- **Role-based access** — Volunteer, NGO, Authority, Affected Person
- **Resource Registry** — Register, track, and allocate relief supplies
- **Aid Requests** — Submit and manage requests sorted by urgency (Critical → Low)
- **Shelter Management** — Live capacity tracking for relief camps
- **Volunteer Coordination** — Assign volunteers to areas and tasks
- **ShaktiDB (SQLite)** — Persistent storage for all data

## Tech Stack

| Layer | Technology |
|-------|-----------|
| Backend | Python 3, Flask |
| Database | ShaktiDB (SQLite via Python) |
| Frontend | HTML5, CSS3, Jinja2 templates |
| OS | Ubuntu (Linux) |
| Version Control | GitHub |
| Editor | VS Code |

## Setup & Run

### 1. Clone / extract the project
```bash
cd disaster_relief
```

### 2. Install dependencies
```bash
pip install -r requirements.txt
```

### 3. Run the application
```bash
python app.py
```

### 4. Open in browser
```
http://localhost:5000
```

The database is auto-created on first run with demo data.

## Demo Accounts

| Role | Email | Password |
|------|-------|----------|
| Authority | admin@relief.gov | admin123 |
| NGO | ngo@redcross.org | ngo123 |
| Volunteer | arjun@vol.com | vol123 |
| Affected | meera@gmail.com | user123 |

## Project Structure

```
disaster_relief/
├── app.py                  # Flask app entry point
├── requirements.txt
├── database/
│   ├── db.py               # Database connection helpers
│   ├── schema.sql          # Table definitions + seed data
│   └── relief.db           # Auto-generated SQLite database
├── routes/
│   ├── auth.py             # Login, Register, Logout
│   └── main.py             # Dashboard, Resources, Requests, Shelters, Volunteers
├── templates/
│   ├── base.html           # Sidebar layout template
│   ├── login.html
│   ├── register.html
│   ├── dashboard.html
│   ├── resources.html
│   ├── add_resource.html
│   ├── requests.html
│   ├── new_request.html
│   ├── shelters.html
│   ├── add_shelter.html
│   └── volunteers.html
└── static/
    └── css/
        └── style.css       # Full UI stylesheet
```

## Database Schema

- **users** — All users with role (volunteer/ngo/authority/affected)
- **resources** — Registered supplies with type, quantity, location, status
- **aid_requests** — Help requests with urgency level and status tracking
- **shelters** — Relief camps with capacity and occupancy data
- **volunteers** — Volunteer profiles with skills and assignment details

## Disaster Types Supported

- 🌊 Flood
- ⛰️ Landslide  
- 🌀 Cyclone
- 🩹 General emergency

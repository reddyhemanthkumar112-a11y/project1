"""
Database management and models for Citizen Complaint Management System.
Uses SQLite for zero-configuration, robust local persistence.
"""

import os
import sqlite3
from datetime import datetime
from typing import Dict, List, Optional, Tuple, Any

DB_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), "complaints.db")

VALID_CATEGORIES = [
    "Roads",
    "Water and drainage",
    "Electricity",
    "Sanitation",
    "Public infrastructure"
]

VALID_STATUSES = [
    "Submitted",
    "In progress",
    "Resolved"
]

DEPARTMENT_MAP = {
    "Roads": "Department of Transportation & Municipal Roads",
    "Water and drainage": "Bureau of Water Supply & Drainage Services",
    "Electricity": "City Energy & Public Lighting Authority",
    "Sanitation": "Waste Management & Sanitation Department",
    "Public infrastructure": "Public Works & Civic Infrastructure Division"
}

NEIGHBORHOODS = [
    "Downtown Central",
    "North Ward",
    "Riverside District",
    "Eastside Suburbs",
    "Westpark Greens",
    "South Industrial Zone"
]

def get_db_connection() -> sqlite3.Connection:
    """Creates a database connection with dict-like row access."""
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON")
    return conn

def init_db(force_reseed: bool = False):
    """Initializes tables and seeds initial data if empty or forced."""
    conn = get_db_connection()
    cursor = conn.cursor()

    if force_reseed:
        cursor.execute("DROP TABLE IF EXISTS complaint_updates")
        cursor.execute("DROP TABLE IF EXISTS complaints")

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS complaints (
            id TEXT PRIMARY KEY,
            category TEXT NOT NULL,
            title TEXT NOT NULL,
            description TEXT NOT NULL,
            location TEXT NOT NULL,
            neighborhood TEXT NOT NULL,
            latitude REAL,
            longitude REAL,
            contact_name TEXT,
            contact_email TEXT,
            contact_phone TEXT,
            photo_url TEXT,
            responsible_department TEXT NOT NULL,
            status TEXT NOT NULL,
            created_at TEXT NOT NULL,
            updated_at TEXT NOT NULL
        )
    """)

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS complaint_updates (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            complaint_id TEXT NOT NULL,
            status TEXT NOT NULL,
            actor TEXT NOT NULL,
            notes TEXT NOT NULL,
            timestamp TEXT NOT NULL,
            FOREIGN KEY (complaint_id) REFERENCES complaints(id) ON DELETE CASCADE
        )
    """)

    conn.commit()

    # Check if empty, seed if so
    cursor.execute("SELECT COUNT(*) AS cnt FROM complaints")
    count = cursor.fetchone()["cnt"]
    if count == 0:
        seed_sample_data(conn)

    conn.close()

def _sample_svg(title: str, category: str, color: str) -> str:
    """Generates an inline SVG data URL for realistic sample complaint images."""
    svg = f"""<svg xmlns="http://www.w3.org/2000/svg" width="600" height="400" viewBox="0 0 600 400">
        <rect width="100%" height="100%" fill="#f1f5f9"/>
        <rect x="20" y="20" width="560" height="360" rx="12" fill="#ffffff" stroke="#cbd5e1" stroke-width="2"/>
        <circle cx="300" cy="160" r="50" fill="{color}" opacity="0.15"/>
        <path d="M280 160h40M300 140v40" stroke="{color}" stroke-width="6" stroke-linecap="round"/>
        <text x="300" y="250" font-family="system-ui, sans-serif" font-size="20" font-weight="bold" fill="#1e293b" text-anchor="middle">{title}</text>
        <text x="300" y="280" font-family="system-ui, sans-serif" font-size="14" fill="#64748b" text-anchor="middle">{category} Field Evidence Photo</text>
        <rect x="230" y="305" width="140" height="26" rx="13" fill="{color}" opacity="0.2"/>
        <text x="300" y="322" font-family="system-ui, sans-serif" font-size="12" font-weight="600" fill="{color}" text-anchor="middle">OFFICIAL ATTACHMENT</text>
    </svg>"""
    import base64
    b64 = base64.b64encode(svg.encode('utf-8')).decode('utf-8')
    return f"data:image/svg+xml;base64,{b64}"

def seed_sample_data(conn: sqlite3.Connection):
    """Inserts realistic sample complaints across all five categories and neighborhoods."""
    cursor = conn.cursor()

    sample_complaints = [
        {
            "id": "CMP-2026-001",
            "category": "Roads",
            "title": "Hazardous deep pothole on Elm Street intersection",
            "description": "Large pothole approximately 2 feet wide and 5 inches deep right after the pedestrian crossing. Multiple vehicles have suffered tire rim damage and cyclists are swerving into oncoming traffic to avoid it.",
            "location": "Corner of Elm St & 4th Avenue, near Central Library",
            "neighborhood": "Downtown Central",
            "latitude": 40.7135,
            "longitude": -74.0055,
            "contact_name": "Sarah Jenkins",
            "contact_email": "s.jenkins@example.com",
            "contact_phone": "(555) 234-8901",
            "photo_url": _sample_svg("Elm St Pothole", "Roads", "#d97706"),
            "responsible_department": DEPARTMENT_MAP["Roads"],
            "status": "In progress",
            "created_at": "2026-10-10 09:30:00",
            "updated_at": "2026-10-11 11:15:00",
            "history": [
                ("Submitted", "Citizen Submission", "Complaint logged by resident via citizen portal.", "2026-10-10 09:30:00"),
                ("In progress", "Field Inspector - Unit 4", "Site inspection verified severe road surface deterioration. Repair crew scheduled for cold-mix asphalt patching.", "2026-10-11 11:15:00")
            ]
        },
        {
            "id": "CMP-2026-002",
            "category": "Water and drainage",
            "title": "Storm drain blockage causing street flooding during rain",
            "description": "Storm drain completely clogged with compacted autumn leaves and street runoff debris. Rainwater is ponding across both travel lanes and spilling onto the pedestrian sidewalk.",
            "location": "742 Evergreen Terrace, near Riverside Park entrance",
            "neighborhood": "Riverside District",
            "latitude": 40.7180,
            "longitude": -74.0120,
            "contact_name": "Marcus Vance",
            "contact_email": "marcus.v@example.com",
            "contact_phone": "(555) 345-6789",
            "photo_url": _sample_svg("Storm Drain Blockage", "Water and drainage", "#0284c7"),
            "responsible_department": DEPARTMENT_MAP["Water and drainage"],
            "status": "Resolved",
            "created_at": "2026-10-08 14:20:00",
            "updated_at": "2026-10-10 16:30:00",
            "history": [
                ("Submitted", "Citizen Submission", "Initial drainage malfunction report submitted.", "2026-10-08 14:20:00"),
                ("In progress", "Drainage Operations", "High-velocity vacuum jetting truck dispatched to clear main culvert.", "2026-10-09 08:45:00"),
                ("Resolved", "Drainage Supervisor Ramos", "Culvert cleared, storm grate replaced, and road washed down. Free water flow restored.", "2026-10-10 16:30:00")
            ]
        },
        {
            "id": "CMP-2026-003",
            "category": "Electricity",
            "title": "Flickering and non-functional streetlights on Maple Ave",
            "description": "Three consecutive streetlights along Maple Avenue between 8th and 10th street have been dark for 4 nights, creating severe safety concerns for evening commuters, schoolchildren, and neighborhood pedestrians.",
            "location": "Maple Avenue (blocks 800-950), outside Oakridge Middle School",
            "neighborhood": "North Ward",
            "latitude": 40.7225,
            "longitude": -74.0010,
            "contact_name": "Elena Rostova",
            "contact_email": "elena.rostova@example.com",
            "contact_phone": "(555) 456-7890",
            "photo_url": _sample_svg("Dark Streetlights", "Electricity", "#eab308"),
            "responsible_department": DEPARTMENT_MAP["Electricity"],
            "status": "In progress",
            "created_at": "2026-10-12 19:40:00",
            "updated_at": "2026-10-13 10:10:00",
            "history": [
                ("Submitted", "Citizen Submission", "Report received via citizen mobile web app.", "2026-10-12 19:40:00"),
                ("In progress", "Grid Dispatch Center", "Electrical contractor issued work order #EL-882 to inspect underground feeder conduit.", "2026-10-13 10:10:00")
            ]
        },
        {
            "id": "CMP-2026-004",
            "category": "Sanitation",
            "title": "Overflowing public waste bins and windblown trash in park",
            "description": "Two municipal recycling and trash receptacles are overflowing with bags piled on the sidewalk. Strong winds are scattering plastic food containers and waste into the adjacent children's playground.",
            "location": "Westpark Greens, south pavilion by 14th Street",
            "neighborhood": "Westpark Greens",
            "latitude": 40.7090,
            "longitude": -74.0160,
            "contact_name": "David Chen",
            "contact_email": "d.chen@example.com",
            "contact_phone": "(555) 567-8901",
            "photo_url": _sample_svg("Waste Overflow", "Sanitation", "#16a34a"),
            "responsible_department": DEPARTMENT_MAP["Sanitation"],
            "status": "Submitted",
            "created_at": "2026-10-14 08:15:00",
            "updated_at": "2026-10-14 08:15:00",
            "history": [
                ("Submitted", "Citizen Submission", "Complaint logged with photo evidence. Queued for route dispatcher triage.", "2026-10-14 08:15:00")
            ]
        },
        {
            "id": "CMP-2026-005",
            "category": "Public infrastructure",
            "title": "Damaged pedestrian guardrail along elevated walkway",
            "description": "A 10-foot section of the protective safety railing along the elevated pedestrian walkway has buckled and loosened from concrete anchor bolts, presenting an immediate hazard to pedestrians and joggers.",
            "location": "Eastside Pedestrian Bridge over Highway Connector",
            "neighborhood": "Eastside Suburbs",
            "latitude": 40.7160,
            "longitude": -73.9920,
            "contact_name": "Amina Al-Mansoor",
            "contact_email": "amina.m@example.com",
            "contact_phone": "(555) 678-9012",
            "photo_url": _sample_svg("Guardrail Damage", "Public infrastructure", "#7c3aed"),
            "responsible_department": DEPARTMENT_MAP["Public infrastructure"],
            "status": "In progress",
            "created_at": "2026-10-11 16:00:00",
            "updated_at": "2026-10-12 09:30:00",
            "history": [
                ("Submitted", "Citizen Submission", "Urgent infrastructure hazard reported.", "2026-10-11 16:00:00"),
                ("In progress", "Civil Works Rapid Response", "Structural team installed temporary orange barricades. Custom replacement railing section ordered from depot.", "2026-10-12 09:30:00")
            ]
        },
        {
            "id": "CMP-2026-006",
            "category": "Roads",
            "title": "Faded zebra crosswalk markings near elementary school",
            "description": "Zebra crossing markings near the primary school crosswalk have completely eroded away after winter salting. Vehicles are failing to stop for crossing students and parents.",
            "location": "Lincoln Blvd & Pine St, outside St. Jude Primary School",
            "neighborhood": "North Ward",
            "latitude": 40.7250,
            "longitude": -74.0040,
            "contact_name": "Thomas Bradley",
            "contact_email": "tbradley@example.com",
            "contact_phone": "(555) 789-0123",
            "photo_url": _sample_svg("Worn Crosswalk", "Roads", "#d97706"),
            "responsible_department": DEPARTMENT_MAP["Roads"],
            "status": "Submitted",
            "created_at": "2026-10-13 14:10:00",
            "updated_at": "2026-10-13 14:10:00",
            "history": [
                ("Submitted", "Citizen Submission", "Complaint submitted by school parent-teacher council.", "2026-10-13 14:10:00")
            ]
        },
        {
            "id": "CMP-2026-007",
            "category": "Water and drainage",
            "title": "Low water pressure and discolored brown tap water",
            "description": "Multiple multi-family apartment buildings on the odd side of Harbor View Drive are experiencing dirty, sediment-rich water and low pressure under 20 PSI.",
            "location": "310-340 Harbor View Drive",
            "neighborhood": "Riverside District",
            "latitude": 40.7205,
            "longitude": -74.0150,
            "contact_name": "Rachel Green",
            "contact_email": "rachel.g@example.com",
            "contact_phone": "(555) 890-1234",
            "photo_url": _sample_svg("Discolored Water", "Water and drainage", "#0284c7"),
            "responsible_department": DEPARTMENT_MAP["Water and drainage"],
            "status": "Resolved",
            "created_at": "2026-10-09 10:05:00",
            "updated_at": "2026-10-09 17:00:00",
            "history": [
                ("Submitted", "Citizen Submission", "Water quality problem logged.", "2026-10-09 10:05:00"),
                ("In progress", "Water Quality Unit", "Flushing sediment buildup via fire hydrants on Harbor View Dr.", "2026-10-09 11:30:00"),
                ("Resolved", "Chief Quality Chemist", "Hydrant flush completed. Pressure certified at 62 PSI and chemical test verified safe drinking water standards.", "2026-10-09 17:00:00")
            ]
        },
        {
            "id": "CMP-2026-008",
            "category": "Electricity",
            "title": "Exposed high-voltage wiring at municipal utility box base",
            "description": "The galvanized metal hatch on public utility junction box #W-22 was pried open or sheared off, exposing insulated power junctions to children and rain.",
            "location": "South Market St & 2nd Alley, near freight depot",
            "neighborhood": "South Industrial Zone",
            "latitude": 40.7040,
            "longitude": -74.0080,
            "contact_name": "Carlos Mendez",
            "contact_email": "c.mendez@example.com",
            "contact_phone": "(555) 901-2345",
            "photo_url": _sample_svg("Exposed Utility Box", "Electricity", "#eab308"),
            "responsible_department": DEPARTMENT_MAP["Electricity"],
            "status": "Resolved",
            "created_at": "2026-10-07 13:45:00",
            "updated_at": "2026-10-08 11:00:00",
            "history": [
                ("Submitted", "Citizen Submission", "Emergency electrical safety report received.", "2026-10-07 13:45:00"),
                ("In progress", "Emergency Grid Response", "High priority crew isolated junction and placed heavy temporary protective shroud.", "2026-10-07 15:00:00"),
                ("Resolved", "Lead Linesman Kelly", "Installed vandal-resistant padlocked steel enclosure. System certified safe.", "2026-10-08 11:00:00")
            ]
        },
        {
            "id": "CMP-2026-009",
            "category": "Sanitation",
            "title": "Missed scheduled curbside compost and organic waste collection",
            "description": "Green compost bins along the entire residential block of Chestnut Lane were bypassed by the morning collection truck, attracting neighborhood pests.",
            "location": "100-180 Chestnut Lane",
            "neighborhood": "Eastside Suburbs",
            "latitude": 40.7145,
            "longitude": -73.9880,
            "contact_name": "Priya Patel",
            "contact_email": "p.patel@example.com",
            "contact_phone": "(555) 012-3456",
            "photo_url": _sample_svg("Missed Compost", "Sanitation", "#16a34a"),
            "responsible_department": DEPARTMENT_MAP["Sanitation"],
            "status": "Resolved",
            "created_at": "2026-10-06 18:30:00",
            "updated_at": "2026-10-07 12:15:00",
            "history": [
                ("Submitted", "Citizen Submission", "Residential missed pickup notice submitted.", "2026-10-06 18:30:00"),
                ("In progress", "Route Operations", "Supplemental recovery vehicle added to Route #4B dispatch schedule.", "2026-10-07 07:45:00"),
                ("Resolved", "Sanitation Supervisor Roy", "Curbside collection completed for entire block. Apologies issued to homeowners.", "2026-10-07 12:15:00")
            ]
        },
        {
            "id": "CMP-2026-010",
            "category": "Public infrastructure",
            "title": "Broken bench and dislodged stone paving in central civic plaza",
            "description": "Two decorative limestone benches have collapsed masonry supports and nearby paving flagstones have heaved up by 3 inches, creating severe trip hazards.",
            "location": "Centennial Civic Plaza, East Fountain Walkway",
            "neighborhood": "Downtown Central",
            "latitude": 40.7115,
            "longitude": -74.0035,
            "contact_name": "Arthur King",
            "contact_email": "a.king@example.com",
            "contact_phone": "(555) 123-4567",
            "photo_url": _sample_svg("Broken Plaza Bench", "Public infrastructure", "#7c3aed"),
            "responsible_department": DEPARTMENT_MAP["Public infrastructure"],
            "status": "Submitted",
            "created_at": "2026-10-14 07:50:00",
            "updated_at": "2026-10-14 07:50:00",
            "history": [
                ("Submitted", "Citizen Submission", "Public plaza facility inspection request registered.", "2026-10-14 07:50:00")
            ]
        }
    ]

    for c in sample_complaints:
        cursor.execute("""
            INSERT INTO complaints (
                id, category, title, description, location, neighborhood,
                latitude, longitude, contact_name, contact_email, contact_phone,
                photo_url, responsible_department, status, created_at, updated_at
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            c["id"], c["category"], c["title"], c["description"], c["location"],
            c["neighborhood"], c["latitude"], c["longitude"], c["contact_name"],
            c["contact_email"], c["contact_phone"], c["photo_url"],
            c["responsible_department"], c["status"], c["created_at"], c["updated_at"]
        ))

        for hist in c["history"]:
            cursor.execute("""
                INSERT INTO complaint_updates (complaint_id, status, actor, notes, timestamp)
                VALUES (?, ?, ?, ?, ?)
            """, (c["id"], hist[0], hist[1], hist[2], hist[3]))

    conn.commit()

def generate_next_id(conn: sqlite3.Connection) -> str:
    """Generates the next sequential complaint ID in CMP-YYYY-XXX format."""
    year = datetime.now().year
    cursor = conn.cursor()
    cursor.execute("SELECT id FROM complaints WHERE id LIKE ? ORDER BY id DESC LIMIT 1", (f"CMP-{year}-%",))
    row = cursor.fetchone()
    if row:
        last_id = row["id"]
        try:
            parts = last_id.split("-")
            seq = int(parts[2]) + 1
            return f"CMP-{year}-{seq:03d}"
        except (IndexError, ValueError):
            pass
    return f"CMP-{year}-001"

def get_complaints(
    category: Optional[str] = None,
    status: Optional[str] = None,
    neighborhood: Optional[str] = None,
    search: Optional[str] = None,
    sort_by: str = "newest"
) -> List[Dict[str, Any]]:
    """Retrieves complaints matching optional filter, neighborhood, and search criteria."""
    conn = get_db_connection()
    cursor = conn.cursor()

    query = "SELECT * FROM complaints WHERE 1=1"
    params = []

    if category and category != "All":
        query += " AND category = ?"
        params.append(category)

    if status and status != "All":
        query += " AND status = ?"
        params.append(status)

    if neighborhood and neighborhood != "All":
        query += " AND neighborhood = ?"
        params.append(neighborhood)

    if search and search.strip():
        term = f"%{search.strip()}%"
        query += " AND (id LIKE ? OR title LIKE ? OR location LIKE ? OR description LIKE ?)"
        params.extend([term, term, term, term])

    if sort_by == "oldest":
        query += " ORDER BY created_at ASC"
    elif sort_by == "updated":
        query += " ORDER BY updated_at DESC"
    else:
        query += " ORDER BY created_at DESC"

    cursor.execute(query, params)
    rows = cursor.fetchall()
    result = [dict(r) for r in rows]
    conn.close()
    return result

def get_complaint_by_id(complaint_id: str) -> Optional[Dict[str, Any]]:
    """Fetches a single complaint with its complete status history."""
    conn = get_db_connection()
    cursor = conn.cursor()

    cursor.execute("SELECT * FROM complaints WHERE id = ?", (complaint_id.strip().upper(),))
    row = cursor.fetchone()
    if not row:
        # Also try exact match in case casing is different
        cursor.execute("SELECT * FROM complaints WHERE UPPER(id) = ?", (complaint_id.strip().upper(),))
        row = cursor.fetchone()

    if not row:
        conn.close()
        return None

    complaint = dict(row)

    cursor.execute(
        "SELECT * FROM complaint_updates WHERE complaint_id = ? ORDER BY timestamp ASC, id ASC",
        (complaint["id"],)
    )
    updates = [dict(u) for u in cursor.fetchall()]
    complaint["history"] = updates

    conn.close()
    return complaint

def create_complaint(data: Dict[str, Any]) -> Tuple[Dict[str, Any], Optional[str]]:
    """Validates and creates a new citizen complaint."""
    # Validate required fields
    category = data.get("category", "").strip()
    title = data.get("title", "").strip()
    description = data.get("description", "").strip()
    location = data.get("location", "").strip()
    neighborhood = data.get("neighborhood", "").strip()

    if not category or category not in VALID_CATEGORIES:
        return {}, f"Invalid category. Must be one of: {', '.join(VALID_CATEGORIES)}"

    if not title or len(title) < 5:
        return {}, "Title is required and must be at least 5 characters long."

    if len(title) > 150:
        return {}, "Title must not exceed 150 characters."

    if not description or len(description) < 15:
        return {}, "Description is required and must be at least 15 characters to provide adequate detail."

    if not location or len(location) < 3:
        return {}, "Location is required (address, street name, or nearby landmark)."

    if not neighborhood or neighborhood not in NEIGHBORHOODS:
        neighborhood = NEIGHBORHOODS[0]  # Default to Downtown Central

    # Coordinate validation / fallback
    latitude = data.get("latitude")
    longitude = data.get("longitude")
    try:
        latitude = float(latitude) if latitude is not None and str(latitude).strip() != "" else 40.7128
        longitude = float(longitude) if longitude is not None and str(longitude).strip() != "" else -74.0060
    except (ValueError, TypeError):
        latitude = 40.7128
        longitude = -74.0060

    conn = get_db_connection()
    cursor = conn.cursor()

    complaint_id = generate_next_id(conn)
    now_str = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    dept = DEPARTMENT_MAP.get(category, "Public Works Department")

    contact_name = data.get("contact_name", "").strip() or None
    contact_email = data.get("contact_email", "").strip() or None
    contact_phone = data.get("contact_phone", "").strip() or None
    photo_url = data.get("photo_url", "").strip() or None

    cursor.execute("""
        INSERT INTO complaints (
            id, category, title, description, location, neighborhood,
            latitude, longitude, contact_name, contact_email, contact_phone,
            photo_url, responsible_department, status, created_at, updated_at
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, (
        complaint_id, category, title, description, location, neighborhood,
        latitude, longitude, contact_name, contact_email, contact_phone,
        photo_url, dept, "Submitted", now_str, now_str
    ))

    cursor.execute("""
        INSERT INTO complaint_updates (complaint_id, status, actor, notes, timestamp)
        VALUES (?, ?, ?, ?, ?)
    """, (
        complaint_id, "Submitted", "Citizen Submission",
        "Complaint registered successfully via citizen portal.", now_str
    ))

    conn.commit()
    conn.close()

    created = get_complaint_by_id(complaint_id)
    return created, None

def update_complaint_status(complaint_id: str, new_status: str, actor: str, notes: str) -> Tuple[Optional[Dict[str, Any]], Optional[str]]:
    """Updates complaint status and appends a record to the status history."""
    if new_status not in VALID_STATUSES:
        return None, f"Invalid status. Must be one of: {', '.join(VALID_STATUSES)}"

    if not notes or len(notes.strip()) < 3:
        notes = f"Status updated to '{new_status}' by {actor}."

    conn = get_db_connection()
    cursor = conn.cursor()

    cursor.execute("SELECT * FROM complaints WHERE id = ?", (complaint_id,))
    row = cursor.fetchone()
    if not row:
        conn.close()
        return None, "Complaint not found."

    now_str = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    cursor.execute("""
        UPDATE complaints
        SET status = ?, updated_at = ?
        WHERE id = ?
    """, (new_status, now_str, complaint_id))

    cursor.execute("""
        INSERT INTO complaint_updates (complaint_id, status, actor, notes, timestamp)
        VALUES (?, ?, ?, ?, ?)
    """, (complaint_id, new_status, actor or "Department Official", notes.strip(), now_str))

    conn.commit()
    conn.close()

    return get_complaint_by_id(complaint_id), None

def get_stats(neighborhood: Optional[str] = None) -> Dict[str, Any]:
    """Computes summary counts (total, submitted, in progress, resolved) and category breakdowns."""
    conn = get_db_connection()
    cursor = conn.cursor()

    where_clause = ""
    params = []
    if neighborhood and neighborhood != "All":
        where_clause = " WHERE neighborhood = ?"
        params.append(neighborhood)

    cursor.execute(f"SELECT COUNT(*) as total FROM complaints{where_clause}", params)
    total = cursor.fetchone()["total"]

    cursor.execute(f"SELECT COUNT(*) as submitted FROM complaints WHERE status = 'Submitted' {'AND neighborhood = ?' if where_clause else ''}", params)
    submitted = cursor.fetchone()["submitted"]

    cursor.execute(f"SELECT COUNT(*) as in_progress FROM complaints WHERE status = 'In progress' {'AND neighborhood = ?' if where_clause else ''}", params)
    in_progress = cursor.fetchone()["in_progress"]

    cursor.execute(f"SELECT COUNT(*) as resolved FROM complaints WHERE status = 'Resolved' {'AND neighborhood = ?' if where_clause else ''}", params)
    resolved = cursor.fetchone()["resolved"]

    # Category breakdown
    cursor.execute(f"""
        SELECT category, COUNT(*) as cnt
        FROM complaints{where_clause}
        GROUP BY category
    """, params)
    by_category = {row["category"]: row["cnt"] for row in cursor.fetchall()}

    # Ensure all categories are present in breakdown
    for cat in VALID_CATEGORIES:
        if cat not in by_category:
            by_category[cat] = 0

    conn.close()

    return {
        "total": total,
        "submitted": submitted,
        "in_progress": in_progress,
        "resolved": resolved,
        "by_category": by_category,
        "neighborhood": neighborhood or "All"
    }

def get_recent_updates(limit: int = 8, neighborhood: Optional[str] = None) -> List[Dict[str, Any]]:
    """Fetches recent updates across complaints with complaint details."""
    conn = get_db_connection()
    cursor = conn.cursor()

    query = """
        SELECT u.id, u.complaint_id, u.status, u.actor, u.notes, u.timestamp,
               c.title, c.category, c.neighborhood, c.location
        FROM complaint_updates u
        JOIN complaints c ON u.complaint_id = c.id
    """
    params = []
    if neighborhood and neighborhood != "All":
        query += " WHERE c.neighborhood = ?"
        params.append(neighborhood)

    query += " ORDER BY u.timestamp DESC, u.id DESC LIMIT ?"
    params.append(limit)

    cursor.execute(query, params)
    rows = cursor.fetchall()
    conn.close()
    return [dict(r) for r in rows]

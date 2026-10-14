# CivicPulse - Citizen Complaint Management System

> A complete, responsive, and accessible civic platform empowering citizens to report roads, water and drainage, electricity, sanitation, and public infrastructure issues, while tracking their live resolution status across city departments.

---

## 🌟 Key Features

### 1. Citizen Dashboard
- **Welcoming Header & Neighborhood Selector**: Choose from citywide view or specific neighborhoods (*Downtown Central, North Ward, Riverside District, Eastside Suburbs, Westpark Greens, South Industrial Zone*). Changing the neighborhood filters complaints, recalculates summary statistics, and smoothly flies the interactive map to that district.
- **Prominent "Report a Problem" Action**: High-visibility call to action accessible immediately from the top navigation, hero banner, and floating actions.
- **Interactive KPI Summary Cards**: Live counts for **Total Complaints**, **Submitted**, **In Progress**, and **Resolved**. Clicking any card instantly filters the dashboard list.
- **Search & Multi-Filter Bar**:
  - Real-time search across Complaint ID (e.g., `CMP-2026-001`), issue title, description, or street address.
  - Category filter dropdown & fast one-click category pills (*Roads, Water & Drainage, Electricity, Sanitation, Public Infrastructure*).
  - Status filter dropdown (*Submitted, In Progress, Resolved*).
  - Sort by *Newest First*, *Oldest First*, or *Recently Updated*.
  - Instant *Clear Filters* reset button.
- **Interactive Neighborhood Map**:
  - Powered by Leaflet and OpenStreetMap (100% free and open-source; **no paid API keys required**).
  - Custom color-coded pins by status (*Amber for Submitted, Blue for In Progress, Green for Resolved*) with category icons.
  - Interactive popups with issue metadata and a one-click button to open full tracking details.
  - Interactive map sidebar showing complaints in the current view; clicking any sidebar item centers and opens its map pin.
- **Live Department Updates Feed**:
  - Chronological stream showing real-time status transitions, inspector notes, and department responses.

---

### 2. Accessible Complaint Submission
- **Five Standard Municipal Categories**:
  - 🚗 **Roads** &bull; potholes, asphalt cracks, faded crosswalks, traffic signs
  - 💧 **Water & Drainage** &bull; clogged culverts, storm flooding, main leaks, discolored water
  - ⚡ **Electricity** &bull; streetlight outages, exposed wires, damaged utility boxes
  - 🗑️ **Sanitation** &bull; overflowing public bins, missed collections, illegal dumping
  - 🏛️ **Public Infrastructure** &bull; pedestrian walkways, bridge railings, public park benches
- **Short Title & Detailed Description Validation**:
  - Enforced length requirements (title: 5–150 chars; description: min 15 chars) with real-time feedback and ARIA live error announcements.
- **Location & Neighborhood Specification**:
  - Street address / landmark input.
  - Optional **Interactive Location Picker Mini-Map**: click or drag the marker to pinpoint exact geographical coordinates.
- **Optional Contact Details**: Full name, email address, and phone number for citizens who wish to receive notifications.
- **Photo Upload**:
  - Drag-and-drop zone or file browser for image evidence (PNG, JPG, WEBP up to 5MB).
  - Instant image thumbnail preview with file size and remove control.
- **Submission Confirmation Screen**:
  - Clean modal displaying the newly minted Complaint ID (e.g., `CMP-2026-011`).
  - One-click **Copy ID** button.
  - Clear next steps and assigned department notice.
  - Quick action buttons to track immediately or return to the updated dashboard.

---

### 3. Track a Complaint & Department Simulator
- **Comprehensive Investigation View**:
  - Displays Complaint ID, category tag, title, detailed description, exact location, neighborhood, and submission timestamp.
  - Assigned responsible department (*e.g., Department of Transportation & Municipal Roads, Bureau of Water Supply & Drainage Services, etc.*).
  - Evidence photo with zoom preview.
  - Mini location map showing the exact site.
- **Consistent Three-Stage Status Lifecycle**:
  - ⏳ **Submitted**: Received and awaiting departmental dispatch triage.
  - ⚙️ **In Progress**: Work order generated, field inspection, or repair crew active on site.
  - ✓ **Resolved**: Repair verified, safety check signed off, and issue closed.
  - Statuses are distinguished by **readable text**, **distinct colors**, and **unique icons** (never relying solely on color).
- **Resolution Audit Timeline**:
  - Chronological log of every status transition with timestamps, acting parties (*Citizen, Field Inspector, Drainage Crew, etc.*), and official notes.
- **Department Action Simulator**:
  - An interactive civic tool built right into the tracking modal for testing and evaluation.
  - Allows changing a complaint's status to *In Progress* or *Resolved*, specifying an official responder name, and entering official department notes.
  - Changes instantly update the database, refresh the timeline, update summary counters, and push to the Recent Updates feed.

---

### 4. Accessibility & Trustworthy Civic Design
- **WCAG 2.1 AA Compliant**:
  - High color contrast across all UI elements and status badges.
  - Visible focus rings (`box-shadow: 0 0 0 3px rgba(2, 132, 199, 0.4)`) on all interactive controls.
  - "Skip to main content" link for keyboard navigation.
  - Full keyboard accessibility (Tab, Enter, Space, and Escape to dismiss modals).
  - Semantic HTML tags (`<header>`, `<nav>`, `<main>`, `<section>`, `<article>`, `<aside>`, `<footer>`, `<dialog>`).
  - Screen reader friendly labels (`aria-label`, `aria-labelledby`, `aria-describedby`, `aria-live`, `role="status"`, `role="alert"`).
- **High Contrast Mode Toggle**:
  - Built-in one-click high-contrast mode with bold borders and AAA contrast, persisted in `localStorage`.
- **Text Size Scaling**:
  - One-click font size toggle (*Standard &rarr; Large &rarr; Extra Large*), persisted in `localStorage`.
- **Responsive Layout**:
  - Flawless display on mobile screens (320px+), tablets, laptops, and ultra-wide desktops.

---

## 🗄️ How Complaint Data is Stored

The application uses **SQLite** (`complaints.db`) managed through `database.py`.

### Schema

#### 1. `complaints` table
| Column | Type | Description |
|---|---|---|
| `id` | TEXT PRIMARY KEY | Formatted identifier (e.g. `CMP-2026-001`) |
| `category` | TEXT | One of the 5 municipal categories |
| `title` | TEXT | Short issue summary (5–150 chars) |
| `description` | TEXT | Detailed description of the problem |
| `location` | TEXT | Street address, cross-street, or landmark |
| `neighborhood` | TEXT | Neighborhood / district name |
| `latitude` | REAL | Geographic latitude for map rendering |
| `longitude` | REAL | Geographic longitude for map rendering |
| `contact_name` | TEXT | Optional citizen name |
| `contact_email` | TEXT | Optional email address |
| `contact_phone` | TEXT | Optional phone number |
| `photo_url` | TEXT | Base64-encoded image or SVG data URI |
| `responsible_department` | TEXT | Assigned city department |
| `status` | TEXT | `Submitted`, `In progress`, or `Resolved` |
| `created_at` | TEXT | ISO timestamp of submission |
| `updated_at` | TEXT | ISO timestamp of latest change |

#### 2. `complaint_updates` table
| Column | Type | Description |
|---|---|---|
| `id` | INTEGER PRIMARY KEY AUTOINCREMENT | Update identifier |
| `complaint_id` | TEXT | Foreign key referencing `complaints(id)` |
| `status` | TEXT | Complaint status at time of update |
| `actor` | TEXT | Department officer, inspector, or citizen |
| `notes` | TEXT | Commentary or action taken |
| `timestamp` | TEXT | Timestamp of action |

### Data Persistence & Seeding
- On first launch, the database automatically initializes and populates **10 realistic sample complaints** spanning all five categories and diverse neighborhoods with complete history timelines.
- Any complaints submitted or status updates made persist across browser refreshes and server restarts.
- A **"Reset Demo Data"** button is included in the footer to restore the initial sample dataset at any time during testing.

### Storage Limitations & Production Considerations
- **SQLite Concurrency**: SQLite is ideal for local, single-server development and light-to-moderate civic loads with WAL mode. For enterprise production with high concurrent writes across distributed servers, migrate to **PostgreSQL** or **MySQL**.
- **Photo Storage**: Photos are stored as base64 strings in the local SQLite database for zero-configuration portability. In large-scale production, store binary image files in cloud object storage (e.g. AWS S3 or Google Cloud Storage) and save their signed URLs in the database.

---

## 🚀 Setup & Run Instructions

### Prerequisites
- **Python 3.8+** installed (`python --version`)
- Standard Python package installer (`pip`)

### Option A: Windows 1-Click Launch
Double-click `run.bat` in the project root. It will:
1. Install dependencies from `requirements.txt`.
2. Run automated test checks.
3. Start the server on `http://127.0.0.1:5000`.

### Option B: Terminal Command

1. **Install dependencies**:
   ```bash
   python -m pip install -r requirements.txt
   ```

2. **Run the test suite**:
   ```bash
   python test_app.py
   ```
   *(All 16 unit and integration tests should pass)*

3. **Start the application**:
   ```bash
   python app.py
   ```

4. **Open in browser**:
   Navigate to [http://127.0.0.1:5000](http://127.0.0.1:5000)

---

## 📡 REST API Reference

| Endpoint | Method | Description |
|---|---|---|
| `/` | `GET` | Serves the main Citizen Complaint Portal UI |
| `/api/complaints` | `GET` | Filter complaints by `category`, `status`, `neighborhood`, `search`, `sort` |
| `/api/complaints/<id>` | `GET` | Get single complaint details with complete audit history |
| `/api/complaints` | `POST` | Submit a new complaint (JSON payload) |
| `/api/complaints/<id>/status` | `POST` | Update status (`Submitted` / `In progress` / `Resolved`) & append notes |
| `/api/stats` | `GET` | Get total, submitted, in progress, and resolved counts |
| `/api/updates` | `GET` | Get recent department updates & status transitions |
| `/api/reset` | `POST` | Reset database back to realistic sample data |

---

## 🧪 Testing Summary

Automated tests are located in `test_app.py` and test:
- Database initialization and 10-item sample seeding across all 5 categories
- Status representation across Submitted, In progress, Resolved
- Category, status, and neighborhood filtering
- Text search across title, location, description, and complaint ID
- Single complaint retrieval with full audit timeline
- Input validation and descriptive 400 error responses on invalid data
- New complaint creation returning sequential ID (e.g., `CMP-YYYY-XXX`)
- Department status advancement and timeline record appending
- Statistics and summary KPI computations
- Live updates stream retrieval
- Frontend index template rendering and static asset delivery
- Clean reset functionality

Run tests anytime with:
```bash
python test_app.py
```

# 📅 CampusConnect

**The Ultimate Campus Event Management Platform**

<p align="center">
  <strong>Discover • Create • Celebrate Campus Events</strong>
</p>

## Overview

**CampusConnect** is a comprehensive web-based platform designed to help students and administrators discover, organize, and manage campus events effortlessly. Instead of searching across multiple platforms and social media groups, students can access all campus events from one clean, intuitive dashboard.

## Basic Details

### Project Name
CampusConnect - Campus Event Management Platform

### Team Members
- Team Lead: [Your Name] - [College]
- Developer: [Team Member Name] - [College]
- UI/UX Designer: [Team Member Name] - [College]

### Hosted Project Link
Local Hosting: `http://localhost:5000`

### Project Description
CampusConnect is a centralized event management platform that helps students discover, bookmark, and register for campus events. Admins can easily create, edit, and manage events with automatic cleanup of past events.

### Problem Statement
- Campus events information is scattered across WhatsApp groups, social media, emails, and notices
- Students struggle to find relevant events in one place
- Event details are often incomplete or outdated
- No centralized registration system
- Event information gets lost in multiple platforms

### Solution
CampusConnect provides:
- **Centralized Event Platform:** All campus events in one dashboard
- **Smart Filtering:** Events filtered by Tech, Cultural, Fun, Sports categories
- **Admin Tools:** Easy event management with CRUD operations
- **Auto-Cleanup:** Expired events automatically deleted
- **Bookmarks:** Students can save favorite events
- **Session Security:** Secure user and admin authentication

---

## Technical Details

### Technologies/Components Used

**For Software:**
- **Languages:** HTML5, CSS3, JavaScript (Vanilla), Python 3
- **Backend Framework:** Flask (Python web framework)
- **Frontend Framework:** Bootstrap 5.3.3, Custom CSS (Glass-morphism)
- **Database:** SQLite3
- **Libraries & Tools:**
  - Werkzeug (file upload handling)
  - UUID (unique file naming)
  - JSON (API responses)
- **Tools:** VS Code, Git, Windows PowerShell, SQLite Browser
- **APIs:** RESTful API with JSON responses

---

## Features

### ✨ User Features
- ✅ **User Registration & Login:** Secure signup with phone number & password
- ✅ **Event Discovery:** Browse all campus events with posters
- ✅ **Category Filtering:** Filter events by Tech, Cultural, Fun, Sports
- ✅ **Event Details Modal:** View full event information and posters
- ✅ **Bookmarks System:** Save favorite events to localStorage
- ✅ **Quick Registration:** Direct links to event registration forms
- ✅ **Session Management:** 7-day persistent login sessions
- ✅ **Responsive Design:** Mobile-friendly interface
- ✅ **Logout Function:** Secure session termination

### 🛠️ Admin Features
- ✅ **Secure Admin Login:** Username/password protected access
- ✅ **Create Events:** Add new events with posters (PNG, JPG, JPEG, WEBP)
- ✅ **Edit Events:** Modify any event details anytime
- ✅ **Delete Events:** Remove events with confirmation
- ✅ **Event Details Form:** Name, Date, Time, Domain, Content, Registration Link
- ✅ **Poster Management:** Upload, update, auto-cleanup of poster images
- ✅ **Event List View:** See all events with quick actions
- ✅ **Modal View:** Detailed event information display

### ⚡ System Features
- ✅ **Auto-Cleanup:** Automatically deletes events when date < today
- ✅ **File Management:** Secure file uploads with UUID naming
- ✅ **Database Validation:** Parameterized queries prevent SQL injection
- ✅ **Session Security:** Server-side session management
- ✅ **Responsive Layout:** Works on desktop, tablet, mobile devices
- ✅ **Toast Notifications:** Success/error messages with auto-hide
- ✅ **WAL Database Mode:** Prevents database locking issues
- ✅ **Poster Cleanup:** Deletes old poster files when updating events

---

## Implementation

### Installation & Setup

**Step 1: Install Python & Flask**
```powershell
# Check Python installation
python --version

# Install Flask
pip install flask
```

**Step 2: Create uploads folder**
```powershell
# Navigate to project directory
cd "C:\Users\Nima Maria Jacob\OneDrive\Desktop\CampusConnect\CampusConnect"

# Create uploads directory
New-Item -ItemType Directory -Path "static\uploads" -Force
```

**Step 3: Run the application**
```powershell
# Start Flask development server
python app.py

# Expected output:
# * Running on http://127.0.0.1:5000
# * Press CTRL+C to quit
```

**Step 4: Access the application**
```
Open browser → http://localhost:5000
```

---

## User Guide

### 📱 For Students (Users)

#### Registration & Login
1. Visit **http://localhost:5000**
2. Click **"Enter as User"** → **"Sign up"**
3. Enter Phone Number: `0123456789` (or your own)
4. Enter Password: `password123` (min 6 characters)
5. Click **"Create Account"**
6. Login with your credentials

#### Browse Events
1. You're now on **User Dashboard**
2. Use the **Domain Filter** dropdown:
   - **All** - See all events
   - **Tech** - Technology events
   - **Cultural** - Cultural programs
   - **Fun** - Entertainment
   - **Sports** - Sports activities
3. Click on event card to view details

#### Bookmark Events
- Click the **star (☆)** on any event to bookmark
- Star fills **★** when saved
- Go to **"Bookmarks"** to view saved events
- Click star again to remove

#### Register & Logout
- Click **"Register Now"** button to go to registration form
- Click **"Logout"** to end session

### 👨‍💼 For Admins

#### Admin Login
1. Visit **http://localhost:5000**
2. Click **"Enter as Admin"**
3. Username: `admin`
4. Password: `12345`
5. Click **"Login"**

#### Create Event
1. Click **"+ Add Event"** button
2. Fill form fields:
   - **Event Name:** e.g., "Tech Talk 2026"
   - **Date:** `YYYY-MM-DD` (e.g., 2026-02-20)
   - **Time:** e.g., "10:00 AM"
   - **Domain:** Choose Tech/Cultural/Fun/Sports
   - **Poster:** Upload image file
   - **Content:** Event description
   - **Registration Link:** Form/link URL
3. Click **"Submit"**

#### Edit Event
1. Click on event in **"ALL EVENTS"** section
2. Modal appears with event details
3. Click **"✏️ Edit Event"** button
4. Form auto-fills with current details
5. Make changes (can update poster)
6. Click **"Update Event"**

#### Delete Event
1. Find event in **"ALL EVENTS"**
2. Click **trash icon (🗑)** on right
3. Confirm deletion
4. Event removed immediately

---

## Database Schema

### events Table
```sql
CREATE TABLE events (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL,
    date TEXT NOT NULL,
    time TEXT,
    domain TEXT NOT NULL,
    reg_link TEXT NOT NULL,
    content TEXT,
    poster_url TEXT
);
```

### users Table
```sql
CREATE TABLE users (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    phone TEXT UNIQUE NOT NULL,
    password TEXT NOT NULL
);
```

---

## API Documentation

### Base URL
`http://localhost:5000`

### Authentication Endpoints

**POST /api/auth/signup**
- Create new user account
- **Request Body:**
```json
{
  "phone": "0123456789",
  "password": "password123"
}
```
- **Response:** `{ "message": "Account created successfully" }`

**POST /api/auth/login**
- Login and create session
- **Request Body:**
```json
{
  "phone": "0123456789",
  "password": "password123"
}
```
- **Response:** `{ "message": "Login successful" }`

**POST /api/auth/admin-login**
- Admin authentication
- **Request Body:**
```json
{
  "username": "admin",
  "password": "12345"
}
```
- **Response:** `{ "message": "Admin login successful" }`

**POST /api/auth/logout**
- End user session
- **Response:** `{ "message": "Logged out successfully" }`

### Events Endpoints

**GET /api/events**
- Retrieve events with optional filtering
- **Query Parameters:** `domain=All|Tech|Cultural|Fun|Sports`
- **Response:** Array of event objects with all details

**POST /api/events** (Admin only)
- Create new event
- **Form Data:** name, date, time, domain, content, reg_link, poster (file)
- **Response:** `{ "message": "Event added successfully", "id": 1 }`

**PUT /api/events/<event_id>** (Admin only)
- Update existing event
- **Form Data:** name, date, time, domain, content, reg_link, poster (optional)
- **Response:** `{ "message": "Event updated successfully" }`

**DELETE /api/events/<event_id>** (Admin only)
- Delete event
- **Response:** `{ "message": "Event deleted successfully" }`

---

## Project Structure

```
CampusConnect/
├── app.py                          # Flask application & API routes
├── campusconnect.db               # SQLite database (auto-created)
├── README.md                       # Documentation (this file)
├── SETUP_GUIDE.md                 # Quick setup guide
├── create_test_user.py            # Test user creation script
├── static/
│   └── uploads/                   # Event poster storage
└── templates/
    ├── index.html                 # Landing page
    ├── login.html                 # User login/signup
    ├── admin.html                 # Admin login
    ├── user_dashboard.html        # User event browser & bookmarks
    ├── admin_dashboard.html       # Admin event management
    ├── bookmarks.html             # Saved events view
    └── info.html                  # About & contact page
```

---

## Test Credentials

### Test User
- **Phone:** `0123456789`
- **Password:** `password123`
- **Auto-created:** When app starts for first time

### Admin Account
- **Username:** `admin`
- **Password:** `12345`
- **Static:** Change in app.py if needed

---

## Configuration

### Change Admin Credentials
Edit `app.py` (around line 165):
```python
ADMIN_USER = "admin"      # Change username
ADMIN_PASS = "12345"      # Change password
```

### Change Test User Phone
Edit `app.py` (around line 82):
```python
cur.execute("INSERT INTO users (phone, password) VALUES (?, ?)", 
           ("0123456789", "password123"))  # Change phone number
```

### Adjust Session Timeout
Edit `app.py` (line 11):
```python
app.permanent_session_lifetime = timedelta(days=7)  # Change 7 to any number
```

### File Upload Size Limit
Edit `app.py` (line 12):
```python
app.config["MAX_CONTENT_LENGTH"] = 16 * 1024 * 1024  # 16MB max size
```

---

## Key Technologies

- **Frontend:** HTML5, CSS3, JavaScript, Bootstrap 5
- **Backend:** Python, Flask
- **Database:** SQLite3
- **Authentication:** Server-side sessions
- **File Upload:** Werkzeug secure_filename
- **UI Effects:** CSS animations, glass-morphism design

---

## Features Highlights

### 🎯 Smart Auto-Cleanup
- Automatically deletes events when date < today
- Removes associated poster images
- Runs on app startup and every dashboard load

### 🎨 Modern UI/UX
- Glass-morphism design with gradients
- Smooth animations and transitions
- Responsive mobile-first layout
- Toast notifications for feedback

### 🔒 Security
- Secure password storage (store in DB)
- Input validation and sanitization
- SQL injection prevention
- Secure file uploads with UUID naming

### ⚡ Performance
- WAL database mode to prevent locking
- Optimized queries with indexes
- Asynchronous form submissions
- Lazy-loaded Bootstrap components

---

## Troubleshooting

### "Port 5000 already in use"
```powershell
# Flask auto-switches to 5001
python app.py
# Or specify different port via environment
```

### "Database locked" error
```powershell
# Delete corrupted database
Remove-Item campusconnect.db
# Restart app - new DB will be created
python app.py
```

### "Poster upload fails"
1. Verify `static/uploads/` folder exists
2. Check file is PNG, JPG, JPEG, or WEBP
3. File size must be < 16MB
4. Check folder write permissions

### "Login not working"
1. Clear browser cache/cookies
2. Check browser console (F12) for errors
3. Ensure Flask server is running
4. Verify correct credentials

### "Events not showing"
1. Refresh page (Ctrl+F5)
2. Check network tab in browser tools
3. Verify events aren't expired
4. Check console for JS errors

---

## Future Enhancements

🚀 Planned features for v2.0:
- 📧 Email notifications for event reminders
- 📊 Admin analytics dashboard with event stats
- 📱 Mobile app (React Native/Flutter)
- 🗺️ Location mapping with Google Maps
- 💬 User comments and reviews on events
- 🎫 Advanced ticketing system
- 📅 iCal export for calendar integration
- 🔍 Advanced search with full-text search
- 👥 User profile management
- 🔔 Push notifications
- 🌙 Dark mode theme
- 🏆 Leaderboard/gamification

---

## Contributing

Contributions are welcome! Follow these steps:

1. **Fork** the repository
2. **Create** a feature branch: `git checkout -b feature/new-feature`
3. **Commit** changes: `git commit -m "Add new feature"`
4. **Push** to branch: `git push origin feature/new-feature`
5. **Submit** a Pull Request

### Code Guidelines
- Follow PEP 8 for Python code
- Use meaningful variable names
- Add comments for complex logic
- Test before submitting PR

---

## License

This project is licensed under the **MIT License** - see LICENSE file for details.

CampusConnect is free and open-source software. Feel free to use, modify, and distribute!

---

## Contact & Support

For questions, issues, or suggestions:

**📧 Email:** support@campusconnect.edu

**📍 Location:** [Your College], India

**🎓 College:** [Your Institution Name]

**👨‍💼 Team Lead:** [Your Name]

---

## Acknowledgments

- 🙏 Flask and Python community
- 🙏 Bootstrap framework team
- 🙏 College administration and support
- 🙏 All contributors and testers
- 🙏 TinkerHub for guidance

---

## Project Links

- **Repository:** [GitHub Link]
- **Issues:** Report bugs here
- **Discussions:** Ask questions and suggest features
- **Wiki:** Extended documentation

---

<p align="center">
  <strong style="font-size: 18px;">✨ CampusConnect - Never Miss a Campus Event! ✨</strong>
  <br>
  <strong>Built with ❤️ for Campus Community</strong>
  <br>
  <strong>v1.0 • February 2026</strong>
</p>

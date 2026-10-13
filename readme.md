GYM SLOT BOOKING APP

This application is made in python primarily in flask and postgresql for backend with javascript,html and css for frontend.
The application uses Flask with Flask-SQLAlchemy on a relational database and client-side JavaScript (fetch) with Flask-JWT-Extended for authentication.
The schema consists of four relational models:
Users: Stores user_id, name, email,hashed passwords(werkzeug.security), and access role (user vs admin).
Sessions: for date, start hour, total capacity(fixed at 20), and dynamically tracked mats.
Bookings: Links user_id and session_id, alphanumeric booking_code and check-in status.
Waitlist: Tracks positions of useers per session in a waitlist for overflow bookings.   

ASSUMPTIONS
Admin workflows are separated into dedicated routes (/admin, /admin/check-in, /admin/sessions/create) for better user experience, cleared with the coordinator.
Sessions run strictly for 1 hour starting on the hour.
Waitlist promotions follow FIFO order automatically upon cancellation prior to session start.
Handled capacity checks at the application level via active booking counts prior to database commits.
Calculated seats remaining dynamically from active booking records rather than relying solely on a mutable counter column, preventing state drift.   
Automated waitlist promotion executes synchronously within the cancellation transaction, promoting the next queued member immediately without needing a separate message broker or task queue. Members are only promoted from the waitlist if the cancelled session has not yet started. 

Python 3.10(or higher),PostgreSQL,pip and virtual environment required

Test data(1 admin + 2user account and 3 different sessions) through seed.py
Admin 
Name: Gym Admin
Email: admin@gym.com
Password: Admin123!

Member 1
Name: Rohan
Email: rohan@gym.com
Password: Rohan123!
Member 2:
Name: Aditya
Email: aditya@gym.com
Password: Aditya123!

Session 1: 2026-10-15 at 10:00 (19 seats left)
Session 2: 2026-10-17 at 11:00 (20 seats left)
Session 3: 2026-10-18 at 18:00 (FULL - 0 seats left)
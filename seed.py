from datetime import date, time, timedelta
import secrets
from werkzeug.security import generate_password_hash
from app import app, database, user, sessions, bookings, waitlist

with app.app_context():
    waitlist.query.delete()
    bookings.query.delete()
    sessions.query.delete()
    user.query.delete()
    database.session.commit()

    print("Clearing database...")

    admin_user = user(Name="Gym Admin",Email="admin@gym.com",Password=generate_password_hash("Admin123!"))
    admin_user.role = "admin"
    database.session.add(admin_user)

    member1 = user(Name="Rohan",Email="rohan@gym.com",Password=generate_password_hash("Rohan123!"))
    member2 = user(Name="Aditya",Email="aditya@gym.com",Password=generate_password_hash("Aditya123!"))
    database.session.add_all([member1, member2])

    filler_members = []
    for i in range(1, 21):
        u = user(
            Name=f"Attendee {i}",
            Email=f"attendee{i}@gym.com",
            Password=generate_password_hash("Pass123!")
        )
        database.session.add(u)
        filler_members.append(u)

    database.session.commit()

    today = date.today()

    #Session 1 Open with seats available
    s1 = sessions(cap=20,matsleft=19,sdate=today+timedelta(days=2),stime=time(10, 0))
    database.session.add(s1)
    database.session.commit()

    #Rohan booking- Session 1
    code1 = secrets.token_hex(4).upper()
    b1 = bookings(uid=member1.user_id,sid=s1.session_id,bcode=code1)
    database.session.add(b1)

    #Session2 Completely Empty (20 seats left)
    s2 = sessions(cap=20,matsleft=20,sdate=today + timedelta(days=4),stime=time(11, 0))
    database.session.add(s2)

    #Session3-Completely FULL(0 seats left)
    s3_full = sessions(
        cap=20,
        matsleft=0,
        sdate=today + timedelta(days=4),
        stime=time(18, 0)
    )
    database.session.add(s3_full)
    database.session.commit()

    
    for i in range(20):
        b_code = secrets.token_hex(4).upper()
        b_full = bookings(
            uid=filler_members[i].user_id,sid=s3_full.session_id,bcode=b_code)
        database.session.add(b_full)

    database.session.commit()

    print("\nDatabase seeded")
    print("Admin:    admin@gym.com  / Admin123!")
    print("Member 1: rohan@gym.com  / Rohan123!")
    print("Member 2: aditya@gym.com    / Aditya123!")
    print(f"Session 1: {today+ timedelta(days=2)} at 10:00 (19 seats left)")
    print(f"Session 2: {today + timedelta(days=4)} at 11:00 (20 seats left)")
    print(f"Session 3: {today + timedelta(days=5)} at 18:00 (FULL - 0 seats left)")
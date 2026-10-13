from flask import Flask, render_template,redirect,url_for,request,jsonify
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import UniqueConstraint
from dotenv import load_dotenv
import os,secrets,traceback
from flask_migrate import Migrate
from datetime import datetime,timedelta
from werkzeug.security import check_password_hash,generate_password_hash
from flask_jwt_extended import JWTManager,get_jwt_identity,jwt_required,create_access_token

load_dotenv()

app=Flask(__name__)

app.config['SQLALCHEMY_DATABASE_URI']=os.environ['DATABASE_URL']
app.config['SQLALCHEMY_TRACK_MODIFICATIONS']=False
app.config['JWT_SECRET_KEY']=os.environ['JWT_SECRET_KEY']

database=SQLAlchemy(app)
migrate=Migrate(app,database)
jwt=JWTManager(app)

def error_all(msg,status):
    return jsonify({
        "success":False,
        "message":msg
    }),status

class user(database.Model):
    __tablename__='Users'

    user_id=database.Column(database.Integer,primary_key=True)
    name=database.Column(database.String(100), nullable=False)
    email=database.Column(database.String(100),unique=True, nullable=False)
    password_hashed=database.Column(database.String(255),nullable=False)
    role = database.Column(database.String(20), nullable=False, default="user", server_default="user")

    def __init__(self, Name , Email, Password ):
        self.name=Name
        self.email=Email
        self.password_hashed=Password

class sessions(database.Model):
    __tablename__='Sessions'

    session_id=database.Column(database.Integer, unique=True, primary_key=True) 
    capacity=database.Column(database.Integer, nullable=False , default=20)
    mats_left=database.Column(database.Integer)
    session_date=database.Column(database.Date,nullable=False)
    session_time=database.Column(database.Time,nullable=False)

    __table_args__ = (UniqueConstraint('session_date', 'session_time', name='uix_date_time'),)

    def __init__(self, cap , matsleft , sdate , stime):
        self.capacity=cap
        self.mats_left=matsleft
        self.session_date=sdate
        self.session_time=stime
    

class bookings(database.Model):
    __tablename__='Bookings'

    booking_id=database.Column(database.Integer, unique=True,  primary_key=True)
    user_id=database.Column(database.Integer, database.ForeignKey('Users.user_id'))
    session_id=database.Column(database.Integer, database.ForeignKey('Sessions.session_id'))
    booking_code=database.Column(database.String(12),unique=True,nullable=True)
    checked_in=database.Column(database.Boolean, default=False)

    def __init__(self,uid,sid,bcode):
        self.user_id=uid
        self.session_id=sid
        self.booking_code=bcode


class waitlist(database.Model):
    __tablename__='Waitlist'

    waitlist_id=database.Column(database.Integer, unique=True,  primary_key=True)
    user_id=database.Column(database.Integer, database.ForeignKey('Users.user_id'))
    session_id=database.Column(database.Integer, database.ForeignKey('Sessions.session_id'))
    waitlist_number=database.Column(database.Integer, nullable=False)
    
    def __init__(self,uid,sid,wno):
        self.user_id=uid
        self.session_id=sid
        self.waitlist_number=wno
        

@app.route('/')
def home():
    return render_template("home.html")

@app.route('/register', methods=["GET","POST"] )
def register():
    if request.method=="GET":
        return render_template("register.html")
    rdata=request.get_json()
    if not rdata:
        return error_all("Invalid or missing JSON payload", 400)
    name=rdata.get('name')
    email=rdata.get('email')
    password=rdata.get('password')
    if not name or not email or not password:
        return error_all("Name, Email and Password are required",400)
    user_exists=user.query.filter_by(email=email).first()
    if(user_exists):
        return error_all("User already exists",409)
    hashed_pass=generate_password_hash(password)
    new_user=user(name,email,hashed_pass)
    database.session.add(new_user)
    try:
       database.session.commit()
    except Exception as error:
        database.session.rollback()
        return error_all("Internal error_all",500)
    return jsonify({
            "success":True,
            "message":"Registeration Succesful"
        }),201

@app.route('/login',methods=["GET","POST"])
def login():
    if request.method=="GET":
        return render_template("login.html")
    ldata=request.get_json()
    if not ldata:
        return error_all("Invalid or missing JSON payload", 400)
    name=ldata.get('name')
    email=ldata.get('email')
    password=ldata.get('password')
    if not name or not email or not password:
            return error_all("Name, Email and Password are required",400)
    existing_user=user.query.filter_by(email=email).first()
    if existing_user is None or not check_password_hash(existing_user.password_hashed,password):
        return error_all("Invalid email or password",401)

    accesstoken=create_access_token(identity=str(existing_user.user_id),additional_claims={"role": existing_user.role})
    return jsonify({
        "success":True,
        "message":"Login successful",
        "access_token": accesstoken,
        "role": existing_user.role
    })
@app.route('/user')
def user_page():
    return render_template("home.html")

@app.route('/admin')
def admin_page():
    return render_template("admin.html")

@app.route('/admin/sessions/create')
def session_create_html():
    return render_template("session_create.html")

@app.route('/api/admin/sessions/create',methods=["POST"])
@jwt_required()
def create_sessions():
    user_id = int(get_jwt_identity())
    admin = user.query.get(user_id)
    if admin is None or admin.role != 'admin':
        return error_all("Admin access required.",403)
    sdata=request.get_json()
    if not sdata:
            return error_all("Invalid or missing JSON payload", 400)
    date=sdata.get('date')
    time=sdata.get('time')
    if not date or not time:
            return error_all("All options are required",400)
    existing_session=sessions.query.filter_by(session_date=date,session_time=time).first()
    if(existing_session):
            return error_all("Session already exists",409)
    new_session=sessions(20,20,date,time)
    database.session.add(new_session)
    try:
           database.session.commit()
    except Exception as error:
            database.session.rollback()
            return error_all("Internal error_all",500)
    return jsonify({
                "success":True,
                "message":"Session created successfully"
            })

@app.route('/admin/check-in')
def check_in_html():
    return render_template("admin_checkin.html")

@app.route('/api/admin/check-in',methods=["POST"])
@jwt_required()
def check_in():
    user_id = int(get_jwt_identity())
    admin = user.query.get(user_id)
    if admin is None or admin.role != 'admin':
        return error_all("Admin access required.",403)
    cdata=request.get_json()
    if not cdata:
        return error_all("Invalid or missing JSON payload", 400)
    bcode=cdata.get('bookingcode')
    if not bcode:
        return error_all("Booking code is required", 400)
    booking=bookings.query.filter_by(booking_code=bcode).first()
    if not booking:
         return error_all("No valid booking",404)
    if (booking.checked_in):
         return error_all("This booking has already been checked in",409)
    session=sessions.query.filter_by(session_id=booking.session_id).first()
    if not session:
             return error_all("No valid session",404)
    start_time = datetime.combine(session.session_date, session.session_time)
    end_time = start_time+timedelta(hours=1)
    now= datetime.now()
    if not (start_time <= now < end_time):
        return error_all("Check-in is only allowed during the session hour.",409)
    try:
        usr=user.query.filter_by(user_id=booking.user_id).first()
        booking.checked_in=True
        database.session.commit()
        return jsonify({"success":True,"message":"checked in","name":usr.name,"email":usr.email})
    except Exception as e:
        database.session.rollback()
        return error_all("Server error,couldnot complete check in",500)

@app.route('/admin/roster')
def admin_roster_page():
    return render_template("adminroster.html")

@app.route('/admin/session/<int:session_id>/bookings', methods=['GET'])
@jwt_required()
def admin_session_bookings(session_id):
    user_id = int(get_jwt_identity())
    admin_usr = user.query.get(user_id)
    if admin_usr is None or admin_usr.role != 'admin':
        return error_all("Admin access required.", 403)

    session_bookings = bookings.query.filter_by(session_id=session_id).all()
    data = []
    for b in session_bookings:
        usr = user.query.get(b.user_id)
        data.append({
            'booking_id': b.booking_id,
            'booking_code': b.booking_code,
            'checked_in': b.checked_in,
            'name': usr.name if usr else 'Unknown',
            'email': usr.email if usr else 'Unknown'
        })
    return jsonify(data), 200


@app.route('/sessions')
def sessions_page():
    return render_template("sessions.html")


@app.route('/api/sessions',methods=["GET"])
@jwt_required()
def show_sessions():
    date = request.args.get('date')
    if date:
        sessiondata = sessions.query.filter_by(session_date=date).all()
    else:
        sessiondata = sessions.query.all()
    data = []
    for s in sessiondata:
        booked_count = bookings.query.filter_by(session_id=s.session_id).count()
        mats_left = max(0, s.capacity - booked_count)
        data.append({
            'session_id': s.session_id,
            'date': str(s.session_date),
            'time': str(s.session_time),
            'mats_left': mats_left
        })
    return jsonify(data), 200

@app.route('/sessions/book/<int:sessionid>',methods=["POST"])
@jwt_required()
def book_session(sessionid):
    usrid = int(get_jwt_identity())
    try:
        selected_session = sessions.query.filter_by(session_id=sessionid).first()
        if selected_session is None:
            return error_all("Session not found",404)
        existing_booking = bookings.query.filter_by(
            user_id=usrid, session_id=sessionid
        ).first()
        if existing_booking:
            return error_all("Already have a booking",409)
        existing_waitlist = waitlist.query.filter_by(
            user_id=usrid, session_id=sessionid
        ).first()
        if existing_waitlist:
            return error_all("You are already on the waitlist",409)

        booked_count = bookings.query.filter_by(session_id=sessionid).count()
        if booked_count >= selected_session.capacity:
            return error_all("Session is full. Please join the waitlist.",409)
        bcd = secrets.token_hex(4).upper()
        new_booking = bookings(usrid,sessionid,bcd)
        database.session.add(new_booking)
        database.session.commit()
        return jsonify({
            "success":True,
            "message":"Booking successful",
            "booking_code":bcd
        }),201
    except Exception as e:
        database.session.rollback()
        return error_all("Server error",500)

@app.route('/sessions/waitlist/<int:sessionid>',methods=["POST"])
@jwt_required()
def join_waitlist(sessionid):
    usrid = int(get_jwt_identity())
    try:
        selected_session = sessions.query.filter_by(session_id=sessionid).first()
        if selected_session is None:
            return error_all("Session not found",404)
        existing_booking = bookings.query.filter_by(
            user_id=usrid, session_id=sessionid
        ).first()
        if existing_booking:
            return error_all("You already have a booking",409)
        existing_waitlist = waitlist.query.filter_by(
            user_id=usrid, session_id=sessionid
        ).first()
        if existing_waitlist:
            return error_all("You are already on the waitlist",409)

        booked_count = bookings.query.filter_by(session_id=sessionid).count()
        if booked_count < selected_session.capacity:
            return error_all("Session still has available mats. Please book it.",409)
        last_entry = waitlist.query.filter_by(
            session_id=sessionid
        ).order_by(waitlist.waitlist_number.desc()).first()
        if last_entry:
            waitlist_number = last_entry.waitlist_number + 1
        else:
            waitlist_number = 1
        new_waitlist = waitlist(usrid,sessionid,waitlist_number)
        database.session.add(new_waitlist)
        database.session.commit()
        return jsonify({
            "success":True,
            "message":"Successfully joined the waitlist",
            "waitlist_number":waitlist_number
        }),201
    except Exception as e:
        database.session.rollback()
        return error_all("Server error",500)
    


@app.route('/my_bookings')
@jwt_required()
def history():
    user_id = int(get_jwt_identity())

    user_bookings = bookings.query.filter_by(user_id=user_id).all()
    result =[]
    for booking in user_bookings:
        session = sessions.query.filter_by(session_id=booking.session_id).first()
        if session is None:
            continue
        result.append({'type': 'booked','booking_id': booking.booking_id,'session_id': session.session_id,
            'date': session.session_date.strftime('%Y-%m-%d'),'time': session.session_time.strftime('%H:%M'),
            'checked_in': booking.checked_in ,'booking_code':booking.booking_code})

    user_waitlist = waitlist.query.filter_by(user_id=user_id).all()
    for entry in user_waitlist:
        session = sessions.query.filter_by(session_id=entry.session_id).first()
        if session is None:
            continue
        result.append({ 'type': 'waitlisted','waitlist_id': entry.waitlist_id,'session_id': session.session_id,
            'date': session.session_date.strftime('%Y-%m-%d'),'time': session.session_time.strftime('%H:%M'),
            'waitlist_number': entry.waitlist_number})
    result.sort(key=lambda item: (item['date'], item['time']), reverse=True)

    return jsonify(result), 200

@app.route('/booking_history')
def bookinghistory():
    return render_template("history.html")

@app.route('/booking/del/<int:bookingid>',methods=["DELETE"])
@jwt_required()
def cancel_booking(bookingid):
    try:
        user_id = int(get_jwt_identity())
        booking_to_delete = bookings.query.filter_by(booking_id=bookingid,user_id=user_id).first()
        if booking_to_delete is None:
             return error_all("Booking cannot be found",404)
        waitlist_count=waitlist.query.filter_by(session_id=booking_to_delete.session_id).all()
        session=sessions.query.filter_by(session_id=booking_to_delete.session_id).first()
        session_start = datetime.combine(session.session_date, session.session_time)
        if datetime.now() >= session_start:
            return error_all("Cannot cancel a session that has already started.", 400)
        if datetime.now()< session_start and len(waitlist_count) != 0:
            waitlist_first = waitlist.query.filter_by(session_id=booking_to_delete.session_id).order_by(waitlist.waitlist_number.asc()).first()
            code = secrets.token_hex(4).upper()
            booking_to_be_made = bookings(waitlist_first.user_id,waitlist_first.session_id,code)
            database.session.add(booking_to_be_made)
            database.session.delete(waitlist_first)

        database.session.delete(booking_to_delete)
        database.session.commit()
        return jsonify({'message':"Booking succesfully cancelled"}),200 
    except Exception as e:
        database.session.rollback()
        return error_all("Server error",500)

@app.route('/waitlist/del/<int:waitlistid>',methods=["DELETE"])
@jwt_required()
def cancel_waitlist(waitlistid):
    user_id = int(get_jwt_identity())
    try:
        waitlist_to_delete=waitlist.query.filter_by(waitlist_id=waitlistid,user_id=user_id).first()
        if waitlist_to_delete is None:
            return error_all("Booking cannot be found in waitlist",404)
        database.session.delete(waitlist_to_delete)
        database.session.commit()
        return jsonify({'message':"Booking succesfully cancelled"}),200 
    except Exception as e:
        database.session.rollback()
        return error_all("Server error",500)

@app.errorhandler(404)
def handle_404(e):
    return error_all("Endpoint or resource not found.", 404)

@app.errorhandler(500)
def handle_500(e):
    return error_all("Internal server error.", 500)

@app.errorhandler(Exception)
def handle_generic_exception(e):
    return error_all("An unexpected error occurred.", 500)

if __name__=='__main__':
    app.run(debug=True)
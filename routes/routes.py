from flask import Blueprint, request, jsonify, send_file
from models.model import User, Classroom, Attendance
from models.database import db
from services.services import create_user
import qrcode
import io
import jwt
import datetime

SECRET_KEY = "YOUR_SECRET_KEY"

routes_bp = Blueprint("routes", __name__)

@routes_bp.route('/create_users', methods=['POST'])
def route_create_users():
    data = request.json

    # Ensure JSON array
    if not isinstance(data, list):
        return jsonify({"error": "Expected a list of users"}), 400

    created_users = []
    for item in data:
        if not all(key in item for key in ['name', 'email', 'role']):
            return jsonify({"error": f"Missing required fields in {item}"}), 400

        user = create_user(
            name=item['name'],
            email=item['email'],
            reg_no=item.get('reg_no'),
            role=item['role'],
            dept=item.get('dept'),
            semester=item.get('semester'),
            password=item.get('password', 'password')
        )

        created_users.append({
            "id": user.id,
            "name": user.name,
            "email": user.email,
            "role": user.role
        })

    return jsonify({"message": "Users created", "data": created_users}), 201

@routes_bp.route('/login', methods=['POST'])
def login():
    data = request.json
    email = data.get("email")
    password = data.get("password")

    if not email or not password:
        return jsonify({"error": "Email and password required"}), 400

    user = User.query.filter_by(email=email).first()
    if not user or not user.check_password(password):
        return jsonify({"error": "Invalid email or password"}), 401

    # Generate JWT token (expires in 2 hours)
    payload = {
        "user_id": user.id,
        "role": user.role,
        "exp": datetime.datetime.utcnow() + datetime.timedelta(hours=2)
    }
    token = jwt.encode(payload, SECRET_KEY, algorithm="HS256")

    return jsonify({
        "message": f"Welcome {user.name}!",
        "token": token,
        "user": {
            "id": user.id,
            "name": user.name,
            "email": user.email,
            "role": user.role
        }
    }), 200

@routes_bp.route('/classroom/<int:classroom_id>/qr', methods=['GET'])
def classroom_qr(classroom_id):
    classroom = Classroom.query.get(classroom_id)
    if not classroom:
        return jsonify({"error": "Classroom not found"}), 404

    # JWT token containing classroom ID and expiry
    payload = {
        "classroom_id": classroom_id,
        "exp": datetime.datetime.utcnow() + datetime.timedelta(minutes=15)
    }
    token = jwt.encode(payload, SECRET_KEY, algorithm="HS256")

    qr = qrcode.QRCode(version=1, box_size=10, border=5)
    qr.add_data(token)
    qr.make(fit=True)

    img = qr.make_image(fill="black", back_color="white")
    buf = io.BytesIO()
    img.save(buf, format="PNG")
    buf.seek(0)

    return send_file(buf, mimetype='image/png')

# Commit attendance after scanning QR code
@routes_bp.route('/attendance/commit', methods=['POST'])
def commit_attendance():
    data = request.json
    token = data.get("token", "").strip()
    user_id = data.get("user_id")  # authenticated user ID

    if not token or not user_id:
        return jsonify({"error": "Token and user_id required"}), 400

    try:
        decoded = jwt.decode(token, SECRET_KEY, algorithms=["HS256"])
        classroom_id = decoded["classroom_id"]
    except jwt.ExpiredSignatureError:
        return jsonify({"error": "Token expired"}), 401
    except jwt.InvalidTokenError:
        return jsonify({"error": "Invalid token"}), 401

    user = User.query.get(user_id)
    if not user or user.role != "Student":
        return jsonify({"error": "Invalid user"}), 403

    # Check if attendance already exists
    today = datetime.date.today()
    existing = Attendance.query.filter_by(student_id=user_id, classroom_id=classroom_id, date=today).first()
    if existing:
        return jsonify({"message": "Attendance already recorded"}), 200

    attendance = Attendance(student_id=user_id, classroom_id=classroom_id, status="Present")
    db.session.add(attendance)
    db.session.commit()

    return jsonify({"message": f"Attendance recorded for {user.name} in classroom {classroom_id}"}), 201

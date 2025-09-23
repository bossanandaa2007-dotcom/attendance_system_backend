from models.model import User, Attendance, db
from datetime import date

# Create a new user

def create_user(name, email, reg_no, role, dept, semester, password):
    user = User(
        name=name,
        email=email,
        reg_no=reg_no,
        role=role,
        dept=dept,
        semester=semester,
        password_hash=password
    )
    db.session.add(user)
    db.session.commit()
    return user


# Get attendance based on role
def get_attendance(user):
    if user.role == 'Student':
        return Attendance.query.filter_by(student_id=user.id).all()
    elif user.role == 'Faculty':
        # Assuming Faculty can see all students in their dept
        return Attendance.query.join(User).filter(User.dept == user.dept).all()
    elif user.role == 'HOD':
        # HOD sees all students in their department
        return Attendance.query.join(User).filter(User.dept == user.dept).all()
    elif user.role == 'Dean':
        # Dean sees all attendance globally
        return Attendance.query.all()
    else:
        return []

# Mark attendance
def mark_attendance(student_id, status):
    today = date.today()
    attendance = Attendance(student_id=student_id, date=today, status=status)
    db.session.add(attendance)
    db.session.commit()
    return attendance

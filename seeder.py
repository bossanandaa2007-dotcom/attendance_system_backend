from app import create_app
from models.database import db
from models.model import User, Classroom

# Users to store in DB
users_data = [
    {"name": "Prakul", "email": "prakuk@vernex.com", "reg_no": "91242432", "role": "Student", "dept": "AI_DS", "semester": "3", "password": "PASS_1234"},
    {"name": "Allen Danel", "email": "allen@vernex.com", "reg_no": "9124243004", "role": "Student", "dept": "AI_DS", "semester": "3", "password": "PASS_1234"},
    {"name": "Dinesh", "email": "dinesh@vernex.com", "reg_no": "9124243045", "role": "Student", "dept": "AI_DS", "semester": "3", "password": "PASS_1234"},
    {"name": "Devi", "email": "devi@vernex.com", "reg_no": "9124243009", "role": "Student", "dept": "AI_DS", "semester": "3", "password": "PASS_1234"},
    {"name": "Bhuvanesh", "email": "bhuvanesh@vernex.com", "reg_no": "9124243010", "role": "Student", "dept": "AI_DS", "semester": "3", "password": "PASS_1234"},
    {"name": "Boss Anandaa", "email": "bossfaculty@vernex.com", "reg_no": "F01", "role": "Faculty", "dept": "AI_DS", "semester": None, "password": "PASS_1234"},
    {"name": "Boss Anandaa", "email": "bosshod@vernex.com", "reg_no": "HOD01", "role": "HOD", "dept": "AI_DS", "semester": None, "password": "PASS_1234"},
    {"name": "Boss Anandaa", "email": "bossdean@vernex.com", "reg_no": "Dean01", "role": "Dean", "dept": None, "semester": None, "password": "PASS_1234"}
]


classrooms_data = [
    {"name": "AI_DS 101", "course_code": "AI101", "faculty_email": "bossfaculty@vernex.com"}
]


def seed():
    app = create_app()
    with app.app_context():
        for u in users_data:
            if not User.query.filter_by(email=u["email"]).first():
                user = User(name=u["name"], email=u["email"], reg_no=u.get("reg_no"), role=u["role"], dept=u.get("dept"), semester=u.get("semester"))
                user.set_password(u["password"])
                db.session.add(user)
        db.session.commit()

        for c in classrooms_data:
            faculty = User.query.filter_by(email=c["faculty_email"]).first()
            if faculty and not Classroom.query.filter_by(course_code=c["course_code"]).first():
                classroom = Classroom(name=c["name"], course_code=c["course_code"], faculty_id=faculty.id)
                db.session.add(classroom)
        db.session.commit()
        print("✅ Seeder finished!")

if __name__ == "__main__":
    seed()

from models.model import db, User  # Adjust if your User model is elsewhere

def create_user(name, email, reg_no=None, role=None, dept=None, semester=None, password='password'):
    user = User(
        name=name,
        email=email,
        reg_no=reg_no,
        role=role,
        dept=dept,
        semester=semester,
        password=password
    )
    db.session.add(user)
    db.session.commit()
    return user

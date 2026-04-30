from sqlmodel import Session, select
from .db import engine
from .models import User, Role, Course, Enrollment, Grade, Announcement
from .security import hash_password


def seed() -> None:
    with Session(engine) as s:
        if s.exec(select(User)).first():
            return  # already seeded

        admin = User(email="admin@mentec.test", password_hash=hash_password("admin123"),
                     full_name="Site Admin", role=Role.admin)
        lecturer = User(email="lecturer@mentec.test", password_hash=hash_password("lecturer123"),
                        full_name="Dr. Ada Lovelace", role=Role.lecturer)
        student = User(email="student@mentec.test", password_hash=hash_password("student123"),
                       full_name="Sam Student", role=Role.student)
        s.add_all([admin, lecturer, student])
        s.commit()
        s.refresh(lecturer); s.refresh(student)

        course = Course(code="CS101", title="Intro to Computer Science",
                        description="Foundations of programming and computational thinking.",
                        lecturer_id=lecturer.id)
        s.add(course); s.commit(); s.refresh(course)

        s.add(Enrollment(student_id=student.id, course_id=course.id))
        s.add(Grade(student_id=student.id, course_id=course.id,
                    assessment="Midterm", score=82, max_score=100))
        s.add(Announcement(author_id=lecturer.id,
                           title="Welcome to CS101",
                           body="Lectures begin Monday at 9am. Please review the syllabus."))
        s.commit()

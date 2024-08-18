from datetime import date
import unittest
from .controllers import student_post_controller
from .schemas import StudentCreate


def create_student() -> StudentCreate:
    return StudentCreate(
        email="test@mail.com",
        name="John Doe",
        date_of_birth=date(2010, 1, 1),
        university="Test University",
        major="Test Major",
        credits=100,
        gpa=8.00,
        password="test-password",
    )


class UnitTests(unittest.TestCase):
    async def test_student_create(self):
        student = create_student()
        result = await student_post_controller(student)
        self.assertTrue(result == None)

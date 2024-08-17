import asyncio
import unittest
from unittest.mock import patch, AsyncMock
from ..security import pwd_context
from src.controllers import student_post_controller
from src.schemas import StudentCreate


class UnitTests(unittest.TestCase):
    @patch("src.controllers.get_async_pool")
    def test_student_post_controller(self, mock_get_async_pool: AsyncMock):
        mock_connection = AsyncMock()
        mock_get_async_pool.return_value.connection.return_value.__aenter__.return_value = mock_connection

        password = "password123"
        hashed_password = pwd_context.hash(password)
        
        student = StudentCreate(
            email="test@example.com",
            password="password123",
            name="John Doe",
            date_of_birth="2000-01-01",
            university="Test University",
            major="Computer Science",
            credits=120,
            gpa=3.5
        )

        asyncio.run(student_post_controller(student))

        mock_connection.execute.assert_called_once_with(
            "INSERT INTO students (email, hashed_password, name, date_of_birth, university, major, credits, gpa) VALUES (%s, %s, %s, %s, %s, %s, %s, %s)",
            params=[
                student.email,
                hashed_password,
                student.name,
                student.date_of_birth,
                student.university,
                student.major,
                student.credits,
                student.gpa
            ]
        )

if __name__ == '__main__':
    unittest.main()

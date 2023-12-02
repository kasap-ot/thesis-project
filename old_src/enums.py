from enum import Enum


class Status(Enum):
    WAITING = 1
    ACCEPTED = 2
    REJECTED = 3


class UserType(Enum):
    STUDENT = "student"
    COMPANY = "company"
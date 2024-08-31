from enum import Enum


class Status(Enum):
    WAITING = 0
    ACCEPTED = 1
    REJECTED = 2


class UserType(Enum):
    STUDENT = "student"
    COMPANY = "company"


class Region(Enum):
    GLOBAL = 0
    EUROPE = 1
    ASIA = 2
    AMERICAS = 3

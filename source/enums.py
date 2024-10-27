from enum import Enum


class Status(Enum):
    WAITING = "WAITING"
    ACCEPTED = "ACCEPTED"
    REJECTED = "REJECTED"
    ONGOING = "ONGOING"
    COMPLETED = "COMPLETED"
    ARCHIVED = "ARCHIVED"


class UserType(Enum):
    STUDENT = "student"
    COMPANY = "company"


class Region(Enum):
    GLOBAL = 0
    EUROPE = 1
    ASIA = 2
    AMERICAS = 3


MIN_GPA = 0.00
MAX_GPA = 10.00
MIN_CREDITS = 0
MAX_CREDITS = 300


class Environment:
    TESTING = "TESTING"
    EMAIL_ADDRESS = "EMAIL_ADDRESS"
    EMAIL_PASSWORD = "EMAIL_PASSWORD"
    TRUE = "TRUE"
    FALSE = "FALSE"
from enum import Enum

class TestResult(Enum):
    OK = 'O'
    INCORRECT = ''
    ERROR = 'X'
    ENDLESS_LOOP = 'Inf'
    INACCURATE = 'L'
    FORBIDDEN = 'F'
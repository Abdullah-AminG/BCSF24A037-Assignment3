"""Simple tools for the PUCIT BS(CS) GPA assistant."""

from math import isfinite

# Each entry is (course code, course name, graded credit hours).
# MD-001 and MD-002 are pass/fail, non-credit courses, so they are not here.
COURSES = {
    1: [
        ("MS-251", "Probability & Statistics", 3.0),
        ("GE-160", "Applications of ICT", 3.0),
        ("GE-169", "Applied Physics", 3.0),
        ("GE-167", "Discrete Structures", 3.0),
        ("HQ-001", "Quran Translation - I", 0.5),
        ("GE-190", "Functional English", 3.0),
    ],
    2: [
        ("CC-112", "Programming Fundamentals", 3.0),
        ("CC-112-L", "Programming Fundamentals Lab", 1.0),
        ("CC-110", "Digital Logic Design", 2.0),
        ("CC-110-L", "Digital Logic Design Lab", 1.0),
        ("MS-252", "Linear Algebra", 3.0),
        ("GE-191", "Expository Writing", 3.0),
        ("GE-163", "Islamic Studies", 2.0),
        ("HQ-002", "Quran Translation - II", 0.5),
    ],
    3: [
        ("CC-211", "Object Oriented Programming", 3.0),
        ("CC-211-L", "Object Oriented Programming Lab", 1.0),
        ("CC-215", "Database Systems", 3.0),
        ("CC-215-L", "Database Systems Lab", 1.0),
        ("CC-210", "Computer Organization & Assembly Language", 3.0),
        ("GE-162", "Calculus & Analytical Geometry", 3.0),
        ("GE-192", "Introduction to Management", 2.0),
        ("HQ-003", "Quran Translation - III", 0.5),
    ],
    4: [
        ("CC-213", "Data Structures", 3.0),
        ("CC-213-L", "Data Structures Lab", 1.0),
        ("CC-312", "Information Security", 3.0),
        ("CC-214", "Computer Networks", 3.0),
        ("CC-212", "Software Engineering", 3.0),
        ("DC-220", "Advanced Database Management Systems", 3.0),
        ("HQ-004", "Quran Translation - IV", 0.5),
    ],
    5: [
        ("CC-313", "Analysis of Algorithms", 3.0),
        ("CC-310", "Artificial Intelligence", 3.0),
        ("DC-320", "Theory of Automata and Formal Languages", 3.0),
        ("DC-321", "Human Computer Interaction", 3.0),
        ("DC-322", "Computer Architecture", 3.0),
        ("EC-330", "Web Technologies / Elective", 3.0),
        ("HQ-005", "Quran Translation - V", 0.5),
    ],
    6: [
        ("CC-311", "Operating Systems", 3.0),
        ("EC-333", "Mobile Application Development / Elective", 3.0),
        ("EC-324", "Software Construction & Development / Elective", 3.0),
        ("EC-335", "Machine Learning / Elective", 3.0),
        ("EC-334", "Game Design and Development / Elective", 3.0),
        ("MS-253", "Multivariable Calculus", 3.0),
        ("HQ-006", "Quran Translation - VI", 0.5),
    ],
    7: [
        ("CC-411", "Final Year Project - I", 2.0),
        ("DC-328", "Parallel & Distributed Computing", 3.0),
        ("EC-345", "Computer Vision / Elective", 3.0),
        ("EC-425", "Software Quality Engineering / Elective", 3.0),
        ("MS-254", "Technical and Business Writing", 3.0),
        ("GE-263", "Entrepreneurship", 2.0),
        ("GE-262", "Professional Practices", 2.0),
        ("HQ-007", "Quran Translation - VII", 0.5),
    ],
    8: [
        ("CC-412", "Final Year Project - II", 4.0),
        ("DC-421", "Compiler Construction", 3.0),
        ("UE-272", "Introduction to Marketing", 3.0),
        ("GE-168", "Ideology and Constitution of Pakistan", 2.0),
        ("GE-363", "Civics and Community Engagement", 2.0),
        ("HQ-008", "Quran Translation - VIII", 0.5),
    ],
}



def _number(value: float) -> bool:
    """Check that a value is a real, finite number."""
    return isinstance(value, (int, float)) and not isinstance(value, bool) and isfinite(value)


def _semester(value: int) -> bool:
    """Check that a semester number is valid."""
    return isinstance(value, int) and not isinstance(value, bool) and 1 <= value <= 8


def marks_to_grade_points(marks: int) -> float | str:
    """Use when the student gives marks and asks for grade points."""
    if not isinstance(marks, int) or isinstance(marks, bool) or not 0 <= marks <= 100:
        return "Error: marks must be a whole number from 0 to 100"

    if marks >= 85:
        return 4.0
    if marks >= 80:
        return 3.7
    if marks >= 75:
        return 3.3
    if marks >= 70:
        return 3.0
    if marks >= 65:
        return 2.7
    if marks >= 61:
        return 2.3
    if marks >= 58:
        return 2.0
    if marks >= 55:
        return 1.7
    if marks >= 50:
        return 1.0
    return 0.0


def calculate_semester_gpa(grade_points: list[float], credit_hours: list[float]) -> float | str:
    """Use when all grade points and credit hours for a semester are known."""
    if not isinstance(grade_points, list) or not isinstance(credit_hours, list):
        return "Error: grade points and credit hours must be lists"
    if not grade_points or len(grade_points) != len(credit_hours):
        return "Error: lists must be non-empty and have equal lengths"

    total_points = 0.0
    total_hours = 0.0
    for point, hours in zip(grade_points, credit_hours):
        if not _number(point) or not 0 <= point <= 4:
            return "Error: grade points must be between 0 and 4"
        if not _number(hours) or hours <= 0:
            return "Error: credit hours must be greater than 0"
        total_points += point * hours
        total_hours += hours

    return total_points / total_hours


def calculate_new_cgpa(current_cgpa: float, completed_credit_hours: float,
                       semester_gpa: float, semester_credit_hours: float) -> float | str:
    """Use to find the CGPA after a semester with a known GPA and credit hours."""
    if not _number(current_cgpa) or not 0 <= current_cgpa <= 4:
        return "Error: current CGPA must be between 0 and 4"
    if not _number(semester_gpa) or not 0 <= semester_gpa <= 4:
        return "Error: semester GPA must be between 0 and 4"
    if not _number(completed_credit_hours) or completed_credit_hours < 0:
        return "Error: completed credit hours cannot be negative"
    if not _number(semester_credit_hours) or semester_credit_hours <= 0:
        return "Error: semester credit hours must be greater than 0"

    points = current_cgpa * completed_credit_hours + semester_gpa * semester_credit_hours
    hours = completed_credit_hours + semester_credit_hours
    return points / hours


def required_gpa_for_target(target_cgpa: float, current_cgpa: float,
                            completed_credit_hours: float, remaining_credit_hours: float) -> float | str:
    """Use to find the GPA required over the given future credit hours."""
    if not _number(target_cgpa) or not 0 <= target_cgpa <= 4:
        return "Error: target CGPA must be between 0 and 4"
    if not _number(current_cgpa) or not 0 <= current_cgpa <= 4:
        return "Error: current CGPA must be between 0 and 4"
    if not _number(completed_credit_hours) or completed_credit_hours < 0:
        return "Error: completed credit hours cannot be negative"
    if not _number(remaining_credit_hours) or remaining_credit_hours <= 0:
        return "Error: remaining credit hours must be greater than 0"

    total_hours = completed_credit_hours + remaining_credit_hours
    needed_points = target_cgpa * total_hours - current_cgpa * completed_credit_hours
    return needed_points / remaining_credit_hours


def get_semester_courses(semester: int) -> str:
    """Use to look up a semester's courses, their credits and target-planning hours."""
    if not _semester(semester):
        return "Error: semester must be between 1 and 8"

    lines = [f"Semester {semester} courses:"]
    for code, name, hours in COURSES[semester]:
        lines.append(f"{code}: {name} ({hours:g} credit hours)")

    # A target plan needs cumulative hours; the tool adds them, not the model.
    total = 0.0
    for end in range(semester, 9):
        total += sum(hours for _, _, hours in COURSES[end])
        lines.append(f"Planning hours, semesters {semester} to {end}: {total:.1f}")
    return "\n".join(lines)


def get_remaining_credit_hours(current_semester: int) -> float | str:
    """Use when a student asks how many graded hours remain AFTER a completed semester."""
    if not _semester(current_semester):
        return "Error: semester must be between 1 and 8"
    return sum(hours for sem in range(current_semester + 1, 9)
               for _, _, hours in COURSES[sem])

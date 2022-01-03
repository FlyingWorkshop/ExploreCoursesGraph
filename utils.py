from typing import TypeAlias
import json
import os
import re

import explorecourses
import nltk

CourseID: TypeAlias = int | str

EDIT_DISTANCE_THRESHOLD = 2  # controls how strict we are with typos (low = strict, high = permissive)
CONNECT = explorecourses.CourseConnection()
CACHE_FOLDER = "data"


def _load_cache(year: str, filename: str) -> dict | list[str]:
    filepath = os.path.join(CACHE_FOLDER, year, filename)
    with open(filepath) as f:
        data = json.load(f)
    return data

def load_course_ids(year: str) -> dict:
    return _load_cache(year, "course_ids.json")

def load_departments(year: str) -> dict:
    return _load_cache(year, "departments.json")

def load_prereqs(year: str) -> dict:
    return _load_cache(year, "prereqs.json")

def load_schools(year: str) -> dict:
    return _load_cache(year, "schools.json")

def _get_course(course_id: CourseID, year: str) -> explorecourses.Course:
    query = str(course_id)
    course = CONNECT.get_courses_by_query(query, year)[0]
    return course

def extract_aliases(course: explorecourses.Course):
    """
    >>> extract_aliases(_get_course(217009, "2021-2022"))  # CME 251: Geometric and Topological Data Analysis (CS 233)
    ['CME 251', 'CS 233']
    >>> extract_aliases(_get_course(223024, "2021-2022"))  # GSBGEN 535: Global Trip Leadership Skills (B)
    ['GSBGEN 535']
    >>> extract_aliases(_get_course(220309, "2021-2022"))  # OTOHNS 802: Terminal Graduate Student (TGR) Research
    ['OTOHNS 802']
    """
    aliases = [make_course_name(course)]
    data = load_departments(course.year)
    departments = data.keys()
    matches = [m for m in re.findall(r"\((.*?)\)", course.title)]
    for m in matches:
        if not any(dept in m for dept in departments):
            continue
        aliases += m.split(",")
    return aliases

def inflate(course_name: str) -> str:
    """
    >>> inflate("AA100")
    'AA 100'
    >>> inflate("CME100")
    'CME 100'
    >>> inflate("AA136A")
    'AA 136A'
    >>> inflate("AA274A")
    'AA 274A'
    """
    m = re.search(r"\d", course_name)
    if m:
        s = course_name[:m.start()] + " " + course_name[m.start():]
        return s
    else:
        return course_name

def get_course_ids(course_names, year: str) -> list[CourseID]:
    """
    >>> get_course_ids(['AA100', 'CME100', 'CME102', 'ME70'], "2019-2020")
    ['103093', '202354', '104315', '104789']
    >>> get_course_ids(['AA136A', 'AA236A'], "2021-2022")
    ['103173', '103173']
    >>> get_course_ids(['CS106A', 'CS109', 'EE178', 'ENGR108'], "2021-2022")

    """
    results = []
    data = load_course_ids(year)
    for course_name in course_names:
        course_name = inflate(course_name)
        for course_id, aliases in data.items():
            if course_name in aliases:
                results.append(course_id)
                break
    return results

def _valid_department_code(dept: str, year) -> bool:
    """
    >>> _valid_department_code("MATH", "2020-2021")
    True
    >>> _valid_department_code("OR", "2020-2021")
    False
    """
    data = load_departments(year)
    return dept in data

def _valid_course_name(course_name: str, year) -> bool:
    """
    >>> _valid_course_name("B", year="2021-2022")
    False
    """
    data = load_course_ids(year)
    return any(inflate(course_name) in aliases for aliases in data.values())

def get_subject(course_name: str):
    """
    >>> get_subject("MATH19")
    'MATH'
    >>> get_subject("MATH19-21")
    'MATH'
    >>> get_subject("MATH 19")
    'MATH'
    """
    subject = ""
    m = re.search(r"\d", course_name)
    if m:
        subject = course_name[:m.start()]
    return subject.strip()

def make_course_name(course: explorecourses.Course) -> str:
    return f"{course.subject} {course.code}"

def _unpack_interval(s: str) -> (int, int):
    """
    >>> _unpack_interval("Math 19-21")
    (19, 21)
    """
    start, end = 0, 0
    m = re.search(r"\d", s)
    if m:
        start, end = s[m.start():].split("-")
        start = int(start)
        end = int(end) + 1
    return start, end


def get_prereqs(course: explorecourses.Course) -> list[str]:
    """
    >>> year = "2021-2022"
    >>> get_prereqs(_get_course(117229, year))  # MATH 20: Calculus
    ['MATH19']
    >>> get_prereqs(_get_course(105664, year))  # CME 108: Introduction to Scientific Computing (MATH 114)
    ['CME100', 'CME102', 'CS106A', 'MATH51', 'MATH52', 'MATH53']
    >>> get_prereqs(_get_course(210213, year))  # MATH 228: Stochastic Methods in Engineering (CME 308, MS&E 324)
    []
    >>> get_prereqs(_get_course(219578, year))  # CME 107: Introduction to Machine Learning (EE 104)
    ['CS106A', 'CS109', 'EE178', 'ENGR108']
    >>> get_prereqs(_get_course(221145, year))  # MATH275 Topics in Applied Mathematics
    []
    >>> get_prereqs(_get_course(221549, year))  # AA 146A: Aircraft Design (note: MATH41 is probably supposed to be Physics 41)
    ['AA100', 'MATH20', 'MATH21']
    >>> get_prereqs(_get_course(209786, year))  # BIOE 42: Physical Biology
    ['CHEM31A', 'CHEM31B', 'CME100', 'CME106', 'CS106A', 'MATH19', 'MATH20', 'MATH21', 'MATH51', 'PHYSICS41']
    >>> get_prereqs(_get_course(216444, year))  # CME 250: Introduction to Machine Learning
    []
    >>> get_prereqs(_get_course(122643, year))  # PHYSICS 61: Mechanics and Special Relativity
    ['MATH51', 'MATH61CM', 'MATH61DM']
    >>> get_prereqs(_get_course(104315, year))  # CME 102: Ordinary Differential Equations for Engineers (ENGR 155A)
    ['MATH19', 'MATH20', 'MATH21']
    >>> get_prereqs(_get_course(217009, year))  # CME 251: Geometric and Topological Data Analysis (CS 233)
    ['CS161', 'MATH51']
    >>> get_prereqs(_get_course(214563, year))  # CME 309: Randomized Algorithms and Probabilistic Analysis (CS 265)
    ['CS161', 'STATS116']
    >>> get_prereqs(_get_course(221396, year))  # CS 182W: Ethics, Public Policy, and Technological Change (WIM)
    ['CS106A']
    >>> get_prereqs(_get_course(220404, "2019-2020"))  # AA 102: Introduction to Applied Aerodynamics
    ['AA100', 'CME100', 'CME102', 'ME70']
    >>> get_prereqs(_get_course(103174, "2021-2022"))  # AA 136B: Spacecraft Design Laboratory (AA 236B)
    ['AA136A', 'AA236A']
    """
    # trim description
    m = re.search(r"[Pp]rerequisites?(.*?)\.", course.description)
    if not m:
        return []
    s = course.description[m.start():]
    s = re.sub(r"(Enroll in either.*?\.)|(See.*?for lecture day/time information)", "", s)

    prereqs = set()

    # apply basic strategy
    data = load_departments(course.year)
    departments = data.keys()
    last = make_course_name(course)
    basic_pattern = r"([A-Za-z]*\s*\d+[A-Z]*|\b[A-Z]\b)"
    matches = [re.sub(" ", "", m.upper()) for m in re.findall(basic_pattern, s)]
    for m in matches:
        # basic strategy 1, everything is formatted properly
        if _valid_course_name(m, course.year):
            prereqs.add(m)
            last = m
            continue

        # basic strategy 2, handles cases like 'MATH 51, 52, 53'
        m2 = f"{get_subject(last)}{m}"
        if _valid_course_name(m2, course.year):
            prereqs.add(m2)
            continue

        # basic strategy 3, handles cases like 'CHEM31A, B'
        m3 = f"{last[:-1]}{m}"
        if _valid_course_name(m3, course.year):
            prereqs.add(m3)
            continue

        # basic strategy 4, minor typo in subject like 'STAT116' for 'STATS116'
        subject = get_subject(m)
        if not _valid_department_code(subject, course.year):
            m = m.removeprefix(subject)
            for dept in departments:
                dist = nltk.edit_distance(subject, dept)
                if dist < EDIT_DISTANCE_THRESHOLD:
                    m4 = f"{dept}{m}"
                    if _valid_course_name(m4, course.year):
                        prereqs.add(m4)
                        last = m4
                        break

    # apply hyphen strategy
    hyphen_pattern = r"([a-zA-Z]+\s*\d+-\d+)"
    matches = [re.sub(" ", "", m.upper()) for m in re.findall(hyphen_pattern, s)]
    for m in matches:
        subject = get_subject(m)
        start, end = _unpack_interval(m)
        for i in range(start, end):
            m = f"{subject}{i}"
            if _valid_course_name(m, course.year):
                prereqs.add(m)

    # remove any erroneously-scraped self-references
    course_name = make_course_name(course)
    if course_name in prereqs:
        prereqs.remove(course_name)

    return sorted(prereqs)

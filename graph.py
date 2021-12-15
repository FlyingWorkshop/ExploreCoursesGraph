import re

import explorecourses
import graphviz

import utils

CONNECT = explorecourses.CourseConnection()

def make_url(course_id: utils.CourseID, year: str) -> str:
    """
    >>> make_url(117383, year="2020-2021")
    """
    year = re.sub("-", "", year)
    url = f"https://explorecourses.stanford.edu/search?view=catalog&filter-coursestatus-Active=on&page=0&catalog=&academicYear={year}&q={course_id}&collapse="
    return url

# TODO: look into gzip caching of course objects
# TODO: add coloration to unique department vertices
class Graph:
    def __init__(self, year: str):
        self.year = year
        self.data = {}

    def load(self, courses: list[explorecourses.Course]):
        """
        >>> year = "2020-2021"
        >>> courses = CONNECT.get_courses_by_department("MATH", year)
        >>> graph = Graph(year)
        >>> graph.load(courses)
        >>> graph.data
        """
        if not courses:
            return
        seen = set()
        for course in courses:
            if course.course_id in seen or course.year != self.year:
                continue
            seen.add(course.course_id)
            value = utils.get_prereqs(course)
            if value:
                self.data[course.course_id] = utils.get_course_ids(value, course.year)

    def process(self):
        """
        >>> graph = Graph("2021-2022")
        >>> graph.load(CONNECT.get_courses_by_department("MATH", graph.year))
        >>> graph.process()
        {'MATH20': ['MATH19'], 'MATH51': ['MATH21'], 'MATH52': ['MATH21', 'MATH51'], 'MATH53': ['MATH21', 'MATH51'], 'MATH61DM': ['MATH51'], 'MATH62CM': ['MATH61CM'], 'MATH62DM': ['MATH61DM'], 'MATH63CM': ['MATH61CM', 'MATH61DM'], 'MATH104': ['MATH51'], 'MATH106': ['MATH52'], 'MATH107': ['MATH51'], 'MATH108': ['MATH51'], 'MATH109': ['MATH51'], 'CME108': ['CME100', 'CME102', 'CS106A', 'MATH51', 'MATH52', 'MATH53'], 'MATH115': ['MATH21'], 'MATH116': ['MATH52'], 'MATH118': ['MATH51'], 'MATH120': ['MATH51'], 'MATH121': ['MATH113', 'MATH120'], 'MATH122': ['MATH113', 'MATH120'], 'MATH131P': ['MATH53'], 'MATH136': ['MATH115', 'MATH136', 'MATH151', 'STATS116'], 'MATH137': ['MATH51', 'MATH52', 'MATH53', 'MATH62CM', 'MATH63CM'], 'MATH138': ['MATH53'], 'MATH143': ['MATH53'], 'MATH144': ['MATH113', 'MATH171', 'MATH61CM'], 'MATH147': ['MATH144'], 'MATH148': ['MATH109'], 'MATH151': ['MATH115', 'MATH52', 'MATH61CM'], 'MATH154': ['MATH120'], 'MATH155': ['MATH106', 'MATH152'], 'MATH159': ['MATH151', 'STATS116'], 'MATH171': ['MATH61CM'], 'MATH172': ['MATH171'], 'MATH173': ['MATH171'], 'MATH175': ['MATH115'], 'MATH205A': ['MATH171', 'MATH172'], 'MATH205B': ['MATH171'], 'MATH210A': ['MATH121', 'MATH122', 'MATH145', 'MATH154'], 'MATH210B': ['MATH210A'], 'MATH210C': ['MATH210A'], 'MATH215A': ['MATH120'], 'MATH215B': ['MATH215A'], 'CME303': ['MATH171', 'MATH61CM'], 'CME306': ['CME302', 'CME303'], 'MATH230A': ['MATH171', 'STATS116'], 'MATH230B': ['MATH230A'], 'MATH230C': ['MATH230B'], 'MATH234': ['MATH230A'], 'MATH236': ['MATH136'], 'MATH238': ['MATH136'], 'MATH243': ['MATH215A'], 'MATH244': ['MATH106', 'MATH116', 'MATH143', 'MATH147']}
        """
        index = utils.load_course_ids(self.year)
        processed = {}
        for course_id, prereq_ids in self.data.items():
            course_name = index[str(course_id)][0]
            processed[course_name] = []
            for prereq_id in prereq_ids:
                prereq_name = index[str(prereq_id)][0]
                processed[course_name].append(prereq_name)
        return processed

    def display(self):
        g = graphviz.Digraph()
        processed = self.process()
        for course_name, prereq_names in processed.items():
            for prereq_name in prereq_names:
                g.edge(course_name, prereq_name)
        return g

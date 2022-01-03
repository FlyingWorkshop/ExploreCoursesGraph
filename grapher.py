import random

import explorecourses
import graphviz

import cacher
import utils


class Graph:
    def __init__(self, year: str, lazy=False):
        self.year = year

        connect = explorecourses.CourseConnection()
        cacher.cache_course_ids(connect, year, lazy)
        cacher.cache_departments(connect, year, lazy)
        cacher.cache_prereqs(connect, year, lazy)
        cacher.cache_schools(connect, year, lazy)

        self._schools = utils.load_schools(self.year)
        self._prereqs = utils.load_prereqs(self.year)
        self._departments = utils.load_departments(self.year)
        self._course_ids = utils.load_course_ids(self.year)

    def get_dept_courses(self, dept: str):
        school = self._schools[dept]
        prereqs = self._prereqs[school][dept]
        return prereqs

    def get_course_name(self, course_id) -> str:
        course_name = self._course_ids[course_id][0]  # defaults to the first name in the list of aliases
        utils.get_subject(course_name)
        return course_name

    @staticmethod
    def get_color():
        rgb = "#{:02X}{:02X}{:02X}".format(random.randrange(0, 256),
                                           random.randrange(0, 256),
                                           random.randrange(0, 256))
        return rgb


    def graph_depts(self, *depts: str, format="png", save_file=False):
        # get data
        graph_data = {}
        for dept in depts:
            courses = self.get_dept_courses(dept)
            for course_id, prereq_ids in courses.items():
                course_name = self.get_course_name(course_id)
                if course_name not in graph_data:
                    graph_data[course_name] = set()
                graph_data[course_name].update([self.get_course_name(prereq_id) for prereq_id in prereq_ids])

        # make digraph
        colors = {}
        digraph = graphviz.Digraph(format=format)
        digraph.graph_attr.update(rankdir="LR")
        for course_name, prereq_names in graph_data.items():
            subject = utils.get_subject(course_name)
            if subject not in colors:
                colors[subject] = self.get_color()
            digraph.node(course_name, color=colors[subject], style="filled", fillcolor=colors[subject] + "32")
            for prereq_name in prereq_names:
                subject = utils.get_subject(prereq_name)
                if subject not in colors:
                    colors[subject] = self.get_color()
                digraph.node(prereq_name, color=colors[subject], style="filled", fillcolor=colors[subject] + "32")
                digraph.edge(prereq_name, course_name)
        if save_file:
            digraph.render(f"output/{input('Choose a filename')}.gv")
        return digraph

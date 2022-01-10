document.getElementById("mySearchBox")
    .addEventListener("keyup", function(event) {
    event.preventDefault();
    if (event.key === "Enter") {
        document.getElementById("myButton").click();
    }
});

function getRandomColorAttr() {
    return '#'+(Math.random() * 0xFFFFFF << 0).toString(16).padStart(6, '0');
}

function makeNodeAttrs(colorMap, year, course_data) {
    if (!colorMap.has(course_data.subject)) {
        colorMap.set(course_data.subject, getRandomColorAttr());
    }
    let course_url = 'https://explorecourses.stanford.edu/search?view=catalog&filter-coursestatus-Active=on&page=0&catalog=' +
        '&academicYear=' + year.slice(0, 4) + year.slice(5, 9) +
        '&q=' + course_data.course_id +
        '&collapse=';
    return course_data.course_id + ' [' +
        'label="' + course_data.subject + " " + course_data.code + '" ' +
        'tooltip="' + course_data.title + '" ' +
        'color="' + colorMap.get(course_data.subject) + '" ' +
        'fillcolor="' + colorMap.get(course_data.subject) + '32" ' +
        'URL="' + course_url + '"]';
}


function parseDepartmentQuery(text) {
    let s = text.trim().toUpperCase();
    const deptCodes = new Set();
    for (const elem of s.split(",")) {
        deptCodes.add(elem.trim());
    }
    return deptCodes;
}

function parseCourseNameQuery(text) {
    const courseNames = new Set();
    const parts = text.replaceAll(" ", "").toUpperCase().split(",");
    for (let s of parts) {
        let subject = s.match(/\D+/)[0];
        let code = s.slice(s.indexOf(subject) + subject.length, s.length);
        let courseName = subject + " " + code;
        courseNames.add(courseName);
    }
    return courseNames;
}

function addNode(courseData, colorMap, year,existingNodes, graphvizParts) {
    let courseAttrs = makeNodeAttrs(colorMap, year, courseData);
    graphvizParts.push(courseAttrs);
    existingNodes.add(Number(courseData.course_id));
}

function printSet(s) {
    let temp = [];
    for (let elem of s) {
        temp.push(elem);
    }
    alert(temp);
}


document.getElementById("myButton").addEventListener("click", function() {
    // construct the URL
    let year = document.getElementById("years").value;
    let url = "https://flyingworkshop.github.io/ExploreCoursesGraph/cache/" + year + ".json";

    const text = document.getElementById("mySearchBox").value;
    const colorMap = new Map();
    let existingNodes = new Set();
    let graphvizParts = ['digraph {graph [rankdir=LR, ranksep=0.3, nodesep=0.2] node [shape=record, style=filled] edge [arrowsize=0.5]'];

    if (/\d/.test(text)) {
        const courseNames = parseCourseNameQuery(text);
        const courseIDs = new Set();
        let aliasesURL = "https://flyingworkshop.github.io/ExploreCoursesGraph/cache/course_ids" + year + ".json";
        $.getJSON(aliasesURL, function(aliasData) {
            // get all courseIDs
            $.each(aliasData, function (aliasID, aliasList) {
                if (aliasList.some(alias => courseNames.has(alias))) {
                    courseIDs.add(aliasID);
                }
            });

            const processing = new Set();
            for (let courseID of courseIDs) {
                processing.add(courseID);
            }
            // printSet(processing);
            const processed = new Set();

            const validCourseIDs = new Set();

            $.getJSON(url, function (data) {

                $.each(data, function(courseID, _) {
                    validCourseIDs.add(courseID);
                });

                while (processing.size !== 0) {
                    $.each(data, function (courseID, courseData) {
                        if (processing.has(courseID)) {
                            processing.delete(courseID);
                            // printSet(processing);
                            if (!existingNodes.has(Number(courseID))) {
                                addNode(courseData, colorMap, year, existingNodes, graphvizParts);
                            }
                            processed.add(courseID);

                            for (let prereqID of courseData.prerequisites) {
                                if (validCourseIDs.has(prereqID.toString())) {
                                    $.each(data, function (id, prereqData) {
                                        if (Number(id) === prereqID) {
                                            if (!existingNodes.has(prereqID)) {
                                                addNode(prereqData, colorMap, year, existingNodes, graphvizParts);
                                            }
                                            if (id !== courseID) {
                                                graphvizParts.push(prereqID.toString() + " -> " + courseID + ' [color="' + colorMap.get(prereqData.subject) + 'BE"]');
                                            }
                                            return false;
                                        }
                                    });
                                    // graphvizParts.push(prereqID.toString() + " -> " + courseID + ' [color="' + colorMap.get(prereq_data.subject) + 'BE"]');
                                }
                                if (!processed.has(prereqID.toString())) {
                                    processing.add(prereqID.toString());
                                }
                            }
                        }
                    });

                    for (let courseID of processing) {
                        if (!validCourseIDs.has(courseID)) {
                            processing.delete(courseID);
                            processed.add(courseID);
                        }
                    }
                }
                let graphvizString = graphvizParts.join(" ") + "}";
                d3.select("#graph").graphviz().renderDot(graphvizString);
            });
        });

    } else {
        const deptCodes = parseDepartmentQuery(text);

        for (const deptCode of deptCodes) {
            colorMap.set(deptCode, getRandomColorAttr());
        }
        $.getJSON(url, function (data) {
            $.each(data, function (course_id, course_data) {
                if (deptCodes.has(course_data.subject)) {
                    $.each(course_data.prerequisites, function (i, prereq) {
                        $.each(data, function (prereq_id, prereq_data) {
                            if (prereq === Number(prereq_id) && prereq_id !== course_id) {
                                if (!existingNodes.has(Number(course_id))) {
                                    let courseAttrs = makeNodeAttrs(colorMap, year, course_data);
                                    graphvizParts.push(courseAttrs);
                                    existingNodes.add(Number(course_id));
                                }
                                let prereqAttrs = makeNodeAttrs(colorMap, year, prereq_data);
                                graphvizParts.push(prereqAttrs);
                                existingNodes.add(prereq);
                                graphvizParts.push(prereq + " -> " + course_id + ' [color="' + colorMap.get(prereq_data.subject) + 'BE"]');
                            }
                        });
                    });
                }
            });
            let graphvizString = graphvizParts.join(" ") + "}";
            d3.select("#graph").graphviz().renderDot(graphvizString);
        });
    }
});

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

document.getElementById("myButton").addEventListener("click", function() {
    // construct the URL
    let year = document.getElementById("years").value;
    let url = "https://flyingworkshop.github.io/ExploreCoursesGraph/cache/" + year + ".json";

    const text = document.getElementById("mySearchBox").value;
    const colorMap = new Map();
    let existingNodes = new Set();
    let graphvizParts = ['digraph {graph [rankdir=LR, ranksep=0.3, nodesep=0.2] node [shape=record, style=filled] edge [arrowsize=0.5]'];

    if (/\d/.test(text)) {
        let deptCode = text.match(/\D+/)[0];
        let courseCode = text.slice(text.indexOf(deptCode) + deptCode.length, text.length);
        deptCode = deptCode.trim().toUpperCase();
        courseCode = courseCode.trim().toUpperCase();

        let alias_url = "https://flyingworkshop.github.io/ExploreCoursesGraph/cache/course_ids" + year + ".json";

        $.getJSON(url, function (data) {
            let target_id = "";

            $.getJSON(alias_url, function (alias_data) {
                let course_name = deptCode + " " + courseCode;
                $.each(alias_data, function (id, alias_list) {
                    if (alias_list.includes(course_name)) {
                        target_id = id;
                        return false;
                    }
                });

                $.each(data, function (course_id, course_data) {
                    if (course_id === target_id) {
                        deptCode = course_data.subject;
                        let courseAttrs = makeNodeAttrs(colorMap, year, course_data);
                        graphvizParts.push(courseAttrs);
                        existingNodes.add(Number(course_id));

                        $.each(course_data.prerequisites, function (i, prereq) {
                            $.each(data, function (prereq_id, prereq_data) {
                                if (prereq === Number(prereq_id) && prereq_id !== course_id) {
                                    let prereqAttrs = makeNodeAttrs(colorMap, year, prereq_data);
                                    graphvizParts.push(prereqAttrs);
                                    existingNodes.add(prereq);
                                    graphvizParts.push(prereq + " -> " + course_id + ' [color="' + colorMap.get(prereq_data.subject) + 'BE"]');
                                }
                            });
                        });
                    }
                });

                $.each(data, function (course_id, course_data) {
                    if (course_data.prerequisites.includes(Number(target_id))) {
                        if (!existingNodes.has(Number(course_id))) {
                            let courseAttrs = makeNodeAttrs(colorMap, year, course_data);
                            graphvizParts.push(courseAttrs);
                            existingNodes.add(Number(course_id));
                        }
                        graphvizParts.push(target_id + " -> " + course_id + ' [color="' + colorMap.get(deptCode) + 'BE"]');
                    }
                });
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
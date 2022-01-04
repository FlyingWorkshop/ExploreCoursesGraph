// TODO: debug CS 2021-2022

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

function makeNodeAttrs(colorMap, year, course_id, course_data) {
    let course_url = 'https://explorecourses.stanford.edu/search?view=catalog&filter-coursestatus-Active=on&page=0&catalog=' +
        '&academicYear=' + year.slice(0, 4) + year.slice(5, 9) +
        '&q=' + course_id +
        '&collapse=';
    return course_id + ' [' +
        'label="' + course_data.subject + " " + course_data.code + '" ' +
        'tooltip="' + course_data.title + '" ' +
        'color="' + colorMap.get(course_data.subject) + '" ' +
        'style="filled" ' +
        'fillcolor="' + colorMap.get(course_data.subject) + '32" ' +
        'URL="' + course_url + '"]';
}

document.getElementById("myButton").addEventListener("click", function() {

    // construct the URL
    let year = document.getElementById("years").value;
    let url = "https://flyingworkshop.github.io/ExploreCoursesGraph/cache/" + year + ".json";

    const text = document.getElementById("mySearchBox").value;
    const deptCodes = new Set(text.split(","));
    // TODO: add support for queries with spaces i.e. "MATH, ECON" rather than only "MATH,ECON"

    const colorMap = new Map();
    for (const deptCode of deptCodes) {
        colorMap.set(deptCode, getRandomColorAttr());
    }

    let prereqs = new Set();
    let graphvizParts = ['digraph {graph [rankdir=LR]'];

    $.getJSON(url, function(data) {
        $.each(data, function(course_id, course_data) {
            if (deptCodes.has(course_data.subject)) {
                let nodeAttrs = makeNodeAttrs(colorMap, year, course_id, course_data);
                let hasPrereqs = false;
                $.each(course_data.prerequisites, function (i, prerequisite) {
                    hasPrereqs = true;
                    prereqs.add(prerequisite);
                    graphvizParts.push(prerequisite + " -> " + course_data.course_id);
                });
                if (hasPrereqs) {
                    graphvizParts.push(nodeAttrs);
                }
            }
        });

        $.each(data, function(course_id, course_data) {
            if (prereqs.has(Number(course_id))) {
                if (!colorMap.has(course_data.subject)) {
                    colorMap.set(course_data.subject, getRandomColorAttr());
                }
                let nodeAttrs = makeNodeAttrs(colorMap, year, course_id, course_data);
                graphvizParts.push(nodeAttrs);
            }
        });

        let graphvizString = graphvizParts.join(" ") + "}";
        d3.select("#graph").graphviz().renderDot(graphvizString);
    });
});
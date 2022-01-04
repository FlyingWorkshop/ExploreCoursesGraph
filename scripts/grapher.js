// construct the URL
let year = prompt("Enter an academic year: ", "2020-2021");
let url = "https://flyingworkshop.github.io/ExploreCoursesGraph/cache/" + year + ".json";

// TODO: extend to multiple departments
let deptCode = prompt("Enter a valid department code: ", "MATH");


function getRandomColorAttr() {
    return '#'+(Math.random() * 0xFFFFFF << 0).toString(16).padStart(6, '0');
}

const colorMap = new Map();
colorMap.set(deptCode, getRandomColorAttr());

let prereqs = new Set();
let graphvizParts = ['digraph {graph [rankdir=LR] ']

$.getJSON(url, function(data) {
    // let graphvizParts = ['digraph {graph [rankdir=LR] ']
    $.each(data, function(course_id, course_data) {
        if (course_data.subject === deptCode) {
            let course_url = 'https://explorecourses.stanford.edu/search?view=catalog&filter-coursestatus-Active=on&page=0&catalog=' +
                '&academicYear=' + year.slice(0, 4) + year.slice(5, 9) +
                '&q=' + course_id +
                '&collapse=';
            let nodeAttrs = course_id + ' [' +
                'label="' + course_data.subject + " " + course_data.code + '" ' +
                'tooltip="' + course_data.title + '" ' +
                'color="' + colorMap.get(course_data.subject) + '" ' +
                'style="filled" ' +
                'fillcolor="' + colorMap.get(course_data.subject) + '32" ' +
                'URL="' + course_url + '"]';

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

            let course_url = 'https://explorecourses.stanford.edu/search?view=catalog&filter-coursestatus-Active=on&page=0&catalog=' +
                '&academicYear=' + year.slice(0, 4) + year.slice(5, 9) +
                '&q=' + course_id +
                '&collapse=';
            let nodeAttrs = course_id + ' [' +
                'label="' + course_data.subject + " " + course_data.code + '" ' +
                'tooltip="' + course_data.title + '" ' +
                'color="' + colorMap.get(course_data.subject) + '" ' +
                'style="filled" ' +
                'fillcolor="' + colorMap.get(course_data.subject) + '32" ' +
                'URL="' + course_url + '"]';
            graphvizParts.push(nodeAttrs);
        }
    });

    let graphvizString = graphvizParts.join(" ") + "}"
    d3.select("#graph").graphviz().renderDot(graphvizString);
});
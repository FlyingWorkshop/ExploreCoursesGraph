// TODO: figure out how to pick correct url

// construct the URL
let year = prompt("Enter an academic year: ", "2020-2021");
let fileName = year + ".json"
let urlBase = "https://flyingworkshop.github.io/ExploreCoursesGraph/cache/";
let url = urlBase + fileName;

// TODO: extend to multiple departments
let deptCode = prompt("Enter a valid department code: ", "MATH");

// TODO: convert IDs to course names ideally using the course number as the node ID
// TODO: read up on graphviz documentation
$.getJSON(url, function(data) {
    let graphvizParts = ['digraph {graph [rankdir=LR]']
    $.each(data, function(course_id, course_data) {
        if (course_data.subject === deptCode) {
            $.each(course_data.prerequisites, function(i, prerequisite) {
                graphvizParts.push(prerequisite + " -> " + course_data.course_id);
            });
        }
    });
    let graphvizString = graphvizParts.join(" ") + "}"
    d3.select("#graph").graphviz().renderDot(graphvizString);
});
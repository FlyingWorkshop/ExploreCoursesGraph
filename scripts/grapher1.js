// TODO: figure out why graph doesn't display labels in chrome and only in incognito + safari?

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
    let graphvizParts = ['digraph {graph [rankdir=LR] ']
    $.each(data, function(course_id, course_data) {
        if (course_data.subject === deptCode) {
            let label = course_data.subject + " " + course_data.code;
            let tooltip = course_data.title;
            let course_url = 'https://explorecourses.stanford.edu/search?view=catalog&filter-coursestatus-Active=on&page=0&catalog=' +
                '&academicYear=20202021' + // TODO: make this more specific by doing some string processing
                '&q=' + course_data.course_id +
                '&collapse=';
            // graphvizParts.push(course_data.course_id + ' [label="' + label + '" tooltip="' + tooltip + '" URL="' + course_url + '"]')
            let hasPrereqs = false;
            $.each(course_data.prerequisites, function(i, prerequisite) {
                hasPrereqs = true;
                graphvizParts.push(prerequisite + " -> " + course_data.course_id);
            });
            if (hasPrereqs) {
                graphvizParts.push(course_data.course_id + ' [label="' + label + '" tooltip="' + tooltip + '" URL="' + course_url + '"]')
            }
        }
    });
    let graphvizString = graphvizParts.join(" ") + "}"
    // alert(graphvizString);
    d3.select("#graph").graphviz().renderDot(graphvizString);
});
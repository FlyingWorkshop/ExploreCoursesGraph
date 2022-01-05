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

document.getElementById("myButton").addEventListener("click", function() {

    // construct the URL
    let year = document.getElementById("years").value;
    let url = "https://flyingworkshop.github.io/ExploreCoursesGraph/cache/" + year + ".json";

    const text = document.getElementById("mySearchBox").value;
    const deptCodes = new Set(text.split(","));

    const colorMap = new Map();
    for (const deptCode of deptCodes) {
        colorMap.set(deptCode, getRandomColorAttr());
    }

    let existingNodes = new Set();
    let graphvizParts = ['digraph {graph [rankdir=LR, ranksep=0.3, nodesep=0.2] node [shape=record, style=filled] edge [arrowsize=0.5]'];

    $.getJSON(url, function(data) {

         $.each(data, function(course_id, course_data) {
             if (deptCodes.has(course_data.subject)) {
                 $.each(course_data.prerequisites, function (i, prereq) {
                     $.each(data, function(prereq_id, prereq_data) {
                         if (!existingNodes.has(Number(course_id))) {
                             let courseAttrs = makeNodeAttrs(colorMap, year, course_data);
                             graphvizParts.push(courseAttrs);
                             existingNodes.add(Number(course_id));
                         }

                         if (prereq === Number(prereq_id)) {
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
});

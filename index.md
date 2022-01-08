<meta charset="utf-8">
<head>
    <title>Visualize Stanford Prerequisites</title>
</head>
<body>
<script src="https://ajax.googleapis.com/ajax/libs/jquery/3.5.1/jquery.min.js"></script>
<script src="//d3js.org/d3.v5.min.js"></script>
<script src="https://unpkg.com/@hpcc-js/wasm@0.3.11/dist/index.min.js"></script>
<script src="https://unpkg.com/d3-graphviz@3.0.5/build/d3-graphviz.js"></script>
<div>
    <p>
        Instructions:
        Select an academic year and then enter a query.

        Currently, two types of queries are supported:
        (1) Department query: Enter a department code (like "ECON", "MATH", "BIO") or multiple departments (like "ME, EE, CS"). This will create a graph of all of the courses in the department and each course's 1-layer deep prerequisites.
        (2) Class query: Enter a class name (like "MATH 51" or class names (like "CS 229, MATH 171"). This will create a graph of all the courses specified (if they are valid course names) and graph all perquisites for the course. It will also graph prerequisites for prerequisites.
    </p>
    <select name="years" id="years">
        <option value="2021-2022">2021-2022</option>
        <option value="2020-2021">2020-2021</option>
        <option value="2019-2020">2019-2020</option>
    </select>
    <input type="search" id="mySearchBox" name="q" style="border: thin solid black">
    <button id="myButton">Search</button>
</div>
<div id="graph" style="text-align: center; border: thin solid black"></div>
<script src="scripts/grapher.js"></script>
</body>

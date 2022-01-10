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
        <br>
        Select an academic year and then enter a query.
        <br>
        <br>
        Query Types:
        <ul>
        <li> Department Query: Enter a department code (e.g. "ECON", "MATH", "BIO") or multiple departments (e.g. "ME, EE, CS"). This will create a graph of all the courses in the department and their prerequisites (1-layer deep).
    </li>
        <li> Class Query: Enter a class name (e.g. "MATH 51") or class names (e.g. "CS 229, MATH 171"). This will create a graph of all the courses specified and graph all perquisites for the course (max layers).
    </li>
        </ul>
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

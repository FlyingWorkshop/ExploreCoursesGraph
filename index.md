<meta charset="utf-8">
<head>
    <title>Visualize Stanford Prerequisites</title>
</head>
<body>
<!--<label for="years">Choose an academic year:</label>-->
<!--<select id="years" name="cars">-->
<!--  <option value="2019-2020">2019-2020</option>-->
<!--  <option value="2020-2021">2020-2021</option>-->
<!--  <option value="2021-2022">2021-2022</option>-->
<!--</select>-->
<!--<form action="/action_page.php">-->
<!--  <label for="dept">Department Code:</label><br>-->
<!--  <input type="text" id="dept" value="MATH"><br><br>-->
<!--  <input type="submit" value="Submit">-->
<!--</form>-->
<script src="https://ajax.googleapis.com/ajax/libs/jquery/3.5.1/jquery.min.js"></script>
<script src="//d3js.org/d3.v5.min.js"></script>
<script src="https://unpkg.com/@hpcc-js/wasm@0.3.11/dist/index.min.js"></script>
<script src="https://unpkg.com/d3-graphviz@3.0.5/build/d3-graphviz.js"></script>
<div id="graph" style="text-align: center;"></div>
<script src="scripts/grapher.js"></script>
</body>

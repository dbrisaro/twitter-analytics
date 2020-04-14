function renderTweets(api, user, element) {
    url = api + "/users/" + user + "/tweets";

    var req = new XMLHttpRequest();

    req.onreadystatechange = function () {
        if (this.readyState == 4 && this.status == 200) {
            var table = $('#tweets').DataTable({
                data: JSON.parse(this.responseText),
                order: [[3, "desc"]],
                fixedHeader: true,
                scrollY: '350px',
                columns: [
                    { data: 'id', title: 'ID' },
                    { data: 'text', title: 'Text' },
                    { data: 'likes', title: 'Likes' },
                    { data: 'retweets', title: 'Retweets' },
                    { data: 'replies', title: 'Replies' }
                ]
            });
            $('.dataTables_length').addClass('bs-select');

            $('#tweets').on('click', 'tbody tr', function () {
                rowData = table.row(this).data();
                console.log('API row values : ', table.row(this).data());
                renderTweetSnapshots(api, rowData['id'], "retweets", "likes", "tweet-snapshot-view")
            })
        } else {
            console.log(this.status)
        }
    }
    req.open('GET', url, true);
    req.send();
}

function renderTimeChart(api, user, element, xAxis, yAxis) {
    url = api + "/users/" + user + "/snapshots";
    // set the dimensions and margins of the graph
    var margin = { top: 20, right: 20, bottom: 30, left: 50 },
        width = 960 - margin.left - margin.right,
        height = 500 - margin.top - margin.bottom;

    // set the ranges
    var x = d3.scaleTime().range([0, width]);
    var y = d3.scaleLinear().range([height, 0]);

    // define the line
    var valueline = d3.line()
        .x(function (d) { return x(d.Date); })
        .y(function (d) { return y(d.Followers); });

    // append the svg object to the body of the page
    // appends a 'group' element to 'svg'
    // moves the 'group' element to the top left margin
    var svg = d3.select("#" + element).append("svg")
        .attr("width", width + margin.left + margin.right)
        .attr("height", height + margin.top + margin.bottom)
        .append("g")
        .attr("transform",
            "translate(" + margin.left + "," + margin.top + ")");

    function draw(data) {
        // format the data
        data.forEach(function (d) {
            d.Date = d3.isoParse(d[xAxis]);
            //console.log(d.Date)
            d.Followers = +d[yAxis];
            //console.log(d.Followers)
        });

        // sort years ascending
        data.sort(function (a, b) {
            return a["Date"] - b["Date"];
        })

        // Scale the range of the data
        x.domain(d3.extent(data, function (d) { return d.Date; }));
        y.domain(d3.extent(data, function (d) { return d.Followers }));

        // Add the valueline path.
        svg.append("path")
            .data([data])
            .attr("class", "line")
            .attr("d", valueline);

        // Add the X Axis
        svg.append("g")
            .attr("transform", "translate(0," + height + ")")
            .call(d3.axisBottom(x));

        // Add the Y Axis
        svg.append("g")
            .call(d3.axisLeft(y));
    }

    // Get the data
    d3.json(url).then(function (data) {
        // trigger render
        draw(data);
    }).catch(function (error) {
        console.log(error)
    });
}

function renderHeatmap(api, type, user, property, element) {
    url = api + "/users/" + user + "/stats/" + type;

    // set the dimensions and margins of the graph
    var margin = { top: 80, right: 25, bottom: 30, left: 40 },
        width = 450 - margin.left - margin.right,
        height = 450 - margin.top - margin.bottom;

    // append the svg object to the body of the page
    var svg = d3.select("#" + element)
        .append("svg")
        .attr("width", width + margin.left + margin.right)
        .attr("height", height + margin.top + margin.bottom)
        .append("g")
        .attr("transform",
            "translate(" + margin.left + "," + margin.top + ")");

    //Read the data
    var render = function (data, property, element) {

        // Labels of row and columns -> unique identifier of the column called 'group' and 'variable'
        var myGroups = d3.map(data, function (d) { return d.day_of_week; }).keys()
        var myVars = d3.map(data, function (d) { return d.tweet_hour; }).keys()

        myVars.sort()


        const sorter = {
            // "sunday": 0, // << if sunday is first day of week
            "monday": 1,
            "tuesday": 2,
            "wednesday": 3,
            "thursday": 4,
            "friday": 5,
            "saturday": 6,
            "sunday": 7
        }

        myGroups.sort(function sortByDay(a, b) {
            let day1 = a.toLowerCase();
            let day2 = b.toLowerCase();
            return sorter[day1] - sorter[day2];
        });

        // Build X scales and axis:
        var x = d3.scaleBand()
            .range([0, width])
            .domain(myGroups)
            .padding(0.05);
        svg.append("g")
            .style("font-size", 15)
            .attr("transform", "translate(0," + height + ")")
            .call(d3.axisBottom(x).tickSize(0))
            .select(".domain").remove()

        // Build Y scales and axis:
        var y = d3.scaleBand()
            .range([height, 0])
            .domain(myVars)
            .padding(0.05);
        svg.append("g")
            .style("font-size", 15)
            .call(d3.axisLeft(y).tickSize(0))
            .select(".domain").remove()

        // Build color scale
        var maxValue = d3.max(data, function (d) {
            return +d[property]; //<-- convert to number
        })

        var myColor = d3.scaleSequential()
            .interpolator(d3.interpolateBuPu)
            .domain([0, maxValue])

        // create a tooltip
        console.log("Element: ", element)
        var tooltip = d3.select("#" + element)
            .append("div")
            .style("opacity", 0)
            .attr("class", "tooltip")
            .style("background-color", "white")
            .style("border", "solid")
            .style("border-width", "2px")
            .style("border-radius", "5px")
            .style("padding", "5px")

        // Three function that change the tooltip when user hover / move / leave a cell
        var mouseover = function (d) {
            tooltip
                .style("opacity", 1)
            d3.select(this)
                .style("stroke", "black")
                .style("opacity", 1)
        }
        var mousemove = function (d) {
            tooltip
                .html(d[property])
                .style("left", (event.pageX + "px"))
                .style("top", (event.pageY + "px"))
        }
        var mouseleave = function (d) {
            tooltip
                .style("opacity", 0)
            d3.select(this)
                .style("stroke", "none")
                .style("opacity", 0.8)
        }

        var fillRectangle = function (d, property) { return myColor(d[property]) }

        // add the squares
        svg.selectAll()
            .data(data, function (d) { return d.day_of_week + ':' + d.tweet_hour; })
            .enter()
            .append("rect")
            .attr("x", function (d) { return x(d.day_of_week) })
            .attr("y", function (d) { return y(d.tweet_hour) })
            .attr("rx", 4)
            .attr("ry", 4)
            .attr("width", x.bandwidth())
            .attr("height", y.bandwidth())
            .style("fill", data => fillRectangle(data, property))
            .style("stroke-width", 4)
            .style("stroke", "none")
            .style("opacity", 0.8)
            .on("mouseover", mouseover)
            .on("mousemove", mousemove)
            .on("mouseleave", mouseleave)
    };

    d3.json(url).then(value => render(value, property, element));
}

function renderBarChart(api, type, user, property, element) {
    url = api + "/users/" + user + "/stats/" + type;

    var margin = { top: 20, right: 20, bottom: 30, left: 40 },
        width = 960 - margin.left - margin.right,
        height = 500 - margin.top - margin.bottom;

    var x = d3.scaleBand()
        .range([0, width])
        .padding(0.1);
    var y = d3.scaleLinear()
        .range([height, 0]);

    var svg = d3.select("#" + element).append("svg")
        .attr("width", width + margin.left + margin.right)
        .attr("height", height + margin.top + margin.bottom)
        .append("g")
        .attr("transform",
            "translate(" + margin.left + "," + margin.top + ")");

    var processData = function (data, property) {

        console.log("Data: " + data);
        // format the data
        data.forEach(function (d) {
            d[property] = +d[property];
            console.log(d[property])
        });

        // Scale the range of the data in the domains
        x.domain(data.map(function (d) { return d.aggregatedate; }));
        y.domain([0, d3.max(data, function (d) { return d[property]; })]);

        // append the rectangles for the bar chart
        svg.selectAll(".bar")
            .data(data)
            .enter().append("rect")
            .attr("class", "bar")
            .attr("x", function (d) { return x(d.aggregatedate); })
            .attr("width", x.bandwidth())
            .attr("y", function (d) { return y(d[property]); })
            .attr("height", function (d) { return height - y(d[property]); });

        // add the x Axis
        svg.append("g")
            .attr("transform", "translate(0," + height + ")")
            .call(d3.axisBottom(x));

        // add the y Axis
        svg.append("g")
            .call(d3.axisLeft(y));

    };

    // get the data
    d3.json(url).then(data => processData(data, property));
}

function renderTweetSnapshots(api, id, propertyA, propertyB, element) {
    url = api + "/tweets/" + id + "/snapshots";

    $("#" + element).html("");

    var processData = function (data, propertyA, propertyB) {
        data = data.map(i => {
            i.time_of_capture = i.time_of_capture;
            return i;
        });

        var container = d3.select('#' + element),
            width = 900,
            height = 300,
            margin = { top: 30, right: 20, bottom: 30, left: 50 },
            barPadding = .2,
            axisTicks = { qty: 5, outerSize: 0, dateFormat: '%m-%d' };

        var svg = container
            .append("svg")
            .attr("width", width)
            .attr("height", height)
            .append("g")
            .attr("transform", `translate(${margin.left},${margin.top})`);

        var xScale0 = d3.scaleBand().range([0, width - margin.left - margin.right]).padding(barPadding);
        var xScale1 = d3.scaleBand();
        var yScale = d3.scaleLinear().range([height - margin.top - margin.bottom, 0]);

        var xAxis = d3.axisBottom(xScale0).tickSizeOuter(axisTicks.outerSize);
        var yAxis = d3.axisLeft(yScale).ticks(axisTicks.qty).tickSizeOuter(axisTicks.outerSize);

        xScale0.domain(data.map(d => d.time_of_capture));
        xScale1.domain([propertyA, propertyB]).range([0, xScale0.bandwidth()]);
        yScale.domain([0, d3.max(data, d => d[propertyA] > d[propertyB] ? d[propertyA] : d[propertyB])]);

        console.log(data)
        var model_name = svg.selectAll(".time_of_capture")
            .data(data)
            .enter().append("g")
            .attr("class", "time_of_capture")
            .attr("transform", d => `translate(${xScale0(d.time_of_capture)},0)`);

        /* Add field1 bars */
        model_name.selectAll(".bar." + propertyA)
            .data(d => [d])
            .enter()
            .append("rect")
            .attr("class", "bar " + propertyA)
            .style("fill", "blue")
            .attr("x", d => xScale1(propertyA))
            .attr("y", d => yScale(d[propertyA]))
            .attr("width", xScale1.bandwidth())
            .attr("height", d => {
                return height - margin.top - margin.bottom - yScale(d[propertyA])
            });

        /* Add field2 bars */
        model_name.selectAll(".bar." + propertyB)
            .data(d => [d])
            .enter()
            .append("rect")
            .attr("class", "bar " + propertyB)
            .style("fill", "red")
            .attr("x", d => xScale1(propertyB))
            .attr("y", d => yScale(d[propertyB]))
            .attr("width", xScale1.bandwidth())
            .attr("height", d => {
                return height - margin.top - margin.bottom - yScale(d[propertyB])
            });

        // Add the X Axis
        svg.append("g")
            .attr("class", "x axis")
            .attr("transform", `translate(0,${height - margin.top - margin.bottom})`)
            .call(xAxis);

        // Add the Y Axis
        svg.append("g")
            .attr("class", "y axis")
            .call(yAxis);

    };

    // get the data
    d3.json(url).then(data => processData(data, propertyA, propertyB));
}
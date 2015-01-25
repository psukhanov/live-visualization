var margin = {
    // top: 40,
    // right: 40,
    // bottom: 40,
    // left: 120
},
    // width = 960 - margin.left - margin.right,
    width = 280,
    // height = 500 - margin.top - margin.bottom;
    height = 280;

var y = d3.scale.ordinal().domain(d3.range(1)).rangePoints([0, height]);

var svg = d3.select("#bloom")
    .append("svg")
    .attr("width", width + margin.left + margin.right)
    .attr("height", height + margin.top + margin.bottom)
    .append("g").attr("transform", "translate(" + margin.left + "," + margin.top + ")");
svg.selectAll("circle")
    .data(y.domain())
    .enter()
    .append("circle")
    .attr("stroke-width", 20)
    .attr("r", 10)
    .attr("cx", width / 2)
    .attr("cy", y)
    .each(pulse);

function pulse() {
    var circle = svg.select("circle");
    (function repeat() {
        circle = circle.transition()
            .duration(4500)
            .attr("stroke-width", 20)
            .attr("r", 10)
            .transition()
            .duration(4500)
            .attr('stroke-width', 0.5)
            .attr("r", 125)
            .ease('sine')
            .each("end", repeat);
    })();
}
$(document).ready(function() {
    $('#fullpage').fullpage({
        //Navigation
        anchors: ['1', '2', '3', '4','5', '6', '7', '8', '9', 'lastpage'],
        navigation: true,
        navigationPosition: 'right',
        slidesNavigation: true,

        //Scrolling
        loopTop: true,
        loopBottom: true,
        scrollingSpeed: 500,
        // scrollBar: true,
        easing: 'easeInQuart',
        touchSensitivity: 15,
    });
});

// Muse Connection Indicator
var museConnection = function () {
    console.log('Connected to Platform!');
};

// Results Page Charts
// TODO: Lincoln - get real data to fill data arr
var randomScalingFactor = function() {
        return Math.round(Math.random()*100)
};

var barChartData = {
    labels : ["Average HRV","Average Alpha EEG"],
    datasets : [
        {
            fillColor : "rgba(220,220,220,0.5)",
            strokeColor : "rgba(220,220,220,0.8)",
            highlightFill: "rgba(220,220,220,0.75)",
            highlightStroke: "rgba(220,220,220,1)",
            data : [randomScalingFactor(),randomScalingFactor()]
        },
        {
            fillColor : "rgb(234, 200, 94)",
            strokeColor : "rgb(234, 200, 98)",
            highlightFill : "#eac85e",
            highlightStroke : "#eac85e",
            // highlightStroke : "rgba(151,187,205,1)",
            data : [randomScalingFactor(),randomScalingFactor()]
        }
    ]

}

window.onload = function(){
    var ctx = document.getElementById("canvas").getContext("2d");
    window.myBar = new Chart(ctx).Bar(barChartData, {
        responsive : true,
        // scaleShowGridLines : false,
        scaleFontSize: 20,
        scaleFontColor: "#FFF",
        scaleFontFamily: "'Open Sans',sans-serif;",
        scaleLineColor: "#FFF",
    });
}



// Radar Chart
RadarChart.defaultConfig.color = function() {};
RadarChart.defaultConfig.radius = 3;

// TODO: Lincoln - radar data
var data = [
  {
    className: 'before', // optional can be used for styling
    axes: [
      {axis: "calm", value: 13},
      {axis: "contentedness", value: 6},
      {axis: "distraction", value: 5},
      {axis: "well-being", value: 9},
    ]
  },
  {
    className: 'after',
    axes: [
      {axis: "calm", value: 6},
      {axis: "contentedness", value: 7},
      {axis: "distraction", value: 10},
      {axis: "well-being", value: 13},
    ]
  }
];

function randomDataset() {
  return data.map(function(d) {
    return {
      className: d.className,
      axes: d.axes.map(function(axis) {
        return {axis: axis.axis, value: Math.ceil(Math.random() * 10)};
      })
    };
  });
}

var chart = RadarChart.chart();
var cfg = chart.config(); // retrieve default config
var svg = d3.select('body').append('svg')
.attr('width', cfg.w)
.attr('height', cfg.h + cfg.h / 4);
svg.append('g').classed('single', 1).datum(randomDataset()).call(chart);

function render() {
    var game = svg.selectAll('g.game').data(
      [
        randomDataset(),
        randomDataset(),
        randomDataset(),
        randomDataset()
      ]
    );
    game.enter().append('g').classed('game', 1);
    game
      .attr('transform', function(d, i) { return 'translate('+(i * cfg.w)+','+ (cfg.h * 4) +')'; })
      .call(chart);

    setTimeout(render, 1000);
}
render();

RadarChart.defaultConfig.levelTick = true;
RadarChart.draw(".chart-container", data);
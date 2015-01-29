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
// var randomScalingFactor = function() {
//         return Math.round(Math.random()*100)
// };

// var barChartData = {
//     labels : ["Average HRV","Average Alpha EEG"],
//     datasets : [
//         {
//             fillColor : "rgba(220,220,220,0.5)",
//             strokeColor : "rgba(220,220,220,0.8)",
//             highlightFill: "rgba(220,220,220,0.75)",
//             highlightStroke: "rgba(220,220,220,1)",
//             data : [randomScalingFactor(),randomScalingFactor()]
//         },
//         {
//             fillColor : "rgb(234, 200, 94)",
//             strokeColor : "rgb(234, 200, 98)",
//             highlightFill : "#eac85e",
//             highlightStroke : "#eac85e",
//             // highlightStroke : "rgba(151,187,205,1)",
//             data : [randomScalingFactor(),randomScalingFactor()]
//         }
//     ]

// }

function setBarChartData(data){
  var barChartData = {
    // labels : ["Average HRV","Average Alpha EEG"],
    labels : ["Average HRV"],
    datasets : [
        {
            fillColor : "rgba(220,220,220,0.5)",
            strokeColor : "rgba(220,220,220,0.8)",
            highlightFill: "rgba(220,220,220,0.75)",
            highlightStroke: "rgba(220,220,220,1)",
            // data : [data[0],data[1]]
            data : [data[0]]
        },
        {
            fillColor : "rgb(234, 200, 94)",
            strokeColor : "rgb(234, 200, 98)",
            highlightFill : "#eac85e",
            highlightStroke : "#eac85e",
            // highlightStroke : "rgba(151,187,205,1)",
            data : [data[1]]
        }
    ]
  }
    return barChartData;
}

// Second barchart
function setSecondChartData(data) {
  var barChartData = {
    labels : ["Average Alpha EEG"],
    datasets : [
        {
            fillColor : "rgba(220,220,220,0.5)",
            strokeColor : "rgba(220,220,220,0.8)",
            highlightFill: "rgba(220,220,220,0.75)",
            highlightStroke: "rgba(220,220,220,1)",
            // data : [data[0],data[1]]
            data : [data[2]]
        },
        {
            fillColor : "rgb(234, 200, 94)",
            strokeColor : "rgb(234, 200, 98)",
            highlightFill : "#eac85e",
            highlightStroke : "#eac85e",
            // highlightStroke : "rgba(151,187,205,1)",
            data : [data[3]]
        },
    ]
  }
    return barChartData;
}

function drawBarChart (data){

    var barChartData = setBarChartData(data);
    var ctx = document.getElementById("canvas1").getContext("2d");
    window.myBar = new Chart(ctx).Bar(barChartData, {
        // responsive : true,
        // scaleShowGridLines : false,
        scaleFontSize: 30,
        scaleFontColor: "#FFF",
        scaleFontFamily: "'Open Sans',sans-serif;",
        scaleLineColor: "#FFF",
        showTooltips: false,
    });

    // second chart
    var secondChartData = setSecondChartData(data);
    var newctx = document.getElementById("canvas2").getContext("2d");
    var options = {
        // responsive : true,
        scaleFontSize: 30,
        scaleFontColor: "#FFF",
        scaleFontFamily: "'Open Sans',sans-serif;",
        scaleLineColor: "#FFF",
        showTooltips: false,
    }
    var testBar = new Chart(newctx).Bar(secondChartData, options);

}

//  console.log("myBar:" + window.myBar)
//  window.myBar.
//}

function setRadarChartData(before_data,after_data)
{
  var data = {
    labels: ["Calm", "Contentedness", "Distraction", "Well-being"],
    datasets: [
        {
            label: "Before",
            fillColor: "rgba(220,220,220,0.2)",
            strokeColor: "rgba(220,220,220,1)",
            pointColor: "rgba(220,220,220,1)",
            pointStrokeColor: "#fff",
            pointHighlightFill: "#fff",
            pointHighlightStroke: "rgba(220,220,220,1)",
            data: before_data
        },
        {
            label: "After",
            fillColor: "rgba(151,187,205,0.2)",
            strokeColor: "rgba(151,187,205,1)",
            pointColor: "rgba(151,187,205,1)",
            pointStrokeColor: "#fff",
            pointHighlightFill: "#fff",
            pointHighlightStroke: "rgba(151,187,205,1)",
            data: after_data
        }
    ]
};
  return data;
}

function drawRadarChart(before_data,after_data){

  var radarData = setRadarChartData(before_data,after_data);
  var ctx = document.getElementById("canvas_radar").getContext("2d");
  ctx.font="100px Arial";

  var legendTemplate  = "<ul class=\"<%=name.toLowerCase()%>-legend\"><% for (var i=0; i<datasets.length; i++){%><li><span style=\"background-color:<%=datasets[i].lineColor%>\"></span><%if(datasets[i].label){%><%=datasets[i].label%><%}%></li><%}%></ul>"

  var myRadarChart = new Chart(ctx).Radar(radarData, {
        // responsive : true,
        // scaleShowGridLines : false,
        scaleFontSize: 32,
        pointLabelFontSize: 32,
        pointLabelFontColor: "#FFF",
        pointLabelFontFamily: "'Open Sans',sans-serif;",
        angleLineColor: "#FFF",
        legendTemplate : legendTemplate,
        showTooltips: false,
    }
  );

}

// Radar Chart
RadarChart.defaultConfig.color = function() {};
RadarChart.defaultConfig.radius = 3;

// TODO: Lincoln - radar data
/*var data =
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
];*/

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

/*var chart = RadarChart.chart();
var cfg = chart.config(); // retrieve default config
var svg = d3.select('body').append('svg')
.attr('width', cfg.w)
.attr('height', cfg.h + cfg.h / 4);
svg.append('g').classed('single', 1).datum(randomDataset()).call(chart);*/

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
/*render();

RadarChart.defaultConfig.levelTick = true;
RadarChart.draw(".chart-container", data);*/

function drawRadar(data){

  RadarChart.defaultConfig.color = function() {};
  RadarChart.defaultConfig.radius = 3;
  var chart = RadarChart.chart();

  var radarData = [
  {
    className: 'before', // optional can be used for styling
    axes: [
      {axis: "calm", value: data[0]},
      {axis: "contentedness", value: data[1]},
      {axis: "distraction", value: data[2]},
      {axis: "well-being", value: data[3]},
    ]
  },
  {
    className: 'after',
    axes: [
      {axis: "calm", value: data[4]},
      {axis: "contentedness", value: data[5]},
      {axis: "distraction", value: data[6]},
      {axis: "well-being", value: data[7]},
    ]
  }
];

RadarChart.draw(".chart-container", data);

}


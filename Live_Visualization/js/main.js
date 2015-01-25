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
            fillColor : "rgba(151,187,205,0.5)",
            strokeColor : "rgba(151,187,205,0.8)",
            highlightFill : "rgba(151,187,205,0.75)",
            highlightStroke : "rgba(151,187,205,1)",
            data : [randomScalingFactor(),randomScalingFactor()]
        }
    ]

}

window.onload = function(){
    var ctx = document.getElementById("canvas").getContext("2d");
    window.myBar = new Chart(ctx).Bar(barChartData, {
        responsive : true,
        scaleShowGridLines : false,
        scaleFontSize: 24,
        scaleFontColor: "#FFF",
        scaleFontFamily: "'Open Sans',sans-serif;",
        scaleLineColor: "#FFF",
    });
}
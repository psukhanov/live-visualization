// countdown timer
var countdown = $("#countdown").countdown360({
    radius: 115,
    seconds: 60,
    label: ['sec', 'secs'],
    fontColor: '#FFFFFF',
    strokeStyle: '#f5f5f5',
    fillStyle: '#e5603b',
    autostart: false,
    onComplete: function () {
      console.log('done');
    }
});

//countdown.start();

$('#countdown').click(function() {
  countdown.extendTimer(15);
});
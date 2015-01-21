var countdown = $("#countdown").countdown360({
    radius: 115,
    seconds: 60,
    label: ['sec', 'secs'],
    fontColor: '#FFFFFF',
    strokeStyle: '#398FBD',
    fillStyle: '#6a8da7',
    autostart: false,
    onComplete: function () {
      console.log('done');
    }
});

countdown.start();

$('#countdown').click(function() {
  countdown.extendTimer(15);
});
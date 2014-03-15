var resizeSketches = function() {
  var canvas = $('canvas');
  jswidth = $(window).width();
  jsheight = $(window).height();
  jswidth = 2*jswidth/3;
  jsheight = 2*jsheight/3;
  canvas.attr('width', jswidth);
  canvas.attr('height', jsheight);
  var sketch = Processing.getInstanceById('springydemo');
  if (sketch === void 0) {
    return new Processing($("#springydemo")[0]);
  } else {
    return sketch.restart();
  }
};

$(window).on('resize', resizeSketches);
$(resizeSketches)
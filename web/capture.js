var system = require('system');
var args = system.args;
var page = require('webpage').create();
page.viewportSize = { width: 1200, height: 628 };
var gss = args[1];
var url = args[2];

page.open(url, function() {
  page.render("/tmp/"+gss+".png");
  phantom.exit();
});

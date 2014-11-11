'use strict';

var gulp = require('gulp');
var paths = require('./_paths');
var browserSync = require('browser-sync');
var argv = require('yargs').argv;


// Proxy existing server via brower-sync and serve on localhost:3000
gulp.task('serve', function() {
  var host = argv.host || argv.h || 'localhost';
  var port = argv.port || argv.p || 5000;

  browserSync({
    proxy: host + ':' + port,
    open: false,
    port: 3000
  });

  gulp.watch(paths.templates, browserSync.reload);
  gulp.watch(paths.images, ['images']);
  gulp.watch(paths.ie_styles, ['ie-css']);
  gulp.watch(paths.styles, ['sass']);
  gulp.watch(paths.scripts, ['scripts']);
});

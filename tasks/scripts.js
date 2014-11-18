'use strict';

var gulp = require('gulp');
var paths = require('./_paths');
var filter = require('gulp-filter');
var concat = require('gulp-concat');

gulp.task('scripts', ['clean-js'], function() {
  var scripts = paths.vendor_scripts.concat(paths.scripts);
  var withoutDebug = filter(['**/*.js', '!**/*debug*']);

  var stream = gulp.src(scripts)
    .pipe(withoutDebug)
    .pipe(concat('cla.js'))
    .pipe(gulp.dest(paths.dest + 'javascripts'));

  withoutDebug.restore({ end: true })
    .pipe(concat('cla-debug.js'))
    .pipe(gulp.dest(paths.dest + 'javascripts'));

  return stream;
});

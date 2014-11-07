'use strict';

var gulp = require('gulp');
var paths = require('./_paths');
var concat = require('gulp-concat');

gulp.task('scripts', ['clean-js', 'lint'], function() {
  var scripts = paths.vendor_scripts.concat(paths.scripts);

  return gulp
    .src(scripts)
    .pipe(concat('cla.js'))
    .pipe(gulp.dest(paths.dest + 'javascripts'));
});

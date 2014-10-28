'use strict';

var gulp = require('gulp');
var paths = require('./_paths');
var clean = require('gulp-clean');

gulp.task('clean', function() {
  return gulp
    .src(paths.dest, {read: false})
    .pipe(clean());
});

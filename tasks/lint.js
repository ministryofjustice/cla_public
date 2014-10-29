'use strict';

var gulp = require('gulp');
var paths = require('./_paths');
var jshint = require('gulp-jshint');
var stylish = require('jshint-stylish');

gulp.task('lint', function() {
  gulp
    .src(paths.scripts)
    .pipe(jshint())
    .pipe(jshint.reporter(stylish));
});

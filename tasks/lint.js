'use strict';

var gulp = require('gulp');
var paths = require('./_paths');
var jshint = require('gulp-jshint');
var stylish = require('jshint-stylish');
var scripts = paths.scripts + paths.no_lint_scripts;

gulp.task('lint', function() {
  gulp
    .src(scripts)
    .pipe(jshint())
    .pipe(jshint.reporter(stylish));
});

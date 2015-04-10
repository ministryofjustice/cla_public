'use strict';

var gulp = require('gulp');
var paths = require('./_paths');
var jshint = require('gulp-jshint');
var stylish = require('jshint-stylish');
var filter = require('gulp-filter');

gulp.task('lint', function() {
  var withoutTemplates = filter(['**/*.js', '!**/*templates.js']);

  gulp
    .src(paths.scripts)
    .pipe(withoutTemplates)
    .pipe(jshint())
    .pipe(jshint.reporter(stylish));
});

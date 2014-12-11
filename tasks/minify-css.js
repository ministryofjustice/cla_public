'use strict';

var gulp = require('gulp');
var paths = require('./_paths');
var minifyCss = require('gulp-minify-css');
var rename = require('gulp-rename');

gulp.task('minify-css', ['sass'], function() {
  return gulp
    .src(paths.dest + 'stylesheets/**/*.css')
    .pipe(minifyCss({ noAdvanced: true }))
    .pipe(rename({ suffix: '.min' }))
    .pipe(gulp.dest(paths.dest + 'stylesheets/'));
});

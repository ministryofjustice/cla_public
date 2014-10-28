'use strict';

var gulp = require('gulp');
var paths = require('./_paths');
var minifyCss = require('gulp-minify-css');
var rename = require('gulp-rename');

gulp.task('css-min', ['sass'], function() {
  return gulp
    .src(paths.dest_dir + 'stylesheets/*.css')
    .pipe(minifyCss())
    .pipe(rename({ suffix: '.min' }))
    .pipe(gulp.dest(paths.dest + 'stylesheets/'));
});

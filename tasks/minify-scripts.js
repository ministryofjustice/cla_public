'use strict';

var gulp = require('gulp');
var paths = require('./_paths');
var uglify = require('gulp-uglify');
var rename = require('gulp-rename');

gulp.task('minify-scripts', ['scripts', 'lint'], function() {
  return gulp
    .src(paths.dest + 'javascripts/*.js')
    .pipe(uglify({ mangle: false, compress: false })) // don't compress to prevent reorder
    .pipe(rename({ suffix: '.min' }))
    .pipe(gulp.dest(paths.dest + 'javascripts'));
});

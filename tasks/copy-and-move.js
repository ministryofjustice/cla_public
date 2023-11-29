'use strict';
const gulp = require('gulp');
const webpack = require('webpack-stream');
const paths = require('./_paths');

gulp.task('copy-and-move', function() {
  var copy_path = paths.jquery_scripts;
  return gulp.src(copy_path)
    .pipe(gulp.dest(paths.dest + 'javascripts/jquery'));
});

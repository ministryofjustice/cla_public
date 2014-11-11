'use strict';

var gulp = require('gulp');
var paths = require('./_paths');
var concat = require('gulp-concat');

gulp.task('scripts', ['clean-js'], function() {
  var prod = [paths.scripts];
  prod.push('!' + paths.scripts + '*debug*');

  gulp.src(prod)
    .pipe(concat('cla.js'))
    .pipe(gulp.dest(paths.dest + 'javascripts'));

  return gulp.src(paths.scripts + '*debug*')
    .pipe(concat('cla-debug.js'))
    .pipe(gulp.dest(paths.dest + 'javascripts'));
});

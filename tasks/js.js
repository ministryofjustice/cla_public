'use strict';

var gulp = require('gulp');
var paths = require('./_paths');
var concat = require('gulp-concat');

gulp.task('js', ['clean', 'lint'], function() {
  var prod = paths.scripts.slice(0);

  // ignore debug files
  prod.push('!' + paths.src + '**/*debug*');
  // create concatinated js file
  gulp
    .src(prod)
    .pipe(concat('cla.main.js'))
    .pipe(gulp.dest(paths.dest + 'javascripts'));
  // copy static vendor files
  gulp
    .src(paths.vendor_scripts)
    .pipe(gulp.dest(paths.dest + 'javascripts/vendor'));
  // create debug js file
  gulp
    .src(paths.src + 'javascripts/**/*debug*')
    .pipe(concat('cla.debug.js'))
    .pipe(gulp.dest(paths.dest + 'javascripts/'));
});

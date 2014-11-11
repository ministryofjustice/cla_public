'use strict';

var paths = require('./_paths');
var gulp = require('gulp');
var filter = require('gulp-filter');
var sass = require('gulp-ruby-sass');
var browserSync = require('browser-sync');
var reload = browserSync.reload;

gulp.task('ie-css', ['clean-iecss'], function() {
  return gulp
    .src(paths.ie_styles)
    .pipe(sass({
      lineNumbers: true,
      style: 'compact'
    }))
    .on('error', function (err) { console.log(err.message); })
    .pipe(gulp.dest(paths.dest + 'ie-stylesheets/'))
    .pipe(filter('**/*.css'))  // don't react to .map files when reloading browser
    .pipe(reload({ stream:true }));
});

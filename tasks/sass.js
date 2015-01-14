'use strict';

var paths = require('./_paths');
var gulp = require('gulp');
var filter = require('gulp-filter');
var sass = require('gulp-ruby-sass');
var browserSync = require('browser-sync');
var reload = browserSync.reload;

gulp.task('sass', ['clean-css'], function() {
  return gulp
    .src(paths.src + 'stylesheets/**/*.scss')
    .pipe(sass({
      lineNumbers: true,
      style: 'compact',
      loadPath: 'node_modules/govuk_frontend_toolkit/' // add node module toolkit path
    }))
    .on('error', function (err) { console.log(err.message); })
    .pipe(gulp.dest(paths.dest + 'stylesheets/'))
    .pipe(filter('**/*.css'))  // don't react to .map files when reloading browser
    .pipe(reload({ stream:true }));
});

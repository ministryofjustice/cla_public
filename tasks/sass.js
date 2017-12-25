'use strict';

var paths = require('./_paths');
var gulp = require('gulp');
var filter = require('gulp-filter');
var sass = require('gulp-ruby-sass');
var browserSync = require('browser-sync');
var reload = browserSync.reload;

gulp.task('sass', ['clean-css'], function() {
  return sass(paths.src + 'stylesheets/**/*.scss', { 
      sourcemap: true,
      lineNumbers: true,
      style: 'compact',
      loadPath: 'node_modules/govuk_frontend_toolkit/' // add node module toolkit path
    })
    .on('error', sass.logError )
    .pipe(gulp.dest(paths.dest + 'stylesheets/'))
    .pipe(filter('**/*.css'))  // don't react to .map files when reloading browser
    .pipe(reload({ stream:true }));
});

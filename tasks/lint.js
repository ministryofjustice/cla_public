'use strict';

var gulp = require('gulp');
var paths = require('./_paths');
var jshint = require('gulp-jshint');
var stylish = require('jshint-stylish');

gulp.task('lint', function() {
  var files = paths.scripts.slice(0);

  // files to ignore from linting
  files.push('!cla_public/assets-src/vendor/**');
  files.push('!cla_public/assets-src/javascripts/vendor/**');
  files.push('!cla_public/assets-src/javascripts/templates.js');

  gulp
    .src(files)
    .pipe(jshint())
    .pipe(jshint.reporter(stylish));
});

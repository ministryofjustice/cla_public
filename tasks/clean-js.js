'use strict';

var gulp = require('gulp');
var paths = require('./_paths');
var del = require('del');

gulp.task('clean-js', function(cb) {
  // Ensure the files are deleted before calling next task
  del(paths.dest + 'javascripts', cb);
});

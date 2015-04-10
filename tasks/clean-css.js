'use strict';

var gulp = require('gulp');
var paths = require('./_paths');
var del = require('del');

gulp.task('clean-css', function() {
  del(paths.dest + 'stylesheets');
});

'use strict';

var gulp = require('gulp');
var paths = require('./_paths');
var del = require('del');

gulp.task('clean-iecss', function() {
  del(paths.dest + 'ie-stylesheets');
});

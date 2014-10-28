/* jshint unused: false */

'use strict';

var gulp = require('gulp');
var requireDir = require('require-dir');
var dir = requireDir('./tasks');
var runSequence = require('run-sequence').use(gulp);

gulp.task('build', [
    'clean',
    'css-min',
    'js',
    'images'
  ]
);

gulp.task('default', ['build']);

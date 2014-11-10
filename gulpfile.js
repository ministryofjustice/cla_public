/* jshint unused: false */

'use strict';

var gulp = require('gulp');
var requireDir = require('require-dir');
var dir = requireDir('./tasks');

gulp.task('build', [
    'ie-css',
    'minify-css',
    'minify-scripts',
    'images'
  ]
);

gulp.task('default', ['build']);

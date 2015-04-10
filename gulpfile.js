/* jshint unused: false */

'use strict';

var gulp = require('gulp');
var requireDir = require('require-dir');

requireDir('./tasks');

gulp.task('build', [
    'minify-css',
    'minify-scripts',
    'images'
  ]
);

gulp.task('default', ['build']);

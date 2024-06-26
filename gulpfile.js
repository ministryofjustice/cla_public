/* jshint unused: false */

'use strict';

var gulp = require('gulp');
var requireDir = require('require-dir');

requireDir('./tasks');

gulp.task('build', [
    'copy-jquery',
    'minify-css',
    'webpack',
    'webpack-head',
    'images'
  ]
);

gulp.task('default', ['build']);

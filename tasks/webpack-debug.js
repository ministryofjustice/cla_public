'use strict';
const gulp = require('gulp');
const webpack = require('webpack-stream');
const webpackMerge = require("webpack-merge");
const common = require('./_webpack.common.config')
const paths = require('./_paths');

gulp.task('webpack-debug', function() {
  var config = webpackMerge(common, {
    output: {filename: 'cla-debug.min.js'},
  });
  var scripts = paths.vendor_scripts.concat(paths.scripts);
  return gulp.src(scripts)
  .pipe(webpack(config))
  .pipe(gulp.dest(paths.dest + 'javascripts'));
});

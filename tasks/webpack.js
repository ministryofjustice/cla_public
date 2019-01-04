'use strict';
const gulp = require('gulp');
const webpack = require('webpack-stream');
const common = require('./_webpack.common.config')
const paths = require('./_paths');
const filter = require('gulp-filter');

gulp.task('webpack', ['clean-js', 'webpack-debug', 'lint'], function() {
  var scripts = paths.vendor_scripts.concat(paths.scripts);
  var withoutDebug = filter(['**/*.js', '!**/*debug*'], { restore: true });
  return gulp.src(scripts)
    .pipe(withoutDebug)
    .pipe(webpack(common))
    .pipe(gulp.dest(paths.dest + 'javascripts'));
});

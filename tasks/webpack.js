'use strict';
const gulp = require('gulp');
const webpack = require('webpack-stream');
var paths = require('./_paths');
gulp.task('webpack', function() {
  return gulp.src(paths.webpack_entry)
    .pipe(webpack({
      mode: 'production'
    }))
});

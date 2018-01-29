'use strict';

var gulp = require('gulp');
var paths = require('./_paths');
var filter = require('gulp-filter');
var webpack = require('webpack-stream');

gulp.task('scripts', ['clean-js'], function() {
  var withoutDebug = filter(['**/*.js', '!**/*debug*'], { restore: true });
  var withDebug = gulp.src(paths.scripts);

  var stream = gulp.src(paths.scripts)
    .pipe(withoutDebug)
    .pipe(webpack({
      config : {
        output: {
          filename: 'cla.js'
        }
      }
    }))
    .pipe(gulp.dest(paths.dest + 'javascripts'));

  withDebug
    .pipe(webpack({
      config : {
        output: {
          filename: 'cla-debug.js'
        }
      }
    }))
    .pipe(gulp.dest(paths.dest + 'javascripts'));

  return stream;
});

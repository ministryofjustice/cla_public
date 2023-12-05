'use strict';
const gulp = require('gulp');
const sourceFile = 'node_modules/jquery/dist/*'
const paths = require('./_paths');

gulp.task('copy-jquery', function () {
  return gulp.src(sourceFile)
    .pipe(gulp.dest(paths.dest + 'javascripts/jquery/'));
});

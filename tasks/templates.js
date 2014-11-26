/* jshint unused: false */

var gulp = require('gulp');
var paths = require('./_paths');
var plugins = require('gulp-load-plugins')();

// js templates
gulp.task('templates', function(){
  gulp.src('cla_public/static-src/javascripts/templates/*.hbs')
    .pipe(plugins.handlebars())
    .pipe(plugins.defineModule('plain'))
    .pipe(plugins.declare({
      namespace: 'CLA.templates'
    }))
    .pipe(plugins.concat('templates.js'))
    .pipe(gulp.dest('cla_public/static-src/javascripts'));
});


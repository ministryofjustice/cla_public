/* jshint unused: false */

'use strict';

var gulp = require('gulp');
var paths = require('./_paths');
var handlebars = require('gulp-handlebars');
var defineModule = require('gulp-define-module');
var declare = require('gulp-declare');
var concat = require('gulp-concat');

// js templates
gulp.task('client-templates', function(){
  gulp.src('cla_public/static-src/javascripts/templates/*.hbs')
    .pipe(handlebars())
    .pipe(defineModule('plain'))
    .pipe(declare({
      namespace: 'CLA.templates'
    }))
    .pipe(concat('templates.js'))
    .pipe(gulp.dest('cla_public/static-src/javascripts'));
});


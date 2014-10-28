'use strict';

var paths = {
  src: 'cla_public/assets-src/',
  dest: 'cla_public/assets/',
  styles: 'cla_public/assets-src/stylesheets/**/*.scss',
  templates: 'cla_public/assets-src/javascripts/templates/*.hbs',
  scripts: [
    // vendor scripts
    'cla_public/assets-src/vendor/lodash/dist/lodash.min.js',
    'cla_public/assets-src/vendor/jquery-details/jquery.details.js',
    'cla_public/assets-src/vendor/handlebars/handlebars.js',
    // templates
    'cla_public/assets-src/javascripts/templates.js',
    // CLA
    'cla_public/assets-src/javascripts/moj.Helpers.js',
    'cla_public/assets-src/javascripts/modules/*'
  ],
  vendor_scripts: 'cla_public/assets-src/javascripts/vendor/*',
  images: 'cla_public/assets-src/images/**/*'
};

module.exports = paths;

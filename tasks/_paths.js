'use strict';

var mainBowerFiles = require('main-bower-files');
var vendorFiles = mainBowerFiles();

var paths = {
  src: 'cla_public/static-src/',
  dest: 'cla_public/static/',
  styles: 'cla_public/static-src/stylesheets/**/*.scss',
  ie_styles: 'cla_public/static-src/ie/**/*.scss',
  scripts: [
    'cla_public/static-src/javascripts/**/*'
  ],
  vendor_scripts: vendorFiles,
  images: 'cla_public/static-src/images/**/*',
  templates: 'cla_public/templates/**/*',
};

module.exports = paths;

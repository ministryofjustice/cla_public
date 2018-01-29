'use strict';

var paths = {
  src: 'cla_public/static-src/',
  dest: 'cla_public/static/',
  styles: 'cla_public/static-src/stylesheets/**/*.scss',
  ie_styles: 'cla_public/static-src/ie/**/*.scss',
  scripts: [
    'cla_public/static-src/javascripts/**/*.js',
    '!cla_public/static-src/javascripts/templates.js',
    '!cla_public/static-src/javascripts/webpack.config.js'
  ],
  images: 'cla_public/static-src/images/**/*',
  templates: 'cla_public/templates/**/*',
};

module.exports = paths;

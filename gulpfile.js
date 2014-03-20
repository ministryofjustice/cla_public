var gulp = require('gulp'),
    plugins = require("gulp-load-plugins")(),
    stylish = require('jshint-stylish');

var paths = {
  dest_dir: 'cla_frontend/assets/',
  styles: 'cla_frontend/assets-src/stylesheets/**/*.scss',
  scripts: [
    'cla_frontend/assets-src/javascripts/modules/moj.LabelFocus.js',
    'cla_frontend/assets-src/javascripts/modules/moj.LabelSelect.js',
    'cla_frontend/assets-src/javascripts/modules/moj.Conditional.js',
    'cla_frontend/assets-src/javascripts/modules/moj.Shame.js'
  ],
  vendor_scripts: [
    'cla_frontend/assets-src/vendor/lodash/dist/lodash.min.js',
    'cla_frontend/assets-src/vendor/jquery-details/jquery.details.min.js'
  ],
  images: 'cla_frontend/assets-src/images/**/*'
};

// compile scss
gulp.task('sass', function() {
  return gulp.src(paths.styles)
              .pipe(plugins.rubySass())
              .pipe(gulp.dest(paths.dest_dir + 'stylesheets'));
});

// concat js
gulp.task('js', function() {
  return gulp.src(paths.scripts)
              .pipe(plugins.concat('cla.main.js'))
              .pipe(gulp.dest(paths.dest_dir + 'javascripts'));
});
gulp.task('js:vendor', function() {
  return gulp.src(paths.vendor_scripts)
              .pipe(plugins.concat('vendor.js'))
              .pipe(gulp.dest(paths.dest_dir + 'javascripts'));
});

// jshint js code
gulp.task('lint', function() {
  return gulp.src(paths.scripts)
              .pipe(plugins.jshint())
              .pipe(plugins.jshint.reporter(stylish));
});

// optimise images
gulp.task('images', function() {
  return gulp.src(paths.images)
              .pipe(plugins.imagemin({optimizationLevel: 5}))
              .pipe(gulp.dest(paths.dest_dir + 'images'));
});

// setup watches
gulp.task('watch', function() {
  gulp.watch(paths.styles, ['sass']);
  gulp.watch(paths.scripts, ['js', 'lint']);
  gulp.watch(paths.images, ['images']);
});

// setup default tasks
gulp.task('default', ['build']);
gulp.task('build', ['sass', 'js', 'js:vendor', 'lint', 'images']);
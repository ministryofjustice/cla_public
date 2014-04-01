var gulp = require('gulp'),
    plugins = require('gulp-load-plugins')(),
    stylish = require('jshint-stylish'),
    runSequence = require('run-sequence');

var paths = {
  dest_dir: 'cla_public/assets/',
  src_dir: 'cla_public/assets-src/',
  styles: 'cla_public/assets-src/stylesheets/**/*.scss',
  scripts: [
    'cla_public/assets-src/javascripts/moj.Helpers.js',
    'cla_public/assets-src/javascripts/modules/moj.LabelFocus.js',
    'cla_public/assets-src/javascripts/modules/moj.LabelSelect.js',
    'cla_public/assets-src/javascripts/modules/moj.Conditional.js',
    'cla_public/assets-src/javascripts/modules/moj.QuestionPrompt.js',
    'cla_public/assets-src/javascripts/modules/moj.Validation.js',
    'cla_public/assets-src/javascripts/modules/moj.Shame.js'
  ],
  vendor_scripts: 'cla_public/assets-src/javascripts/vendor/*',
  bower_scripts: [
    'cla_public/assets-src/vendor/lodash/dist/lodash.min.js',
    'cla_public/assets-src/vendor/jquery-details/jquery.details.min.js'
  ],
  images: 'cla_public/assets-src/images/**/*'
};

// clean out assets folder
gulp.task('clean', function() {
  return gulp
    .src(paths.dest_dir, {read: false})
    .pipe(plugins.clean());
});

// compile scss
gulp.task('sass', function() {
  gulp
    .src(paths.styles)
    .pipe(plugins.rubySass())
    .pipe(gulp.dest(paths.dest_dir + 'stylesheets'));
});

// concat and move modules
gulp.task('js:main', function() {
  gulp
    .src(paths.scripts)
    .pipe(plugins.concat('cla.main.js'))
    .pipe(gulp.dest(paths.dest_dir + 'javascripts'));
});
// move vendor scripts
gulp.task('js:vendor', function() {
  gulp
    .src(paths.vendor_scripts)
    .pipe(gulp.dest(paths.dest_dir + 'javascripts/vendor'));
});
// concat and move footer bower vendor scripts
gulp.task('js:bower', function() {
  gulp
    .src(paths.bower_scripts)
    .pipe(plugins.concat('vendor.js'))
    .pipe(gulp.dest(paths.dest_dir + 'javascripts'));
});

// jshint js code
gulp.task('lint', function() {
  gulp
    .src(paths.scripts)
    .pipe(plugins.jshint())
    .pipe(plugins.jshint.reporter(stylish));
});

// optimise images
gulp.task('images', function() {
  gulp
    .src(paths.images)
    .pipe(plugins.imagemin({optimizationLevel: 5}))
    .pipe(gulp.dest(paths.dest_dir + 'images'));
});

// setup watches
gulp.task('watch', function() {
  gulp.watch(paths.styles, ['sass']);
  gulp.watch(paths.scripts, ['lint', 'js:main']);
  gulp.watch(paths.vendor_scripts, ['lint', 'js:vendor']);
  gulp.watch(paths.bower_scripts, ['lint', 'js:bower']);
  gulp.watch(paths.images, ['images']);
});

// setup default tasks
gulp.task('default', ['build']);
// run build
gulp.task('build', function() {
  runSequence('clean', ['js:main', 'js:vendor', 'js:bower', 'images', 'sass']);
});
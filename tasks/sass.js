"use strict";

var paths = require("./_paths");
var gulp = require("gulp");
var filter = require("gulp-filter");
var sass = require("gulp-sass");
var browserSync = require("browser-sync");
var reload = browserSync.reload;

gulp.task("sass", ["clean-css"], function() {
  return gulp
    .src(paths.src + "stylesheets/**/*.scss")
    .pipe(
      sass({
        includePaths: ["node_modules/govuk_frontend_toolkit/", "node_modules/govuk-frontend", "node_modules/govuk_publishing_components/app/assets/stylesheets"],
        outputStyle: "compact"
      }).on("error", sass.logError)
    )
    .pipe(gulp.dest(paths.dest + "stylesheets/"))
    .pipe(filter("**/*.css"))
    .pipe(reload({ stream: true }));
});

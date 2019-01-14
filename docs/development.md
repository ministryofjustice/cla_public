# Frontend build, lint, and serve

Assets reside in `static-src` directory and compiled in `static` directory upon running build tasks.

CLA Public is using [Gulp](http://gulpjs.com/) for build tasks. The following Gulp tasks are used in development:

- `build` builds and minifies all assets and does all of the following
- `lint` runs JS Hint on JS code
- `sass` builds the SCSS and generates source maps
- `serve` watches the files for changes and reloads the browser using [BrowserSync](http://www.browsersync.io/)

If you have [Foreman](https://github.com/ddollar/foreman) installed you can run `./tools/start-server` which will start the CLA Flask server and run the `gulp serve` process, enabling you to concentrate on the code leaving building and reloading to `serve` task.

# Python lint and pre-commit hooks

To lint with Black and flake8, install pre-commit hooks:

```
. env/bin/activate
pip install -r requirements/dev.txt
pre-commit install
```

To run them manually:
```
pre-commit run --all-files
```

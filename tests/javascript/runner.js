var Mocha = require('mocha'),
    fs = require('fs'),
    path = require('path'),
    glob = require('glob'),
    exists = fs.existsSync || path.existsSync,
    resolve = path.resolve,
    join = path.join,
    basename = path.basename,
    phantom_wd_runner = require('phantom-wd-runner');

// First, you need to instantiate a Mocha instance.
var mocha = new Mocha;

// Then, you need to use the method "addFile" on the mocha
// object for each file.

function lookupFiles(path, recursive) {
    var files = [];

    if (!exists(path)) {
        if (exists(path + '.js')) {
            path += '.js'
        } else {
            files = glob.sync(path);
            if (!files.length) throw new Error("cannot resolve path (or pattern) '" + path + "'");
            return files;
        }
    }

    var stat = fs.statSync(path);
    if (stat.isFile()) return path;

    fs.readdirSync(path).forEach(function(file){
        file = join(path, file);
        var stat = fs.statSync(file);
        if (stat.isDirectory()) {
            if (recursive) files = files.concat(lookupFiles(file, recursive));
            return
        }
        if (!stat.isFile() || basename(file)[0] == '.') return;
        files.push(file);
    });

    return files;
}

lookupFiles('tests/javascript/mocha/', true).forEach(function(file){
    // Use the method "addFile" to add the file to mocha
    mocha.addFile(file);
});

// Now, you can run the tests.

phantom_wd_runner().on('listening', function(){
    phantom = this;
    mocha.run(function(failures){
        phantom.kill();
        process.on('exit', function () {
            process.exit(failures);
        });
    });

});

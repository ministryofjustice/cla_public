var Mocha = require('mocha'),
    fs = require('fs'),
    path = require('path'),
    phantom_wd_runner = require('phantom-wd-runner');

// First, you need to instantiate a Mocha instance.
var mocha = new Mocha;

// Then, you need to use the method "addFile" on the mocha
// object for each file.

// Here is an example:
fs.readdirSync('tests/javascript/mocha/').filter(function(file){
    // Only keep the .js files
    return file.substr(-3) === '.js';

}).forEach(function(file){
    // Use the method "addFile" to add the file to mocha
    mocha.addFile(
        path.join('tests/javascript/mocha/', file)
    );
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

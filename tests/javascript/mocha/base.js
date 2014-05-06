var chai, chaiAsPromised, wd, utils;

require('colors');

chai = require("chai");

chaiAsPromised = require("chai-as-promised");

chai.use(chaiAsPromised);

chai.should();
wd = require('wd');

var browser;

before(function(){
    browser = wd.promiseChainRemote();
    this.browser = browser;
    // optional extra logging
    browser.on('status', function(info) {
        console.log(info.cyan);
    });
    browser.on('command', function(eventType, command, response) {
        console.log(' > ' + eventType.cyan, command, (response || '').grey);
    });
    browser.on('http', function(meth, path, data) {
        console.log(' > ' + meth.magenta, path, (data || '').grey);
    });
    return browser
        .init();
});

after(function() {
    return browser.quit();
});
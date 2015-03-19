'use strict';

var execSync = require('child_process').execSync;
var gitRev = execSync('git rev-parse HEAD', {encoding: 'utf8'});

module.exports = (function(settings) {

  for(var x in settings.test_settings) {
    settings.test_settings[x].desiredCapabilities.build = gitRev;
    settings.test_settings[x].desiredCapabilities.project = "CLA Public";
    settings.test_settings[x].desiredCapabilities.javascriptEnabled = true;
    settings.test_settings[x].desiredCapabilities.acceptSslCerts = true;
    settings.test_settings[x].desiredCapabilities["browserstack.user"] = process.env.BS_USER;
    settings.test_settings[x].desiredCapabilities["browserstack.key"] = process.env.BS_PASS;
    settings.test_settings[x].desiredCapabilities["browserstack.debug"] = true;
  }
  return settings;

})(require('./browserstack-integration.json'));

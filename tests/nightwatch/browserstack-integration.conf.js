'use strict';

module.exports = (function(settings) {

  for(var x in settings.test_settings) {
    settings.test_settings[x].desiredCapabilities.build = "latest integration";
    settings.test_settings[x].desiredCapabilities.project = "CLA Public";
    settings.test_settings[x].desiredCapabilities.javascriptEnabled = true;
    settings.test_settings[x].desiredCapabilities.acceptSslCerts = true;
    settings.test_settings[x].desiredCapabilities["browserstack.user"] = process.env.BS_USER;
    settings.test_settings[x].desiredCapabilities["browserstack.key"] = process.env.BS_PASS;
    settings.test_settings[x].desiredCapabilities["browserstack.debug"] = true;
  }
  return settings;

})(require('./browserstack-integration.json'));

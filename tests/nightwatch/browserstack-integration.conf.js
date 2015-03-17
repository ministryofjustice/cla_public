module.exports = (function(settings) {

  for(var x in settings.test_settings) {
    settings.test_settings[x].desiredCapabilities.build = "latest integration";
    settings.test_settings[x].desiredCapabilities.project = "CLA Public";
    settings.test_settings[x].desiredCapabilities.javascriptEnabled = true;
    settings.test_settings[x].desiredCapabilities.acceptSslCerts = true;
    settings.test_settings[x].desiredCapabilities["browserstack.user"] = "janszumiec";
    settings.test_settings[x].desiredCapabilities["browserstack.key"] = "oX5YoppK12BMXdVAgWvz";
  }
  return settings;

})(require('./browserstack-integration.json'));

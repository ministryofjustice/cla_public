var chai = require("chai"),
    chaiAsPromised = require("chai-as-promised"),
    wd = require('wd');

chai.use(chaiAsPromised);
chai.should();
chaiAsPromised.transferPromiseness = wd.transferPromiseness;

var asserters = wd.asserters;

describe('basic test', function() {
    this.timeout(10000);
    var browser;
    before(function(){
        browser = this.browser;
        browser.deleteAllCookies();
    });

    describe('Disposable Income is eligible because not enough income', function() {
        it('should say you are ineligible', function(done){
            browser
                .get('http://localhost:8002')
                .elementByCssSelector('a[role=button]')
                .click()
                .waitForElementByCssSelector('h1', asserters.textInclude('Your Details'), 9000)
                .nodeify(done);
        });

    });
});

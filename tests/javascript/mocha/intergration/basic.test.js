var chai = require("chai"),
    chaiAsPromised = require("chai-as-promised"),
    wd = require('wd');

chai.use(chaiAsPromised);
chai.should();
chaiAsPromised.transferPromiseness = wd.transferPromiseness;

describe('basic test', function() {
    this.timeout(10000);
    var browser;
    before(function(){
        browser = this.browser;
    });

    describe('is site up', function() {
        it('should have correct title', function(done){
            browser.get('http://localhost:8002')
                .title()
                .then(function(title){
                    title.should.equal('Civil Legal Advice')
                })
                .nodeify(done);
        });

    });
});


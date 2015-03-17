SPECS_PATH = ./tests/nightwatch/specs/current

ifdef spec
	specific_test = -t ${SPECS_PATH}/${spec}.js
endif

ifdef bsb
	specific_browserstack_browser = -e ${bsb}
endif

# running tests on local env
test:
	./nightwatch -c tests/nightwatch/local.json -s legacy ${specific_test}
test-chrome:
	./nightwatch -c tests/nightwatch/local.json -s legacy --env chrome ${specific_test}
test-firefox:
	./nightwatch -c tests/nightwatch/local.json -s legacy --env firefox ${specific_test}
test-legacy:
	./nightwatch -c tests/nightwatch/local.json -s current ${specific_test}
test-all:
	./nightwatch -c tests/nightwatch/local.json

# running tests on Browserstack
test-bs:
	./nightwatch -c tests/nightwatch/browserstack-integration.conf.js -s legacy -e default,chromewin,ffmac,ffwin ${specific_test}
	./nightwatch -c tests/nightwatch/browserstack-integration.conf.js -s legacy -e ie11,ie10,ie9,ie8,ie7 ${specific_test}
test-bs-good:
	./nightwatch -c tests/nightwatch/browserstack-integration.conf.js -s legacy -e default,chromewin,ffmac,ffwin ${specific_test}
test-bs-ie:
	./nightwatch -c tests/nightwatch/browserstack-integration.conf.js -s legacy -e ie11,ie10,ie9,ie8,ie7 ${specific_test}

test-bs-specific:
	./nightwatch -c tests/nightwatch/browserstack-integration.conf.js -s legacy ${specific_browserstack_browser} ${specific_test}

SPECS_PATH = ./tests/nightwatch/specs

ifdef spec
	specific_test = -t ${SPECS_PATH}/${spec}.js
endif

ifdef browser
	environment = --env ${browser}
endif

# bsb = browserstack browser. specify for single or use ie for all IEs, good for others. omit for default (chrome on mac)
# our browserstack account currently only lets us run 5 parallel tests, so can't run all at once
ifdef bsb
	ifeq ($(bsb),ie)
		browserstack_browser = -e ie11,ie10,ie9,ie8,ie7
	else ifeq ($(bsb),good)
		browserstack_browser = -e default,chromewin,ffmac,ffwin
	else
		browserstack_browser = -e ${bsb}
	endif
endif

# running tests on local env
test:
	./nightwatch -c tests/nightwatch/local.json ${environment} ${specific_test}
test-chrome:
	./nightwatch -c tests/nightwatch/local.json --env chrome ${specific_test}
test-firefox:
	./nightwatch -c tests/nightwatch/local.json --env firefox ${specific_test}

# running tests on Browserstack - set credentials in env vars BS_USER and BS_PASS
test-bs:
	./nightwatch -c tests/nightwatch/browserstack-integration.conf.js ${browserstack_browser} ${specific_test}

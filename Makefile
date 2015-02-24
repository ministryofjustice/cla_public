SPECS_PATH = ./tests/nightwatch/specs/current

ifdef spec
	specific_test = -t ${SPECS_PATH}/${spec}.js
endif

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

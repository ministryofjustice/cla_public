test:
	./nightwatch -c tests/nightwatch/local.json -t ${test}
test-chrome:
	./nightwatch -c tests/nightwatch/local.json --env chrome -t ${test}
test-firefox:
	./nightwatch -c tests/nightwatch/local.json --env firefox -t ${test}

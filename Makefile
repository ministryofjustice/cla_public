test:
	./nightwatch -c tests/nightwatch/config.json -t ${test}
test-chrome:
	./nightwatch -c tests/nightwatch/config.json --env chrome -t ${test}
test-firefox:
	./nightwatch -c tests/nightwatch/config.json --env firefox -t ${test}

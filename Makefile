test:
	./nightwatch -c tests/javascript/nightwatch.json
test-browserstack:
	./nightwatch -c tests/javascript/nightwatch.json --env integration

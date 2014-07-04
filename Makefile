test:
	./nightwatch --config tests/javascript/nightwatch.json
test-ff:
	./nightwatch --config tests/javascript/nightwatch.json --env firefox
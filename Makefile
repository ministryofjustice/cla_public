test:
	./nightwatch -c tests/nightwatch/config.json
test-chrome:
	./nightwatch -c tests/nightwatch/config.json --env chrome
test-firefox:
	./nightwatch -c tests/nightwatch/config.json --env firefox

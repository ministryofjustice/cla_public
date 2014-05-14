test:
	./nightwatch -c tests/javascript/nightwatch.json

test-jenkins:
	./nightwatch -c tests/javascript/nightwatch.json --env jenkins

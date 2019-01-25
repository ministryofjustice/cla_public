# Monitoring

## Dashboards

1. Open the CPU/memory/network dashboard in [Grafana](https://grafana.apps.cloud-platform-live-0.k8s.integration.dsd.io/d/87a9fc9281061289879d05928d54a80c6b57818a/laa-cla-public?orgId=1&refresh=1m).
1. Select one of the environment namespaces to monitor.

## Accessing logs

### Through Kibana

1. Go to [Kibana in the Kubernetes cluster](https://kibana.apps.cloud-platform-live-0.k8s.integration.dsd.io/_plugin/kibana).
1. Type your query, scoping it to the `cla-public` logs: `kubernetes.namespace_name: "laa-cla-public-<environment>" AND log: "<search terms>"`
1. Select the time period in the upper right corner.

### Directly from Kubernetes

1. Get the list of pods: `kubectl --namespace=laa-cla-public-<environment> get pods`
1. Follow the logs for the pod: `kubectl --namespace=laa-cla-public-<environment> logs laa-cla-public-5c8f4d4f7f-9l2cp --follow`

# Releasing

## Releasing to non-production

1. Wait for [the Docker build to complete on CircleCI](https://circleci.com/gh/ministryofjustice/cla_public) for the feature branch.
1. Approve the pending staging deployment on CircleCI.
    [Watch the how-to video:](https://www.youtube.com/watch?v=9JovuQK-XnA)<br/>
    [![How to approve staging deployments](https://img.youtube.com/vi/9JovuQK-XnA/1.jpg)](https://www.youtube.com/watch?v=9JovuQK-XnA)
1. :rotating_light: Unfortunately, our deployment process does not _yet_ fail the build if the deployment fails.
    To see if the deploy was successful, follow Kubernetes deployments, pods and events for any feedback:
    ```
    kubectl --namespace laa-cla-public-staging get pods,deployments -o wide
    kubectl --namespace laa-cla-public-staging get events
    ```

## Releasing to production

1. Please make sure you tested on a non-production environment before merging.
1. Merge your feature branch pull request to `master`.
1. Wait for [the Docker build to complete on CircleCI](https://circleci.com/gh/ministryofjustice/cla_public/tree/master) for the `master` branch.
1. Approve the pending staging deployment on CircleCI (see 'Releasing to non-production above' video for more info).
1. Approve the pending production deployment on CircleCI.
1. :rotating_light: Unfortunately, our deployment process does not _yet_ fail the build if the deployment fails.
    To see if the deploy was successful, follow Kubernetes deployments, pods and events for any feedback:
    ```
    kubectl --namespace laa-cla-public-production get pods,deployments -o wide
    kubectl --namespace laa-cla-public-production get events
    ```

## Rolling back

1. Check the rollout history with `kubectl rollout history deployment/laa-cla-public --namespace=laa-cla-public-<environment>`
1. Roll back to the previous version with `kubectl rollout undo deployment/laa-cla-public --namespace=laa-cla-public-<environment>`

:memo: The `<environment>` above is either `staging` or `production`.

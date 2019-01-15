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

:warning: This project is currently deployed to _both_ template-deploy and Kubernetes.

:rotating_light: To ensure correctness for end users, please **always deploy to both environments**.

### Template Deploy
1. Please make sure you tested on a non-production environment before merging.
1. Merge your feature branch pull request to `master`.
1. Wait for [the Docker build to complete on CircleCI](https://circleci.com/gh/ministryofjustice/cla_public/tree/master) for the `master` branch.
1. Copy the `master.<sha>` reference from the `build` job's "Push Docker image" step. Eg:
    ```
    Pushing tag for rev [d64474359f5d] on {https://registry.service.dsd.io/v1/repositories/cla_public/tags/master.54c165b}
    ```
1. [Deploy `master.<sha>` to **prod**uction](https://ci.service.dsd.io/job/DEPLOY-cla_public/build?delay=0sec).
    * `ENVIRONMENT` is the target environment, select depending on your needs. Select `prod` for production.
    * `CONTAINER_BRANCH` is the branch that needs to be released (`master` in the above example).
    * `VERSION` is the specific 7-character prefix of the Git SHA (`54c165b` in the above example).

:tada: :shipit:

### Deploy to Kubernetes using CircleCI

**Note:** We currently have an offline production environment in Kubernetes. This will not be mapped to the public URL until further tasks have been completed.

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

# Using Kubernetes

Read the following if you want to use Kubernetes from your local development environment.

## Setup kubectl

You'll need to install and configure `kubectl` CLI tool to interact with Kubernetes. There are [instructions on kubectl configuration](https://ministryofjustice.github.io/cloud-platform-user-docs/01-getting-started/001-kubectl-config/) in the Cloud Platform User Guide.

## Kubernetes namespaces


`cla_public` has two namespaces (environments):

- [laa-cla-public-staging](https://github.com/ministryofjustice/cloud-platform-environments/tree/master/namespaces/cloud-platform-live-0.k8s.integration.dsd.io/laa-cla-public-staging)
- [laa-cla-public-production](https://github.com/ministryofjustice/cloud-platform-environments/tree/master/namespaces/cloud-platform-live-0.k8s.integration.dsd.io/laa-cla-public-production)

## Admin role

When you become a member of the GitHub team `laa-get-access`, you'll automatically get the `ClusterRole - admin` role.

>**What is the ClusterRole -admin**
>Allows admin access, intended to be granted within a namespace using a RoleBinding. If used in a RoleBinding, allows read/write access to most resources in a namespace, including the ability to create roles and rolebindings within the namespace. It does not allow write access to resource quota or to the namespace itself. https://kubernetes.io/docs/reference/access-authn-authz/rbac/#default-roles-and-role-bindings

You can [find out more about roles](https://ministryofjustice.github.io/cloud-platform-user-docs/01-getting-started/002-env-create/#01-rbacyaml) in the Cloud Platform User Guide.


## Authenticating with the Docker registry
Docker images are stored in AWS ECR. To authenticate with the `cla_public` repository, fetch the credentials by typing the following:

```
kubectl --namespace laa-cla-public-staging get secrets -o yaml
```

This command will return the **encoded** `AWS_ACCESS_KEY_ID` and `AWS_SECRET_ACCESS_KEY`. You can find out more by reading [Authenticating with the repository](https://ministryofjustice.github.io/cloud-platform-user-docs/02-deploying-an-app/001-app-deploy/#authenticating-with-the-repository).

## Deploying to Kubernetes

The standard way of deploying is via CircleCI deploy jobs. See [Deploy to Kubernetes using CircleCI](#deploy-to-kubernetes-using-circleci).

If you need to deploy manually because, for example, CircleCI is offline, follow these steps:

1. Build the Docker image locally. For example:
    ```
    docker build -t cla_public:latest .
    ```
1. Tag the build. For example:
    ```
    docker tag cla_public:latest 926803513772.dkr.ecr.eu-west-1.amazonaws.com/laa-get-access/laa-cla-public:awesometag
    ```
1. Push the docker image. For example:
    ```
    docker push 926803513772.dkr.ecr.eu-west-1.amazonaws.com/laa-get-access/laa-cla-public:awesometag
    ```
1. Deploy changes to Kubernetes by applying changes to the `deployment.yml`. This example takes the `deployment.yml` as input, changes the value of `image` for the container named `app` to `926803513772.dkr.ecr.eu-west-1.amazonaws.com/laa-get-access/laa-cla-public:awesometag`, then pipes the updated yaml to the next command. The `kubectl apply` applies the yaml from stdin:
    ```
    kubectl set image --filename="kubernetes_deploy/staging/deployment.yml" --local --output=yaml app="926803513772.dkr.ecr.eu-west-1.amazonaws.com/laa-get-access/laa-cla-public:awesometag" | kubectl apply --namespace=laa-cla-public-staging --filename=/dev/stdin
    ```
   A similiar technique is used in [deploy_to_kubernetes](https://github.com/ministryofjustice/cla_public/blob/master/.circleci/deploy_to_kubernetes) script. Of course, you could simply update the `deployment.yml` file directly and apply the changes.
   
   To use [deploy_to_kubernetes](https://github.com/ministryofjustice/cla_public/blob/master/.circleci/deploy_to_kubernetes), requires an environment variable called `ECR_DEPLOY_IMAGE` and a positional argument for the namespace to deploy to, i.e. `staging` or `production`. Here's an example:
   ```
   kubectl config set-context $(kubectl config current-context) --namespace=laa-cla-public-staging
   ECR_DEPLOY_IMAGE=926803513772.dkr.ecr.eu-west-1.amazonaws.com/laa-get-access/laa-cla-public:awesometag .circleci/deploy_to_kubernetes staging
   ```


## Secrets
See the [Kubernetes Secrets documentation](https://kubernetes.io/docs/concepts/configuration/secret/)

And keep the following in mind:

Remember to namespace e.g. to list secrets

```
kubectl --namespace laa-cla-public-staging get secrets
kubectl --namespace laa-cla-public-production get secrets
```

If adding a secret with a temp file, do *not* git commit the actual secret, whether base64 encoded or not!  

# Jenkins CI

Deployment of Jenkin to K8S

Playbooks:

* `deploy-jenkins.sh` - deploys Jenkins
* `ensure-job.sh` - ensure Jenkins jobs are present

## Prerequisites

* Ansible

  `pip3 install --user ansible`

* OpenShift module

  `pip3 install --user openshift kubernetes`

* Helm with Jenkins charts

  ```bash
  helm repo add jenkinsci https://charts.jenkins.io
  helm repo update
  ```

* K8S and Helm modules

  ```bash
  rm -rf ~/.ansible/collections/ansible_collections/community/kubernetes && \
  ansible-galaxy collection install community.kubernetes
  ```

* In case of GKE workload identity configured for Jenkins `ci` namespaces Kubernetes Service Accounts (KSAs)

  ```bash
  cd ../.../gcp/gke/addons/ng-gke-setup && \
    make apply CLUSTER_NAME=shared1 KNS=ci KSAS='["default","ci", "ci-jenkins"]' ROLES='["roles/storage.admin"]'
  ```

## Running

Samples:

```bash
# deploy to minikube
deploy-jenkins.sh -e minikube -p password-for-jenkins
or
deploy-jenkins.sh minikube -p password-for-jenkins

# deploy to gke
deploy-jenkins.sh -e gke -p password-for-jenkins


# ensure Jobs for env are present
ensure-jobs.sh -e minikube -p password-for-jenkins
```

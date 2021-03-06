#!/usr/bin/env bash

function ensurePlaybookRequirements() {
  [ -x /usr/local/bin/helm ] || (
    curl https://raw.githubusercontent.com/helm/helm/master/scripts/get-helm-3 | bash
    helm repo add stable https://charts.helm.sh/stable
  )
  pip3 show openshift &>/dev/null || {
    pip3 install openshift --user
    pip3 install --pre --upgrade kubernetes --user
    pip3 install kubernetes-validate --user
  }
}

function usage() {
  echo -e "Usage: $(basename "$0") -e|--env minikube/gke -p jenkins-admin-password [env]

Deploys Jenkins in 'env'.
Assumes kubectl is logged to 'env' cluster already.

Samples:
# deploy to minikube
$(basename "$0") -e minikube -p password-for-jenkins
or
$(basename "$0") minikube -p password-for-jenkins

# deploy to gke
$(basename "$0") -e gke -p password-for-jenkins
"
}

ensurePlaybookRequirements

while [[ "$#" -gt 0 ]]; do
  case $1 in
  -h | --help | help)
    usage
    exit 1
    ;;
  -e | --env)
    ENV="$2"
    shift
    ;;
  -p | --jenkins-password)
    PASS="$2"
    shift
    ;;
  *) PARAMS+=("$1") ;; # save it in an array for later
  esac
  shift
done
set -- "${PARAMS[@]}" # restore positional parameters

ENV=${ENV:-${PARAMS[0]}}

if [[ -z "$ENV" || -z "$PASS" ]]; then
  usage
  exit 1
fi

ansible-playbook deploy-jenkins.yaml -v -e env="${ENV}" -e jenkins_admin_pass="${PASS}" && (
  JENKINS_HOST="$(kubectl get ingress ci-jenkins -n ci -o jsonpath="{.spec.rules[0].host}")"
  JENKINS_IP="$(kubectl get ingress ci-jenkins -n ci -o jsonpath="{.status.loadBalancer.ingress[0].ip}")"
  echo "Jenkins Url: https://${JENKINS_HOST}"
  echo "For example: curl -k --resolve \"${JENKINS_HOST}:443:${JENKINS_IP}\" https://${JENKINS_HOST}"
  echo "User: admin Password: ${PASS}"
)

#!/usr/bin/python
# -*- coding: utf-8 -*-
#TODO remove when Ansible merges https://github.com/ansible/ansible/pull/62450
# Copyright: Ansible Project
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)
from __future__ import absolute_import, division, print_function
__metaclass__ = type

ANSIBLE_METADATA = {'metadata_version': '1.1',
                    'status': ['preview'],
                    'supported_by': 'community'}

DOCUMENTATION = '''
---
module: helm_cli
short_description: Manages Kubernetes packages with the Helm package manager
description:
  - Install, upgrade, delete packages with the Helm package manager.
version_added: "2.10"
author:
  - Lucas Boisserie (@LucasBoisserie)
  - Matthieu Diehr (@d-matt)
requirements:
  - "helm (https://github.com/helm/helm/releases)"
  - "yaml (https://pypi.org/project/PyYAML/)"
options:
  binary_path:
    description:
      - The path of a helm binary to use, relative to the 'service_path'
        unless you supply an absolute path.
    required: false
    type: path
  chart_ref:
    description:
      - chart_reference on chart repository
      - path to a packaged chart
      - path to an unpacked chart directory
      - absolute URL
      - Required when release_state is set to present
    required: false
    type: str
  chart_repo_url:
    description:
      - Chart repository url where to locate the requested chart
    required: false
    type: str
  chart_repo_username:
    description:
      - Chart repository username where to locate the requested chart
      - Required if chart_repo_password is specified
    required: false
    type: str
  chart_repo_password:
    description:
      - Chart repository password where to locate the requested chart
      - Required if chart_repo_username is specified
    required: false
    type: str
  chart_version:
    description:
      - Chart version to install. If this is not specified, the latest version is installed
    required: false
    type: str
  release_name:
    description:
      - Release name to manage
    required: true
    type: str
    aliases: [ name ]
  release_namespace:
    description:
      - Kubernetes namespace where the chart should be installed
      - Can't be changed with helm 2
    default: "default"
    required: false
    type: str
    aliases: [ namespace ]
  release_state:
    choices: ['present', 'absent']
    description:
      - Desirated state of release
    required: false
    default: present
    aliases: [ state ]
    type: str
  release_values:
    description:
        - Value to pass to chart
    required: false
    default: {}
    aliases: [ values ]
    type: dict
  tiller_host:
    description:
      - Address of Tiller
      - Ignored when is helm 3
    type: str
  tiller_namespace:
    description:
      - Namespace of Tiller
      - Ignored when is helm 3
    default: "kube-system"
    type: str
  update_repo_cache:
    description:
      - Run `helm repo update` before the operation. Can be run as part of the package installation or as a separate step.
    default: "false"
    type: bool

#Helm options
  disable_hook:
    description:
      - Helm option to disable hook on install/upgrade/delete
    default: False
    type: bool
  force:
    description:
      - Helm option to force reinstall, ignore on new install
    default: False
    type: bool
  kube_context:
    description:
      - Helm option to specify which kubeconfig context to use
    type: str
  kubeconfig_path:
    description:
      - Helm option to specify kubeconfig path to use
    type: path
    aliases: [ kubeconfig ]
  purge:
    description:
      - Remove the release from the store and make its name free for later use
    default: True
    type: bool
  wait:
    description:
      - Wait until all Pods, PVCs, Services, and minimum number of Pods of a Deployment are in a ready state before marking the release as successful
    default: False
    type: bool
  wait_timeout:
    description:
      - Timeout when wait option is enabled (helm2 is a number of seconds, helm3 is a duration
    type: str
'''

EXAMPLES = '''
# With Helm 2
- name: Deploy grafana with params version
  helm_cli:
    name: test
    chart_ref: stable/grafana
    chart_version: 3.3.8
    tiller_namespace: helm
    values:
      replicas: 2

- name: Load Value from template
  helm_cli:
    name: test
    chart_ref: stable/grafana
    tiller_namespace: helm
    values: "{{ lookup('template', 'somefile.yaml') | from_yaml }}"

- name: Remove test release and waiting suppression ending
  helm_cli:
    name: test
    state: absent
    tiller_namespace: helm
    wait: true

# With Helm 3
- name: Create helm namespace HELM 3 doesn't create it automatically
  k8s:
    api_version: v1
    kind: Namespace
    name: "monitoring"
    wait: true

- name: Deploy latest version of Grafana chart inside monitoring namespace
  helm_cli:
    name: test
    chart_ref: stable/grafana
    release_namespace: monitoring
    values:
      replicas: 2

'''

RETURN = """
status:
  type: complex
  description: A dictionary of status output
  returned: on success Creation/Upgrade/Already deploy
  contains:
    appversion:
      type: str
      returned: always
      description: Version of app deployed
    chart:
      type: str
      returned: always
      description: Chart name and chart version
    name:
      type: str
      returned: always
      description: Name of the release
    namespace:
      type: str
      returned: always
      description: Namespace where the release is deployed
    revision:
      type: str
      returned: always
      description: Number of time where the release has been updated
    status:
      type: str
      returned: always
      description: Status of release (can be DEPLOYED, FAILED, ...)
    updated:
      type: str
      returned: always
      description: The Date of last update
    values:
      type: str
      returned: always
      description: Dict of Values used to deploy
stdout:
  type: str
  description: Full `helm` command stdout, in case you want to display it or examine the event log
  returned: always
  sample: ''
stderr:
  type: str
  description: Full `helm` command stderr, in case you want to display it or examine the event log
  returned: always
  sample: ''
command:
  type: str
  description: Full `helm` command built by this module, in case you want to re-run the command outside the module or debug a problem.
  returned: always
  sample: helm upgrade ...
"""

try:
    import yaml
    HAS_YAML = True
except ImportError:
    HAS_YAML = False

from ansible.module_utils.basic import AnsibleModule

module = None
is_helm_2 = True


# get Helm Version
def get_helm_client_version(command):
    is_helm_2_local = True
    version_command = command + " version --client --short"
    rc, out, err = module.run_command(version_command)

    if not out.startswith('Client: v2'):
        is_helm_2_local = False
        # Fallback on Helm 3
        version_command = command + " version --short"
        rc, out, err = module.run_command(version_command)

        if rc != 0:
            module.fail_json(
                msg="Failure when executing Helm command. Exited {0}.\nstdout: {1}\nstderr: {2}".format(rc, out, err),
                command=version_command
            )

    elif rc != 0:
        module.fail_json(
            msg="Failure when executing Helm command. Exited {0}.\nstdout: {1}\nstderr: {2}".format(rc, out, err),
            command=version_command
        )

    return is_helm_2_local


# Get Values from deployed release
def get_values(command, release_name, release_namespace):
    get_command = command + " get values --output=yaml " + release_name

    if not is_helm_2:
        get_command += " --namespace=" + release_namespace

    rc, out, err = module.run_command(get_command)

    if rc != 0:
        module.fail_json(
            msg="Failure when executing Helm command. Exited {0}.\nstdout: {1}\nstderr: {2}".format(rc, out, err),
            command=get_command
        )

    # Helm 3 return "null" string when no values are set
    if not is_helm_2 and out.rstrip("\n") == "null":
        return yaml.safe_load('{}')
    else:
        return yaml.safe_load(out)

# Get Release from all deployed releases
def get_release(state, release_name, release_namespace):
    if state is not None:
        if is_helm_2:
            for release in state['Releases']:
                # release = {k.lower(): v for k, v in release.items()} # NOT WORKING wit python 2.6
                release_lower = dict()
                for k, v in release.items():
                    release_lower[k.lower()] = v
                release = release_lower
                if release['name'] == release_name and release['namespace'] == release_namespace:
                    return release
        else:
            for release in state:
                if release['name'] == release_name and release['namespace'] == release_namespace:
                    return release
    return None


# Get Release state from deployed release
def get_release_status(command, release_name, release_namespace):
    list_command = command + " list --output=yaml "

    if not is_helm_2:
        list_command += " --namespace=" + release_namespace
        list_command += " --filter "

    list_command += release_name

    rc, out, err = module.run_command(list_command)

    if rc != 0:
        module.fail_json(
            msg="Failure when executing Helm command. Exited {0}.\nstdout: {1}\nstderr: {2}".format(rc, out, err),
            command=list_command
        )

    release = get_release(yaml.safe_load(out), release_name, release_namespace)

    if release is None:  # not install
        return None

    release['values'] = get_values(command, release_name, release_namespace)

    return release


# Run Repo update
def run_repo_update(command):
    repo_update_command = command + " repo update"

    rc, out, err = module.run_command(repo_update_command)
    if rc != 0:
        module.fail_json(
            msg="Failure when executing Helm command. Exited {0}.\nstdout: {1}\nstderr: {2}".format(rc, out, err),
            command=repo_update_command
        )


# Get chart info
def fetch_chart_info(command, chart_ref):
    if is_helm_2:
        inspect_command = command + " inspect chart " + chart_ref
    else:
        inspect_command = command + " show chart " + chart_ref

    rc, out, err = module.run_command(inspect_command)
    if rc != 0:
        module.fail_json(
            msg="Failure when executing Helm command. Exited {0}.\nstdout: {1}\nstderr: {2}".format(rc, out, err),
            command=inspect_command
        )

    return yaml.safe_load(out)


# Install/upgrade/rollback release chart
def deploy(command, release_name, release_namespace, release_values, chart_name, wait, wait_timeout, disable_hook, force):
    deploy_command = command + " upgrade -i"  # install/upgrade

    # Always reset values to keep release_values equal to values released
    deploy_command += " --reset-values"

    if wait:
        deploy_command += " --wait"
        if wait_timeout is not None:
            deploy_command += " --timeout " + wait_timeout

    if force:
        deploy_command += " --force"

    if disable_hook:
        deploy_command += " --no-hooks"

    if release_values != {}:
        try:
            import tempfile
        except ImportError:
            module.fail_json(msg="Could not import the tempfile python module. Please install `tempfile` package.")

        fd, path = tempfile.mkstemp(suffix='.yml')
        with open(path, 'w') as yaml_file:
            yaml.dump(release_values, yaml_file, default_flow_style=False)
        deploy_command += " -f=" + path

    deploy_command += " --namespace=" + release_namespace
    deploy_command += " " + release_name
    deploy_command += " " + chart_name

    return deploy_command


# Delete release chart for helm2
def delete_2(command, release_name, purge, disable_hook):
    delete_command = command + " delete"

    if purge:
        delete_command += " --purge"

    if disable_hook:
        delete_command += " --no-hooks"

    delete_command += " " + release_name

    return delete_command


# Delete release chart for helm3
def delete_3(command, release_name, release_namespace, purge, disable_hook):
    delete_command = command + " uninstall --namespace=" + release_namespace

    if not purge:
        delete_command += " --keep-history"

    if disable_hook:
        delete_command += " --no-hooks"

    delete_command += " " + release_name

    return delete_command


def main():
    global module, is_helm_2
    module = AnsibleModule(
        argument_spec=dict(
            binary_path=dict(type='path'),
            chart_ref=dict(type='str'),
            chart_repo_url=dict(type='str'),
            chart_repo_username=dict(type='str'),
            chart_repo_password=dict(type='str', no_log=True),
            chart_version=dict(type='str'),
            release_name=dict(type='str', required=True, aliases=['name']),
            release_namespace=dict(type='str', default='default', aliases=['namespace']),
            release_state=dict(default='present', choices=['present', 'absent'], aliases=['state']),
            release_values=dict(type='dict', default={}, aliases=['values']),
            tiller_host=dict(type='str'),
            tiller_namespace=dict(type='str', default='kube-system'),
            update_repo_cache=dict(type='bool', default=False),

            # Helm options
            disable_hook=dict(type='bool', default=False),
            force=dict(type='bool', default=False),
            kube_context=dict(type='str'),
            kubeconfig_path=dict(type='path', aliases=['kubeconfig']),
            purge=dict(type='bool', default=True),
            wait=dict(type='bool', default=False),
            wait_timeout=dict(type='str'),
        ),
        required_if=[
            ('release_state', 'present', ['release_name', 'chart_ref']),
            ('release_state', 'absent', ['release_name'])

        ],
        required_together=[
            ['chart_repo_username', 'chart_repo_password']
        ],
        supports_check_mode=True,
    )

    if not HAS_YAML:
        module.fail_json(msg="Could not import the yaml python module. Please install `yaml` package.")
    changed = False

    bin_path = module.params.get('binary_path')
    chart_ref = module.params.get('chart_ref')
    chart_repo_url = module.params.get('chart_repo_url')
    chart_repo_username = module.params.get('chart_repo_username')
    chart_repo_password = module.params.get('chart_repo_password')
    chart_version = module.params.get('chart_version')
    release_name = module.params.get('release_name')
    release_namespace = module.params.get('release_namespace')
    release_state = module.params.get('release_state')
    release_values = module.params.get('release_values')
    tiller_host = module.params.get('tiller_host')
    tiller_namespace = module.params.get('tiller_namespace')
    update_repo_cache = module.params.get('update_repo_cache')

    # Helm options
    disable_hook = module.params.get('disable_hook')
    force = module.params.get('force')
    kube_context = module.params.get('kube_context')
    kubeconfig_path = module.params.get('kubeconfig_path')
    purge = module.params.get('purge')
    wait = module.params.get('wait')
    wait_timeout = module.params.get('wait_timeout')

    if bin_path is not None:
        helm_cmd_common = bin_path
    else:
        helm_cmd_common = module.get_bin_path('helm', required=True)

    is_helm_2 = get_helm_client_version(helm_cmd_common)

    # Helm 2 need tiller, Helm 3 and higher doesn't
    if is_helm_2:
        if tiller_host is not None:
            helm_cmd_common += " --host=" + tiller_namespace
        else:
            helm_cmd_common += " --tiller-namespace=" + tiller_namespace

    if kube_context is not None:
        helm_cmd_common += " --kube-context " + kube_context

    if kubeconfig_path is not None:
        helm_cmd_common += " --kubeconfig " + kubeconfig_path

    if update_repo_cache:
        run_repo_update(helm_cmd_common)

    # Get real/deployed release status
    release_status = get_release_status(helm_cmd_common, release_name, release_namespace)

    # keep helm_cmd_common for get_release_status in module_exit_json
    helm_cmd = helm_cmd_common
    if release_state == "absent" and release_status is not None:
        if is_helm_2:
            helm_cmd = delete_2(helm_cmd, release_name, purge, disable_hook)
        else:
            helm_cmd = delete_3(helm_cmd, release_name, release_namespace, purge, disable_hook)
        changed = True
    elif release_state == "present":

        if chart_version is not None:
            helm_cmd += " --version=" + chart_version

        if chart_repo_url is not None:
            helm_cmd += " --repo=" + chart_repo_url
            if chart_repo_username is not None and chart_repo_password is not None:
                helm_cmd += " --username=" + chart_repo_username
                helm_cmd += " --password=" + chart_repo_password

        # Fetch chart info to have real version and real name for chart_ref from archive, folder or url
        chart_info = fetch_chart_info(helm_cmd, chart_ref)

        if release_status is None:  # Not installed
            helm_cmd = deploy(helm_cmd, release_name, release_namespace, release_values, chart_ref, wait, wait_timeout,
                              disable_hook, False)
            changed = True

        elif is_helm_2 and release_namespace != release_status['namespace']:
            module.fail_json(
                msg="With helm2, Target Namespace can't be changed on deployed chart ! Need to destroy the release "
                    "and recreate it "
            )

        elif force or release_values != release_status['values'] \
                or (chart_info['name'] + '-' + chart_info['version']) != release_status["chart"]:
            helm_cmd = deploy(helm_cmd, release_name, release_namespace, release_values, chart_ref, wait, wait_timeout,
                              disable_hook, force)
            changed = True

    if module.check_mode:
        module.exit_json(changed=changed)
    elif not changed:
        module.exit_json(changed=False, status=release_status)

    rc, out, err = module.run_command(helm_cmd)

    if rc != 0:
        module.fail_json(
            msg="Failure when executing Helm command. Exited {0}.\nstdout: {1}\nstderr: {2}".format(rc, out, err),
            command=helm_cmd
        )

    module.exit_json(changed=changed, stdout=out, stderr=err,
                     status=get_release_status(helm_cmd_common, release_name, release_namespace), command=helm_cmd)


if __name__ == '__main__':
    main()
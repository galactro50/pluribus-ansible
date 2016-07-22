#!/usr/bin/python
""" PN CLI cluster-create/cluster-delete """

import subprocess
import shlex

DOCUMENTATION = """
---
module: pn_cluster
author: "Pluribus Networks"
short_description: CLI command to create/delete a cluster
description:
  - Execute cluster-create or cluster-delete command. 
  - A cluster allows two switches to cooperate in high-availability (HA) 
    deployments. The nodes that form the cluster must be members of the same 
    fabric. Clusters are typically used in conjunction with a virtual link 
    aggregation group (VLAG) that allows links physically connected to two
    separate switches appear as a single trunk to a third device. The third 
    device can be a switch,server, or any Ethernet device.
options:
  pn_cliusername:
    description:
      - Login username
    required: true
    type: str
  pn_clipassword:
    description:
      - Login password
    required: true
    type: str
  pn_cliswitch:
    description:
    - Target switch to run the cli on.
    required: False
    type: str
  pn_command:
    description:
      - The C(pn_command) takes the cluster-create/cluster-delete command
      as value.
    required: true
    choices: cluster-create, cluster-delete
    type: str
  pn_name:
    description:
      - Specify the name of the cluster.
    required: true
    type: str
  pn_cluster_node1:
    description:
      - Specify the name of the first switch in the cluster.
    required_if: cluster-create
    type: str
  pn_cluster_node2:
    description:
      - Specify the name of the second switch in the cluster.
    required_if: cluster-create
    type: str
  pn_validate:
    description:
      - validate the inter-switch links and state of switches in the cluster.
    choices: validate, no-validate
    type: str
  pn_quiet:
    description:
      - Enable/disable system information.
    required: false
    type: bool
    default: true
"""

EXAMPLES = """
- name: create spine cluster
  pn_cluster:
    pn_cliusername: admin
    pn_clipassword: admin
    pn_command: 'cluster-create'
    pn_name: 'spine-cluster'
    pn_cluster_node1: 'spine01'
    pn_cluster_node2: 'spine02'
    pn_validate: validate
    pn_quiet: True

- name: delete spine cluster
  pn_cluster:
    pn_cliusername: admin
    pn_clipassword: admin
    pn_command: 'cluster-delete'
    pn_name: 'spine-cluster'
    pn_quiet: True
"""

RETURN = """
command:
  description: the CLI command run on the target node(s).
stdout:
  description: the set of responses from the cluster command.
  returned: always
  type: list
stderr:
  description: the set of error responses from the cluster command.
  returned: on error
  type: list
rc:
  description: return code of the module.
  returned: 0 on success, 1 on error
  type: int
changed:
  description: Indicates whether the CLI caused changes on the target.
  returned: always
  type: bool
"""


def main():
    """ This section is for arguments parsing """
    module = AnsibleModule(
        argument_spec=dict(
            pn_cliusername=dict(required=True, type='str',
                                aliases=['username']),
            pn_clipassword=dict(required=True, type='str',
                                aliases=['password']),
            pn_cliswitch=dict(required=False, type='str', aliases=['switch']),
            pn_command=dict(required=True, type='str',
                            choices=['cluster-create', 'cluster-delete'],
                            aliases=['command']),
            pn_name=dict(required=True, type='str', aliases=['name']),
            pn_cluster_node1=dict(type='str', aliases=['cluster_node1']),
            pn_cluster_node2=dict(type='str', aliases=['cluster_node2']),
            pn_validate=dict(type='str', choices=['validate', 'no-validate'],
                             aliases=['validate']),
            pn_quiet=dict(default=True, type='bool', aliases=['quiet'])
        ),
        required_if=(
            ["pn_command", "cluster-create",
             ["pn_name", "pn_cluster_node1", "pn_cluster_node2"]],
            ["pn_command", "cluster-delete", ["pn_name"]]
        )
    )

    # Accessing the parameters
    cliusername = module.params['pn_cliusername']
    clipassword = module.params['pn_clipassword']
    cliswitch = module.params['pn_cliswitch']
    command = module.params['pn_command']
    name = module.params['pn_name']
    cluster_node1 = module.params['pn_clusternode1']
    cluster_node2 = module.params['pn_clusternode2']
    validate = module.params['pn_validate']
    quiet = module.params['pn_quiet']

    # Building the CLI command string
    if quiet is True:
        cli = ('/usr/bin/cli --quiet --user ' + cliusername + ':' +
               clipassword + ' ')
    else:
        cli = '/usr/bin/cli --user ' + cliusername + ':' + clipassword + ' '

    if cliswitch:
        cli += ' switch ' + cliswitch

    cli += ' ' + command + ' name ' + name

    if cluster_node1:
        cli += ' cluster-node-1 ' + cluster_node1

    if cluster_node2:
        cli += ' cluster-node-2 ' + cluster_node2

    if validate:
        cli += ' ' + validate

    # Run the CLI command
    clustercmd = shlex.split(cli)
    response = subprocess.Popen(clustercmd, stderr=subprocess.PIPE,
                                stdout=subprocess.PIPE, universal_newlines=True)

    # 'out' contains the output
    # 'err' contains the error messages
    out, err = response.communicate()

    # Response in JSON format
    if err:
        module.exit_json(
            command=cli,
            stderr=err.rstrip("\r\n"),
            rc=0,
            changed=False
        )

    else:
        module.exit_json(
            command=cli,
            stdout=out.rstrip("\r\n"),
            rc=1,
            changed=True
        )


# AnsibleModule boilerplate
from ansible.module_utils.basic import AnsibleModule

if __name__ == '__main__':
    main()


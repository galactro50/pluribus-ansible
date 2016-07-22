#!/usr/bin/python
""" PN CLI trunk-create/trunk-delete/trunk-modify """

import subprocess
import shlex

DOCUMENTATION = """
---
module: pn_trunk
author: "Pluribus Networks"
short_description: CLI command to create/delete/modify a trunk
description:
  - Execute trunk-create or trunk-delete command.
  - Trunks can be used to aggregate network links at Layer 2 on the local
    switch. Use this command to create a new trunk.
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
      - The C(pn_command) takes the trunk commands as value.
    required: true
    choices: trunk-create, trunk-delete, trunk-modify
    type: str
  pn_name:
    description:
      - Specify the name for the trunk configuration.
    required: true
    type: str
  pn_ports:
    description:
      - Specify the port number(s) for the link(s) to aggregate into the trunk.
    required_if: trunk-create
    type: str
  pn_speed:
    description:
      - Specify the port speed or disable the port.
    required: false
    choices: disable, 10m, 100m, 1g, 2.5g, 10g, 40g
    type: str
  pn_egress_rate_limit:
    description:
      - Specify an egress port data rate limit for the configuration.
    type: str
  pn_jumbo:
    description
      - Specify if the port can receive jumbo frames.
    type: bool
  pn_lacp_mode:
    description:
      - Specify the LACP mode for the configuration.
    choices: off, passive, active
    type: str
  pn_lacp_priority:
    description
      - Specify the LACP priority. This is a number between 1 and 65535 with a
        default value of 32768.
    type: int
  pn_lacp_timeout:
    description:
      - Specify the LACP time out as slow (30 seconds) or fast (4seconds).
        The default value is slow.
    choices: slow, fast
    type: str
  pn_lacp_fallback:
    description:
      - Specify the LACP fallback mode as bundles or individual.
    choices: bundle, individual
    type: str
  pn_lacp_fallback_timeout:
    description:
      - Specify the LACP fallback timeout in seconds. The range is between 30
        and 60 seconds with a default value of 50 seconds.
    type: str
  pn_edge_switch:
    description:
      - Specify if the switch is an edge switch.
    type: bool
  pn_pause:
    description:
      - Specify if pause frames are sent.
    type: bool
  pn_description:
    description:
      - Specify a description for the trunk configuration.
    type: str
  pn_loopback:
    description;
      - Specify loopback if you want to use loopback.
    type: bool
  pn_mirror_receive:
    description:
      - Specify if the configuration receives mirrored traffic.
    type: bool
  pn_unkown_ucast_level:
    description:
      - Specify an unkown unicast level in percent. The default value is 100%.
    type: str
  pn_unkown_mcast_level:
    description:
      - Specify an unkown multicast level in percent. The default value is 100%.
    type: str
  pn_broadcast_level:
    description:
      - Specify a broadcast level in percent. The default value is 100%.
    type: str
  pn_port_macaddr:
    description:
      - Specify the MAC address of the port.
    type: str
  pn_loopvlans:
    description:
      - Specify a list of looping vlans.
    type: str
  pn_routing:
    description:
      - Specify if the port participates in routing on the network.
    type: bool
  pn_host:
    description:
      - Host facing port control setting.
    type: bool
  pn_quiet:
    description:
      - Enable/disable system information.
    required: false
    type: bool
    default: true
"""

EXAMPLES = """
- name: create trunk
  pn_trunk:
    pn_cliusername: admin
    pn_clipassword: admin
    pn_command: 'trunk-create'
    pn_name: 'spine-to-leaf'


- name: delete trunk
  pn_trunk:
    pn_cliusername: admin
    pn_clipassword: admin
    pn_command: 'trunk-delete'
    pn_name: 'spine-to-leaf'
"""

RETURN = """
command:
  description: the CLI command run on the target node(s).
stdout:
  description: the set of responses from the trunk command.
  returned: always
  type: list
stderr:
  description: the set of error responses from the trunk command.
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
    """ This portion is for arguments parsing """
    module = AnsibleModule(
        argument_spec=dict(
            pn_cliusername=dict(required=True, type='str',
                                aliases=['username']),
            pn_clipassword=dict(required=True, type='str',
                                aliases=['password']),
            pn_cliswitch=dict(required=False, type='str', aliases=['switch']),
            pn_command=dict(required=True, type='str',
                            choices=['trunk-create', 'trunk-delete',
                                     'trunk-modify'], aliases=['switch']),
            pn_name=dict(required=True, type='str', aliases=['name']),
            pn_ports=dict(type='str', aliases=['ports']),
            pn_speed=dict(type='str',
                          choices=['disable', '10m', '100m', '1g', '2.5g',
                                   '10g', '40g'], aliases=['speed']),
            pn_egress_rate_limit=dict(type='str',
                                      aliases=['egress_rate_limit']),
            pn_jumbo=dict(type='bool', aliases=['jumbo']),
            pn_lacp_mode=dict(type='str', choices=['off', 'passive', 'active'],
                              aliases=['lacp_mode']),
            pn_lacp_priority=dict(type='int', aliases=['lacp_priority']),
            pn_lacp_timeout=dict(type='str', choices=['slow', 'fast'],
                                 aliases=['lacp_timeout']),
            pn_lacp_fallback=dict(type='str', choices=['bundle', 'individual'],
                                  aliases=['lacp_fallback']),
            pn_lacp_fallback_timeout=dict(type='str',
                                          aliases=['lacp_fallback_timeout']),
            pn_edge_switch=dict(type='bool', aliases=['edge_switch']),
            pn_pause=dict(type='bool', aliases=['pause']),
            pn_description=dict(type='str', aliases=['description']),
            pn_loopback=dict(type='bool', aliases=['loopback']),
            pn_mirror_receive=dict(type='bool', aliases=['mirror_receive']),
            pn_unknown_ucast_level=dict(type='str',
                                        aliases=['unkown_ucast_level']),
            pn_unknown_mcast_level=dict(type='str',
                                        aliases=['unkown_mcast_level']),
            pn_broadcast_level=dict(type='str', aliases=['broadcast_level']),
            pn_port_macaddr=dict(type='str', aliases=['port_macaddr']),
            pn_loopvlans=dict(type='str', aliases=['loopvlans']),
            pn_routing=dict(type='bool', aliases=['routing']),
            pn_host=dict(type='bool', aliases=['host']),
            pn_quiet=dict(default=True, type='bool', aliases=['quiet'])
        ),
        required_if=(
            ["pn_command", "trunk-create", ["pn_name", "pn_ports"]],
            ["pn_command", "trunk-delete", ["pn_name"]],
            ["pn_command", "trunk-modify", ["pn_name"]]
        )
    )

    cliusername = module.params['pn_cliusername']
    clipassword = module.params['pn_clipassword']
    cliswitch = module.params['pn_cliswitch']
    command = module.params['pn_command']
    name = module.params['pn_name']
    ports = module.params['pn_ports']
    speed = module.params['pn_speed']
    egress_rate_limit = module.params['pn_egress_rate_limit']
    jumbo = module.params['pn_jumbo']
    lacp_mode = module.params['pn_lacp_mode']
    lacp_priority = module.params['pn_lacp_priority']
    lacp_timeout = module.params['pn_lacp_timeout']
    lacp_fallback = module.params['pn_lacp_fallback']
    lacp_fallback_timeout = module.params['pn_lacp_fallback_timeout']
    edge_switch = module.params['pn_edge_switch']
    pause = module.params['pn_pause']
    description = module.params['pn_description']
    loopback = module.params['pn_loopback']
    mirror_receive = module.params['pn_mirror_receive']
    unknown_ucast_level = module.params['pn_unknown_ucast_level']
    unknown_mcast_level = module.params['pn_unknown_mcast_level']
    broadcast_level = module.params['pn_broadcast_level']
    port_macaddr = module.params['pn_port_macaddr']
    loopvlans = module.params['pn_loopvlans']
    routing = module.params['pn_routing']
    host = module.params['pn_host']
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

    if ports:
        cli += ' ports ' + ports

    if speed:
        cli += ' speed ' + speed

    if egress_rate_limit:
        cli += ' egress-rate-limit ' + egress_rate_limit

    if jumbo is True:
        cli += ' jumbo '
    if jumbo is False:
        cli += ' no-jumbo '

    if lacp_mode:
        cli += ' lacp-mode ' + lacp_mode

    if lacp_priority:
        cli += ' lacp-priority ' + lacp_priority

    if lacp_timeout:
        cli += ' lacp-timeout ' + lacp_timeout

    if lacp_fallback:
        cli += ' lacp-fallback ' + lacp_fallback

    if lacp_fallback_timeout:
        cli += ' lacp-fallback-timeout ' + lacp_fallback_timeout

    if edge_switch is True:
        cli += ' edge-switch '
    if edge_switch is False:
        cli += ' no-edge-switch '

    if pause is True:
        cli += ' pause '
    if pause is False:
        cli += ' no-pause '

    if description:
        cli += ' description ' + description

    if loopback is True:
        cli += ' loopback '
    if loopback is False:
        cli += ' no-loopback '

    if mirror_receive is True:
        cli += ' mirror-receive-only '
    if mirror_receive is False:
        cli += ' no-mirror-receive-only '

    if unknown_ucast_level:
        cli += ' unknown-ucast-level ' + unknown_ucast_level

    if unknown_mcast_level:
        cli += ' unknown-mcast-level ' + unknown_mcast_level

    if broadcast_level:
        cli += ' broadcast-level ' + broadcast_level

    if port_macaddr:
        cli += ' port-mac-address ' + port_macaddr

    if loopvlans:
        cli += ' loopvlans ' + loopvlans

    if routing is True:
        cli += ' routing '
    if routing is False:
        cli += ' no-routing '

    if host is True:
        cli += ' host-enable '
    if host is False:
        cli += ' host-disable '

    # Run the CLI command
    trunkcmd = shlex.split(cli)
    response = subprocess.Popen(trunkcmd, stderr=subprocess.PIPE,
                                stdout=subprocess.PIPE, universal_newlines=True)

    # 'out' contains the output
    # 'err' contains the err messages
    out, err = response.communicate()

    # Response in json format
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

# Ansible boiler-plate
from ansible.module_utils.basic import AnsibleModule

if __name__ == '__main__':
    main()


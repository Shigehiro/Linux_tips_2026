import pulumi
import pulumi_cloudinit as cloudinit
import pulumi_libvirt as libvirt

pulumi_pool = libvirt.Pool("pulumi_pool",
  type = "dir",
  path = "/var/lib/libvirt/images/my_pool"
)

cent10 = libvirt.Volume("cent10",
  pool   = pulumi_pool.name,
  source = "/qcow2/CentOS-Stream-GenericCloud-x86_64-10-20260622.0.x86_64.qcow2",
  format = "qcow2",
)

# pool size must be larger than the volume size
filesystem = libvirt.Volume("filesystem",
  base_volume_id = cent10.id,
  pool           = pulumi_pool.name,
  size           = 10*1024*1024*1024 # 10GB
)

pulumi_network = libvirt.Network("pulumi_network",
    addresses=[
        "10.17.3.0/24",
    ],
    dns={
        "enabled": True,
        "local_only": True,
    },
    dnsmasq_options={},
    domain="puluminetwork.local",
    mode="nat")

# Define the cloud-init configuration parts
# Part 1: cloud-config data to install nginx and create a file
cloud_config_content = """#cloud-config
users:
  - name: centos
    sudo: ALL=(ALL) NOPASSWD:ALL
    shell: /bin/bash
    groups: sudo, wheel
    ssh_authorized_keys:
        - ssh-ed25519 ...
    password: centos
    chpasswd: {expire: False}
    ssh_pwauth: True
runcmd:
  - echo "Hello from cloud-init!" > /tmp/hello.txt
"""

# Part 2: a shell script to run
# When gzip and base64_encode are True, the cloud-init config is not rendered correctly.
shell_script_content = """#!/bin/bash
echo "This is a shell script part." >> /tmp/cloud-init-log.txt
"""

cloud_init_config = cloudinit.Config("cloud-init-config",
    parts=[
        cloudinit.ConfigPartArgs(
            content=cloud_config_content,
            content_type="text/cloud-config",
            filename="config.yaml",
        ),
        cloudinit.ConfigPartArgs(
            content=shell_script_content,
            content_type="text/x-shellscript",
            filename="script.sh",
        ),
    ],
    gzip=False,          # Optionally gzip the output
    base64_encode=False  # Optionally base64 encode the output (default)
)


cloud_init_disk = libvirt.CloudinitDisk("cloudinit-disk",
    name="vm-cloudinit-disk.iso",
    user_data=cloud_init_config.rendered, # Pass the rendered MIME config here
    pool = pulumi_pool.name,
)

domain = libvirt.Domain("cent10",
  type = "kvm",
  graphics = libvirt.DomainGraphicsArgs(type="vnc"),
  autostart = False,
  cpu = {
    "mode": "host-passthrough",
  },
  memory = 2048, # 2GB
  cloudinit = cloud_init_disk.id,
  consoles=[libvirt.DomainConsoleArgs(
    type = "pty",
    target_type = "serial",
    target_port = "0",
  )],
  vcpu = 2,
  disks = [libvirt.DomainDiskArgs(
    volume_id = filesystem.id,
  )],
  network_interfaces = [libvirt.DomainNetworkInterfaceArgs(
    network_id = pulumi_network.id,
    wait_for_lease = True,
  )],
)

pulumi.export("VM name", domain.name)
pulumi.export("cloud_init_output", cloud_init_config.rendered)

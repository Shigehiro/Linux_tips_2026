# Using the Pulumi (Python) Docker Image to Manage libvirt

## Description

This guide explains how to use the Pulumi Docker image to manage libvirt resources.

## Host OS

```bash
$ cat /etc/centos-release
CentOS Stream release 10 (Coughlan)

$ getenforce
Permissive

$ sudo grep ^uri_default /etc/libvirt/libvirt.conf
uri_default = "qemu:///system"
```

## Walkthrough

Enable the rootless Podman socket:

```bash
systemctl --user enable --now podman.socket
```

Confirm that `podman.socket` is enabled:

```bash
systemctl --user status podman.socket
```

Configure the environment variables so that Pulumi commands can be executed non-interactively from a single command line:

```bash
export PULUMI_CONFIG_PASSPHRASE='...'
```

Launch the container:

```bash
podman run -it -d \
  -v /run/user/$(id -u)/podman/podman.sock:/var/run/docker.sock:Z \
  -v /var/run/libvirt/libvirt-sock:/var/run/libvirt/libvirt-sock \
  -v $(pwd):/app \
  -w /app \
  -v ${HOME}/Qcow2:/qcow2 \
  -e PULUMI_BACKEND_URL="file://~" \
  -e PULUMI_CONFIG_PASSPHRASE=${PULUMI_CONFIG_PASSPHRASE} \
  -e DOCKER_HOST=unix:///var/run/docker.sock \
  --entrypoint bash \
  docker.io/pulumi/pulumi-python:3.257.0-debian
```

Install the required package:

```bash
podman exec vigorous_williams apt install -y genisoimage
```

Create a new Pulumi project:

```bash
podman exec \
  vigorous_williams \
  /pulumi/bin/pulumi new python \
  --yes \
  --name "my-project" \
  --runtime-options toolchain=uv \
  --runtime-options virtualenv=.venv
```

Add the libvirt provider package:

```bash
pulumi package add terraform-provider registry.opentofu.org/dmacvicar/libvirt 0.8.3
```

Install the required Python package:

```bash
podman exec vigorous_williams uv add pulumi_cloudinit
```

Configure the libvirt URI:

```bash
podman exec vigorous_williams /pulumi/bin/pulumi config set libvirt:uri qemu:///system
```

Verify the configuration:

```bash
$ podman exec vigorous_williams /pulumi/bin/pulumi config

KEY          VALUE
libvirt:uri  qemu:///system
pulumi:tags  {"pulumi:template":"python"}
```

Edit `__main__.py` and deploy the VM:

```bash
podman exec vigorous_williams /pulumi/bin/pulumi up -y
```

Verify that the VM is running:

```bash
$ virsh list

 Id   Name             State
--------------------------------
 1    cent10-02c8665   running
```

Confirm that you can access the VM.

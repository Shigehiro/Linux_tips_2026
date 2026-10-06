# Set Up Ollama with an AMD Ryzen 9 7940HS w/ Radeon 780M Graphics

## Reference

- [Running a Local LLM on AMD Radeon 780M (gfx1103) with ROCm](https://www.k8s.it/posts/running-a-local-llm-on-amd-radeon-780m-gfx1103-rocm-and-the-gpu-that-wasnt-supposed-to-work/)
- [Ollama GPU Support for AMD Radeon](https://docs.ollama.com/gpu#amd-radeon)

## Walkthrough

Set up Ollama in a Podman container.

```bash
$ cat /etc/centos-release 
CentOS Stream release 10 (Coughlan)

$ uname -ri
6.12.0-271.el10.x86_64 unknown

$ grep 'model name' /proc/cpuinfo | uniq
model name      : AMD Ryzen 9 7940HS w/ Radeon 780M Graphics

$ free -mh
               total        used        free      shared  buff/cache   available
Mem:            60Gi       2.5Gi        55Gi        19Mi       2.4Gi        57Gi
Swap:           30Gi          0B        30Gi

$ getenforce 
Permissive
```

<br>Confirm that /dev/kfd and /dev/dri are available.
```bash
$ ls /dev/kfd /dev/dri
/dev/kfd

/dev/dri:
by-path  card0  renderD128
```

<br>The architecture of the Radeon 780M Graphics is gfx1103, which is not officially supported by Ollama. However, you can use this GPU by specifying HSA_OVERRIDE_GFX_VERSION=11.0.2, as shown below.
```
$ amdgpu-arch
gfx1103
```

```bash
$ mkdir ollama
```

<br>Start the container:
```bash
sudo podman run -d \
  --name ollama \
  --device /dev/kfd --device /dev/dri \
  --group-add keep-groups \
  -e HSA_OVERRIDE_GFX_VERSION="11.0.2" \
  -e OLLAMA_IGPU_ENABLE=1 \
  -v ./ollama:/root/.ollama \
  -p 11434:11434 \
  --cpus 4 \
  --shm-size 2g \
  docker.io/ollama/ollama:rocm
```

<br>Check the logs to confirm that Ollama recognizes the GPU.
```bash
$ sudo podman logs ollama
...

time=2026-10-06T07:32:12.833Z level=INFO source=runner.go:60 msg="discovering available GPUs..."
time=2026-10-06T07:32:12.834Z level=WARN source=runner.go:722 msg="user overrode visible devices" HSA_OVERRIDE_GFX_VERSION=11.0.2
time=2026-10-06T07:32:12.834Z level=WARN source=runner.go:726 msg="if GPUs are not correctly discovered, unset and try again"
time=2026-10-06T07:32:13.176Z level=INFO source=types.go:32 msg="inference compute" id=0 filter_id=0 library=ROCm compute=gfx1102 name=ROCm0 description="AMD Radeon 780M Graphics" libdirs=ollama,rocm_v7_2 driver=0.0 pci_id=0000:c4:00.0 type=iGPU total="30.1 GiB" available="30.1 GiB"
time=2026-10-06T07:32:13.176Z level=INFO source=routes.go:2050 msg="vram-based default context" total_vram="30.1 GiB" default_num_ctx=32768
time=2026-10-06T07:32:13.196Z level=INFO source=model_recommendations.go:177 msg="model recommendations cache sleep scheduled" wait=3h46m1.798194751s consecutive_failures=0
```

<br>Pull a model:
```bash
$ sudo podman exec ollama ollama pull gemma3:4b
```

<br>Run a prompt:
```bash
$ sudo podman exec -it ollama bash

root@022a4e38caa9:/# ollama list
NAME         ID              SIZE      MODIFIED
gemma3:4b    a2af6cc3eb7f    3.3 GB    About a minute ago

root@022a4e38caa9:/# ollama run gemma3:4b
>>> why is the sky blue?

...
```

<br>Confirm that Ollama is using the GPU:
```bash
$ sudo podman exec ollama ollama ps
NAME         ID              SIZE      PROCESSOR    CONTEXT    UNTIL
gemma3:4b    a2af6cc3eb7f    3.1 GB    100% GPU     32768      4 minutes from now    
```

<br>Here is the GPU RAM allocation.
```
$ cat /sys/class/drm/card0/device/mem_info_gtt_used
4812259328

$ cat /sys/class/drm/card0/device/mem_info_gtt_total
32366415872
```

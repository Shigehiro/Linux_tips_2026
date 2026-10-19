# Set up OpenClaw and connect it to a local LLM(Ollama)

As for setting up Ollama, please see [Set Up Ollama with an AMD Ryzen 9 7940HS w/ Radeon 780M Graphics](https://github.com/Shigehiro/Linux_tips_2026/blob/main/Ollama_AMD_Ryzen9_7940HS_Radeon780M/README.md)

## Walkthough

Run the Ollama continaer. This container allows an access from the remote nodes, so please take care the security matters.
```bash
sudo podman run -d \
  --name ollama \
  --device /dev/kfd --device /dev/dri \
  --group-add keep-groups \
  -e HSA_OVERRIDE_GFX_VERSION="11.0.2" \
  -e OLLAMA_IGPU_ENABLE=1 \
  -v ./ollama:/root/.ollama \
  -p 11434:11434 \
  -e OLLAMA_HOST=0.0.0.0:11434 \
  -e OLLAMA_ORIGINS="*" \
  --cpus 4 \
  --shm-size 2g \
  docker.io/ollama/ollama:rocm
```
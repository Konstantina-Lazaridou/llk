# Optional installation

The `pyproject.toml` contains various dependencies that are needed for notebooks used for development. Some additional dependencies and configurations are necessary and explained below.

### Quantized models

To use quantized models for inference, additional non poetry libraries need to be installed:

- Flash attention installation according to the official documentation (version: flash_attn==2.7.4.post1)
- Autoawq installation (autoawq==0.2.8) as follows:
```
pip install --upgrade pip setuptools wheel
pip install autoawq
```

### Ollama

Install ollama according to the official documentation: https://github.com/ollama/ollama.
Access ollama endpoint:
```
ollama start
ollama run llama3.2
curl http://localhost:11434/v1/models
ollama show llama3.2
```

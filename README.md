# 🧾 AI Receipt Extractor (Qwen-1.5B Fine-Tuned)

Transforming messy, colloquial transaction text into deterministic, structured JSON schemas using Parameter-Efficient Fine-Tuning (QLoRA).

## 🧠 The Problem
Out-of-the-box LLMs treat data extraction as a conversation. When asked to parse a receipt, they inject preamble (`"Sure! Here is your JSON:"`) and hallucinate keys, breaking automated software pipelines.

## ⚡ The Solution
Fine-tuned **Qwen2.5-1.5B** using **QLoRA** (4-bit `nf4` quantization) to force strict JSON compliance with zero conversational overhead.

* **Base Model:** `Qwen/Qwen2.5-1.5B`
* **Technique:** LoRA (`r=16`, targeting attention heads: `q_proj`, `k_proj`, `v_proj`, `o_proj`)
* **Efficiency:** Trained on just **3.5M parameters** (0.22% of the total network) on a single free T4 GPU.

## 🎯 Live Output Example

**Unseen Test Input:**
> "Snagged 4 energy drinks at CVS for 11.20 total."

**Model Output:**
```json
{"store": "CVS", "items": [{"name": "energy drinks", "qty": 4, "unit_price": 2.80}]}


## 🛠️ Exporting the Custom LoRA to Ollama (.gguf)

Because standard `llama.cpp` compilers fail when encountering modernized HuggingFace `.safetensors` LoRAs, this repo contains a self-healing Colab export bridge: `colab_lora_exporter.py`.

### Usage inside Google Colab:
1. Finish running your `SFTTrainer` cell.
2. Drop a new code cell at the bottom of your notebook and run:

```python
# Download the script from this repository and run it live
!wget [https://raw.githubusercontent.com/YOUR_GITHUB_NAME/cashier-ai/main/colab_lora_exporter.py](https://raw.githubusercontent.com/YOUR_GITHUB_NAME/cashier-ai/main/colab_lora_exporter.py)
!python colab_lora_exporter.py

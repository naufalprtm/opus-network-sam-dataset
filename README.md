# Modeling Opux - A Dynamic QA Pair Generation Framework

This repository houses a collection of Python scripts designed to generate and validate dynamic question-answer (QA) pairs using various NLP models and APIs. The scripts are optimized for both GPU and CPU environments and include advanced techniques for batch processing, logging, and answer validation.

## Table of Contents

1. [Overview](#overview)
2. [File Descriptions](#file-descriptions)
   - [modeling_opux_gpu.py](#modeling_opux_gpupy)
   - [modeling_opux_gemini.py](#modeling_opux_geminipy)
   - [modeling_opux_cpu.py](#modeling_opux_cpupy)
3. [Installation](#installation)
4. [Usage](#usage)
   - [Running the GPU Script](#running-the-gpu-script)
   - [Running the Gemini Script](#running-the-gemini-script)
   - [Running the CPU Script](#running-the-cpu-script)
5. [Configuration](#configuration)
6. [Output](#output)
7. [Logging](#logging)

## Overview

This repository contains Python scripts designed to generate and validate dynamic QA pairs, using various NLP models and APIs. The scripts leverage both GPU and CPU-based models for text generation and incorporate advanced techniques for batch processing, logging, and answer validation.

## File Descriptions

### 1. `modeling_opux_gpu.py`
This script is optimized for running on GPU-enabled environments. It uses the Hugging Face `transformers` library to load and interact with the GPT-2 model. The primary purpose of this script is to generate QA pairs based on a set of predefined keywords, job titles, and topics.

#### Key Features:
- **GPU Utilization:** Automatically detects and uses GPU if available.
- **Dynamic Topic Generation:** Generates random topics based on a predefined list of keywords.
- **QA Batch Processing:** Processes batches of prompts concurrently using a thread pool to maximize efficiency.
- **Answer Validation:** Ensures generated answers are relevant and meet a certain readability score using the Flesch-Kincaid grade.
- **Incremental Dataset Saving:** Saves generated data incrementally to prevent data loss.

### 2. `modeling_opux_gemini.py`
This script is designed to interface with the Google Gemini AI API for generating QA pairs. It includes functionality for configuring API keys, generating entries, and saving the output to a JSON file.

#### Key Features:
- **API Integration:** Securely integrates with the Google Gemini API for text generation.
- **Dynamic Question Generation:** Creates questions by randomly selecting from predefined keywords, job titles, and topics.
- **Configurable Output:** Allows setting parameters like temperature, top_p, and top_k to control the generation behavior.
- **Timestamping:** Each generated entry is timestamped for easy tracking.
- **Output in JSON:** Automatically formats and saves the generated QA pairs in a structured JSON file.

### 3. `modeling_opux_cpu.py`
This script is a CPU-optimized version of the `modeling_opux_gpu.py`. It uses the GPT-2 model from Hugging Face to generate QA pairs and is designed for environments where GPU is not available.

#### Key Features:
- **CPU Utilization:** Specifically configured to run on CPU to accommodate environments without GPU access.
- **Batch Processing:** Utilizes threading to efficiently process multiple prompts.
- **Validation and Logging:** Includes mechanisms to validate answers and log the progress.
- **Readability Scoring:** Implements a Flesch-Kincaid readability check to ensure generated answers meet readability standards.

## Installation

To set up the environment and install the required dependencies, follow the steps below:

### Prerequisites

- Python 3.8 or higher
- pip (Python package installer)
- A virtual environment is recommended

### Steps

1. Clone the repository:
```bash
   git clone https://github.com/your-username/modeling_opux.git
   cd modeling_opux
```

2. Create a virtual environment:

```bash
   python3 -m venv venv
   source venv/bin/activate  # On Windows use `venv\Scripts\activate`
```

3. Install the required dependencies:

```bash
pip install -r requirements.txt
Set up API keys (if using the Gemini script):
```

4. Create a .env file in the root directory.
Add your Google Gemini API key:
```bash
touch .env && nano .env
```
GEMINI_API_KEY=your_gemini_api_key

5. Running the GPU Script
To run the modeling_opux_gpu.py 
- **script:**
```bash
python modeling_opux_gpu.py
```
This script will generate QA pairs using a GPU if available. The output will be saved incrementally to avoid data loss.

6. Running the Gemini Script
To run the modeling_opux_gemini.py 
- **script:**
```bash
python modeling_opux_gemini.py
```
This script interacts with the Google Gemini API to generate QA pairs. Make sure your API key is correctly set in the .env file.

7. Running the CPU Script
To run the modeling_opux_cpu.py
- **script:**
```bash
python modeling_opux_cpu.py
```
This script will generate QA pairs on a CPU, making it suitable for environments without GPU access.

### 5. `Configuration`
Each script includes configurable parameters such as:
- **Temperature:**
Controls the randomness of predictions by scaling the logits before applying softmax.
- **Top_k and Top_p:**
These parameters control the diversity of the generated text.
- **Batch Size:**
Number of prompts processed simultaneously.
These can be adjusted directly in the script or by passing arguments when running the script.

### 6. `Output`
- **JSON Files:** 
The generated QA pairs are saved in JSON format. Each entry includes the question, answer, timestamp, and other metadata.
- **Logs:**
Detailed logs are generated during execution, capturing progress and any issues encountered.

### 7. `Logging`
Logging is implemented using Python’s built-in logging library. Logs include timestamps, severity levels, and messages to help in debugging and tracking script progress.

Log Levels: 
- **INFO, DEBUG, WARNING, ERROR**
Log Outputs: 
- **Console output and log files saved in the logs/ directory.**

# 3D-CIMlet

3D-CIMlet: A Chiplet Co-Design Framework for Heterogeneous In-Memory Acceleration of Edge LLM Inference and Continual Learning

<!-- ---

## Table of Contents

1. [Overview](#overview)
2. [Features](#features)
3. [Installation](#installation)
4. [Usage](#usage)
5. [Configuration](#configuration)
6. [Examples](#examples)
7. [Contributing](#contributing)
8. [License](#license) -->

---

## Overview

The 3D-CIMlet is a thermal-aware modeling and co-design framework for 2.5D/3D edge-LLM engines exploiting heterogeneous computing-in-memory (CIM) chiplets, adaptable for both inference and continual learning. The memory-reliability-aware chiplet mapping strategies was developed for a case study of edge LLM system integrating RRAM, capacitor-less eDRAM, and hybrid chiplets in mixed technology nodes. At the core of 3D-CIMlet's co-design capabilities are diverse embedded computational memories, in-memory compute-storage allocation strategies, NoP/NoC interplays with intra-chiplet designs, flexible model-to-architecture mapping space, and chiplet-to-package thermal analysis. These features, extending beyond the case study presented, will enable memory-reliability-aware and thermal-aware system designs for scalable and energy-efficient deployment of future LLM workloads at the edge and beyond.

This framework is currently under review and has been made available in this repository for evaluation purposes. It is intended for non-commercial use and will be further updated after the review process is completed. Detailed documentation and updates will follow in the future.

---

## Features

- Feature 1: We develop 3D-CIMlet, a modeling and co-design framework that allows rapid design space exploration of 2.5D/3D chiplet-based accelerator architectures for transformers, leveraging heterogeneous memory technologies.
- Feature 2: Based upon 3D-CIMlet, we develop a heterogeneous RRAM/eDRAM CIM system with 2.5D and 3D integration schemes and corresponding reliability-aware mapping strategies to support efficient inference and continual learning of edge LLMs.
- Feature 3: Through chiplet-to-package, multi-scale design space explorations (DSE), we provide co-optimization guidelines spanning CIM chiplet designs (intra-chiplet and inter-chiplet), cost-aware and thermal-aware system integration, and runtime optimizations for continual learning.

---

## Installation

### Prerequisites

- Python 3.8+

### Steps

1. Get the framework from GitHub:
   ```bash
   git clone https://anonymous.4open.science/r/3D-CIMlet
2. Go to the 3D-CIMlet folder, check the configuration in config.py and run main.py:
   ```bash
   cd 3D-CIMlet
   python3 main.py
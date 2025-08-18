# Overview
`vworkshop` is a templating application for vanilla web development. This `README` is a work in progress

# Installation
- Clone the repository to your system
  - `git clone https://github.com/scarletti-ben/vworkshop`
- Change directory into the cloned repository
  - `cd vworkshop`
- Create a virtual environment
  - `python -m venv .venv`
- Activate the virtual environment
  - `.venv\Scripts\activate`
- Install dependencies to the virtual environment
  - `pip install -r requirements.txt`
- Deactivate the virtual environment
  - `deactivate`
- Add `vworkshop` directory to your system `PATH`
  - POSTIT
- Test `vworkshop` (from anywhere) 
  - `vworkshop -h`

# Usage
For now usage can be inferred from the output of the `help` command, which can be seen below
```text
usage: vworkshop [-h] [-s] [-r] blueprint [target]

Create template folders from YAML blueprints

positional arguments:
  blueprint         Blueprint code ('001' => 'blueprint_001.yaml)
  target            Target directory name (optional)

options:
  -h, --help        show this help message and exit
  -s, --skip        skip all confirmations
  -r, --repository  include repository files
```

# Dependencies
The recommended dependencies for `vworkshop` are listed below
- **OS**: `Windows`
- **Shell**: `Command Prompt` or `PowerShell`
- **Python**: 
  - **Version**: 3.13+
  - **Packages**: 
    - `PyYAML`

# Project Metadata
```yaml
---
title: "Vanilla Workshop (vworkshop)"
date: "2025-08-18"
description: "Simple template generator for vanilla web development"
categories: [
  coding
]
tags: [
  webdev, html, javascript, css, python, batch
]
---
```
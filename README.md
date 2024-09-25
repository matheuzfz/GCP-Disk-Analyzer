# GCP-Disk-Analyzer
Ferramenta de automação em Python para analisar e gerar relatórios dos discos persistentes na Google Cloud Platform (GCP), fornecendo detalhes sobre o conteúdo dos arquivos e suas datas de última modificação. A ferramenta monta cada disco em uma VM, recupera metadados dos arquivos e desanexa os discos automaticamente após a análise.

# GCP Disk Content Analyzer

This repository contains a Python-based automation tool to analyze all persistent disks in a Google Cloud Platform (GCP) project. The tool mounts each disk to a temporary Virtual Machine (VM), retrieves the file names and their last modification dates, and generates a report for each disk. The tool can be extended to download or store these reports in a preferred location.

## Features
- **List all disks** in a GCP project.
- **Mount disks** to a VM for analysis.
- **Retrieve file contents** and **last modification dates** for all files on each disk.
- **Generate and download reports** with disk content details.
- Automatically **detach and unmount** the disks after analysis.

## Requirements
Before running this project, make sure you have the following:

1. **Python 3.x** installed.
2. **Google Cloud SDK** installed and configured on your machine.
3. A GCP account with permissions to access and manage disks, VMs, and API access.
4. The following Python packages:
    - `google-cloud-compute`

To install the required package:
```bash
pip install google-cloud-compute

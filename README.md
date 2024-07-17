
# Azure Resource Mover

Azure Resource Mover is a CLI tool for managing and moving Azure resources, with a focus on Function Apps.

## Installation

1. Clone the repository:
   ```
   git clone https://github.com/yourusername/Move-Function-App-SDK-.git
   cd Move-Function-App-SDK-
   ```

2. Set up a virtual environment (optional but recommended):
   ```
   python -m venv venv
   source venv/bin/activate  # On Windows use `venv\Scripts\activate`
   ```

3. Install the package:
   ```
   pip install -e .
   ```

## Configuration

1. Copy the `.env.example` file to `.env`:
   ```
   cp .env.example .env
   ```

2. Edit the `.env` file and fill in your Azure credentials and other required information.

## Usage

After installation, you can use the CLI tool by running:

```
armover
```

This will start the interactive CLI interface.

## Features

- Generate names for Azure resources (Function Apps, Resource Groups)
- Move Function Apps between subscriptions
- List Function Apps and Resource Groups

## Requirements

- Python 3.6+
- Azure CLI (must be installed separately)
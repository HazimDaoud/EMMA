# Software Folder
This folder contains the software-related components for the Fall Detection project.

## Setup

To set up the software components, follow these steps:

### Prerequisites

- Python 3.8

### Virtual Environment Setup (Optional)

It is recommended to use Miniconda for managing the Python environment. If you don't have Miniconda installed, you can download it from (https://docs.conda.io/projects/miniconda/en/latest/) and follow the installation instructions for your operating system.

Once Miniconda is installed, you can create a conda environment for this project. Navigate to the Software folder and run:

```bash

# Create a conda environment
conda env create -f requirements.txt -n fallDetectionEnv
# activate the conda environment
source activate fallDetectionEnv
# you can check that the conda environment was created athrough the command. The environment that has an asterisk next to it, is the active environment.
conda info --envs

```

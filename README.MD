

# Project Environment Setup Guide

This guide will walk you through setting up the necessary Conda environment to run this project.

### Prerequisites

You must have **Anaconda** or **Miniconda** installed on your system.

-----

### Step-by-Step Installation

Follow these steps in your terminal from the project's root directory.

**1. Create the Conda Environment**

This command creates a new Conda environment named `cdg.env312` inside this project folder, using Python 3.12.

```bash
conda create --prefix ./cdg.env312 python=3.12
```

*Using `--prefix ./` keeps the environment self-contained within the project.*

**2. Activate the Environment**

You must activate the environment to use it.

```bash
conda activate ./cdg.env312
```

*(You will need to do this every time you work on the project in a new terminal session.)*

**3. Install Jupyter Notebook**

Install the necessary packages for running notebooks.

```bash
conda install jupyter notebook
```

**4. Link the Environment to Jupyter**

This step creates a custom Jupyter kernel so you can select this specific environment within Jupyter Notebook. It will appear with the name "Python (GPU)".

```bash
python -m ipykernel install --user --name env312 --display-name "Python (GPU)"
```

**5. Set Required API Keys**

This project requires a Roboflow API key. The command below will save it as an environment variable specific to this Conda environment.

```bash
conda env config vars set ROBOFLOW_KEY=YOUR_API_KEY_HERE
```

**Important:**

  * Replace `YOUR_API_KEY_HERE` with your actual Roboflow key.
  * After setting the variable, you must deactivate and reactivate the environment for the change to take effect:
    ```bash
    conda deactivate
    conda activate ./cdg.env312
    ```

-----

### Alternative Setup (Using `environment.yml`)

If an `environment.yml` file is provided in the repository, you can perform the entire setup with a single command:

```bash
conda env create -f environment.yml
```

You will still need to activate the environment and set your API key (Steps 2 and 5 above).

-----

### Useful Commands

**List all Conda environments:**

```bash
conda env list
```

**Deactivate the current environment:**

```bash
conda deactivate
```

**Remove the environment completely:**

```bash
conda env remove --prefix ./cdg.env312
```
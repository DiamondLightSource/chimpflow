VERSION = $(shell soakdb3 --version)

# Shell to use instead of /bin/sh.
SHELL := /bin/bash

# Run all commands in the target in a single shell.
.ONESHELL:

# ------------------------------------------------------------------
# Install into conda.
# To keep /home/$(USER)/.conda/pkgs from being used (and filling up disk quota) do this:
#   conda config --add pkgs_dirs /scratch/kbp43231/conda/pkgs

CONDA_PUBLIC_PREFIX = /dls_sw/apps/xchem/conda/envs/xchem_chimpflow/$(VERSION)
CONDA_LOCAL_PREFIX = /scratch/$(USER)/conda/envs/xchem_chimpflow
PYTHON_VERSION = 3.9
CONDA_ACTIVATE = source $$(conda info --base)/etc/profile.d/conda.sh ; conda activate ; conda activate

# Create the conda environment for local development.
create_local_conda:
	rm -rf $(CONDA_LOCAL_PREFIX)
	module load mamba && \
	mamba create -y --prefix $(CONDA_LOCAL_PREFIX) python=$(PYTHON_VERSION)

# Install the packages into the conda environment.
provision_local_conda:
	$(CONDA_ACTIVATE) $(CONDA_LOCAL_PREFIX)
	mamba env update -f conda.yaml



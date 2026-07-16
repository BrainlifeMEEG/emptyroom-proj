"""
Compute empty-room SSP projectors.

This app loads an empty-room raw recording and computes SSP projectors
via mne.compute_proj_raw, saving the projector file and a topomap plot.

Inputs:
    - fif: Path to empty-room raw MEG/EEG data file
    - start, stop, duration: Time window parameters for projector estimation
    - n_grad, n_mag, n_eeg: Number of projection vectors per channel type
    - reject, flat: Optional rejection/flat channel thresholds
    - n_jobs: Number of parallel jobs
    - meg: MEG projector method

Outputs:
    - out_dir/proj.fif: Empty-room SSP projectors
    - out_figs/emptyroom_projectors.png: Projector topomap plot
    - product.json: Metadata about the computed projectors
"""

# Copyright (c) 2026 brainlife.io
#
# Authors: Guiomar Niso, Saeed Zahran

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'brainlife_utils'))

# Standard imports
import mne
import matplotlib.pyplot as plt

# Import shared utilities
from brainlife_utils import (
    load_config,
    setup_matplotlib_backend,
    ensure_output_dirs,
    create_product_json,
    add_info_to_product,
    add_image_to_product,
    require_config_keys
)

# Set up matplotlib for headless execution
setup_matplotlib_backend()

# Ensure output directories exist
ensure_output_dirs('out_dir', 'out_figs')

# Load configuration
config = load_config()
require_config_keys(config, ['fif'])

# == LOAD DATA ==
fname = config['fif']
raw = mne.io.read_raw(fname)

# == GET CONFIG VALUES ==
start = config['start']
stop = config['stop'] if config['stop'] else None
duration = config['duration']
n_grad = config['n_grad']
n_mag = config['n_mag']
n_eeg = config['n_eeg']
reject = config['reject'] if config['reject'] else None
flat = config['flat'] if config['flat'] else None
n_jobs = config['n_jobs']
meg = config['meg']
verbose = None

# == COMPUTE EMPTYROOM PROJECTOR ==
er_proj = mne.compute_proj_raw(raw, start, stop, duration, n_grad, n_mag, n_eeg, reject, flat, n_jobs, meg, verbose)

# == SAVE FILE ==
proj_path = os.path.join('out_dir', 'proj.fif')
mne.write_proj(proj_path, er_proj)

# == FIGURE ==
plt.figure(1)
fig_ep = mne.viz.plot_projs_topomap(er_proj, colorbar=True, vlim='joint', info=raw.info)
fig_path = os.path.join('out_figs', 'emptyroom_projectors.png')
fig_ep.savefig(fig_path)
plt.close(fig_ep)

# == CREATE PRODUCT.JSON ==
product_items = []
add_info_to_product(product_items, f'Computed {len(er_proj)} empty-room SSP projector(s)', 'success')
add_image_to_product(product_items, 'Empty-room projectors', filepath=fig_path)
create_product_json(product_items)

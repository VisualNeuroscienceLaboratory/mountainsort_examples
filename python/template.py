# standard imports
import os, sys, json
import numpy as np
from matplotlib import pyplot as plt

# mountainlab imports
from mountainlab_pytools import mlproc as mlp
from mountainlab_pytools import mdaio

def append_to_path(dir0): # A convenience function
  if dir0 not in sys.path:
    sys.path.append(dir0)

# imports from this repo
append_to_path('/home/stimulus/movshonMS4/python')
import mountainsort4_1_0 as ms4 # MountainSort spike sorting

def sort_file(dsdir, input_file, chan_range, outputdir=None, adj_radius=75, detect_thres=3, detect_int=30):

    #pipeline = mlp.mlproc_impl._MLPipeline();
    
    # output directory
    if outputdir is None:
      output_dir= dsdir # just set to input directory, unless you have a specific need otherwise

    #with pipeline:
    ms4.sort_dataset(dataset_dir=dsdir,output_dir=output_dir,input_file=input_file,adjacency_radius=adj_radius,detect_threshold=detect_thres,detect_interval=detect_int,chan_range=chan_range);

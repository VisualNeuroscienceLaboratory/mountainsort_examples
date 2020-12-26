# Spike soring neuropixel array data

## Requirements

For spike sorting you’ll just need a terminal window. For visualizing the output of the spike
sorting process you’ll need to use klingsor, farzana, or another mac (I’m working on setup
instructions for any mac). Just for now limit yourself to recordings where we did a channel map
of 1-384. I need to make more geom files to do the others (referenced below).

**Note that the git repository (on Arindal) is located at ~/movshonMS4.**

## Background:

For m676, we recorded activity using neuropixels arrays. The data is written out in two .bin files,
one for action potentials labeled ap and one for lfp. Multiple tests have suggested that it’s best
to sort subsets of files. I’ll take an example joint tuning experiment and walk through the steps.
For example, the files from m676 are stored on arindal at /experiments/m676_V1V2/recordings/

## Steps

1 . ssh into arindal, preferably as stimulus. Something like this will do
~~~~
ssh stimulus@arindal.cns.nyu.edu
cd /experiments/
~~~~
2 . Create a folder for relevant files. Say we wish to sort a joint tuning file
m676p3#11_dir24_sf14_g1_t0.imec.ap.bin (notice the AP). We need to create a place
where the raw output of this file along with its associated files will be stored. These need to
be stored in /experiments/ms4binaries/.
~~~~
mkdir /experiments/ms4binaries/m676/m676p3#11/
~~~~
3 . Copy the file, changing it to a .dat file. And shortening the naming convention
~~~~
cp /experiments/m676_V1V2/recordings/m676p3#11_dir24_sf14_g1_t0.imec.ap.bin /experiments/ms4binaries/m676/m676p3#11/m676p3#11.dat
~~~~
Next: Activate mountainlab.
As stimulus execute the following
~~~~
conda activate mlab
~~~~
4: Create a geom file.
~~~!
Note (from PL): there is analogous (perhaps updated) set of configuration files that are part of the core 
github repository (i.e. ~/movshonMS4/python/).
  
~~~~
5: Copy other configuration files to the folder from /experiments/ms4binaries/config_files
~~~~
cp /experiments/ms4binaries/config_files/params.json
/experiments/ms4binaries/m676/m676p3#11/
cp /experiments/ms4binaries/config_files/template.ipynb
/experiments/ms4binaries/m676/m676p3#11/
~~~~
6: Open the python pipeline. In the terminal window where mlab activated execute
~~~~
jupyter notebook --no-browser --port=8889
~~~~
In a second terminal window execute

~~~~
ssh -N -f -L localhost:8888:localhost:8889 stimulus@arindal.cns.nyu.edu
~~~~
Go to your browser and go to localhost:8888, a jupyter notebook will pop up  

7: 
* Set things up to look only in the folder you are storing things in. Set the channels you wish to analyze.
* Run the cells of the jupyter notebook.



8: If you are comfortable using Xquartz, then you need not transfer files to a computer with mountainview.
Instead, in an Xquartz terminal run the following
~~~~
ssh -X stimulus@arindal.cns.nyu.edu
~~~~
and navigate back to where you data is, and run the "qt-mountainview" command as below. On arindal, run
~~~~
conda activate mlab
~~~~
(future proof: run "conda info --envs" to get a list of all possible conda environments)

9b: After sorting is completed, transfer the files to a computer with mountainview and go
over results. Let's take klingsor as an example
~~~~
bash
conda activate mountainlab
~~~~
navigate to where the files are stored.
~~~~
qt-mountainview --raw=raw.mda --firings=firings.mda --samplerate=30000
~~~~
Note that you can also add the following flag to recover any manual curating previously done and saved (will be .json) -
~~~~
--cluster_metrics=[your_cluster_metrics.json]
~~~~


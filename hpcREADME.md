# Spike soring neuropixel array data on the NYU HPC

## Requirements/Setup

1. To run this on the NYU HPC, you will need an account. Talk to Paul or Manu, but this will require getting a faculty to approve you getting an HPC account. Once you have an account, you should be able to use the following pipeline.

2. For best results, adjust your ~/.ssh/config file (on your home machine) to include the following:
~~~~
## HPC/GREENE - as of early 2021, the HPC has decommissioned Prince in favor of Greene
Host greene
  HostName greene.hpc.nyu.edu
  User pl1465
  ForwardX11 yes
~~~~
This will allow you to simply 
~~~~
ssh greene
~~~~
from a terminal window to access the prince HPC; further, ForwardX11 will allow you to get any graphical interfaces on the cluster sent (i.e. forwarded) to your home machine. For details on X11, see [this guide](https://uisapp2.iu.edu/confluence-prd/pages/viewpage.action?pageId=280461906). _If_ you want to log in without any password, you'll need to either create or copy over a public key from your home/source machine to your login account on Greene. [See here for details](https://devwikis.nyu.edu/display/NYUHPC/Configuring+SSH+Key-Based+Authentication), but be sure that the [permissions](https://unix.stackexchange.com/questions/36540/why-am-i-still-getting-a-password-prompt-with-ssh-with-public-key-authentication) on the relevant Greene folders/files are properly set.

3. Previously on Prince, we had a shared work folder for the necessary Mountainsort files/environments. As of 21.03.19, we do not have this yet on Greene, so you will have to set up your own. To do so, first create a conda environment in your scratch folder as follows:
~~~~
module purge
module load anaconda3/2020.02
conda create -p /scratch/userID/ms_env/
~~~~

Then, you'll need to activate the environment to install the needed modules as follows. Despite the current HPC guide suggetsing the use of conda to install, this results in the files being installed in the home directory, rather than scratch - this means you'll exceed your file and/or storage quota. FIX TBD.

~~~
pip cache purge
~~~

4. The mountainsort_examples folder (within /beegfs/work/movshon/) is linked with [our git repository](https://github.com/VisualNeuroscienceLaboratory/mountainsort_examples), so this will be up-to-date with any changes we make. Once you go to this folder, you are ready to activate the mountainlab environment:
~~~~
cat prepareEnv.sh
~~~~
then copy/paste those commands into the command line. This conda environment is described in environment.yml.
As a test of the environment, the following command should list several mountainlab "processors" with example roots like ephys, ms3, ms4alg, spikeview:
~~~~
ml-list-processors
~~~~
If the above test worked, you are ready to use the mountainsort pipeline.

5. First, you'll need to have 

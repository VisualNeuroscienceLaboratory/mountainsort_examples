# Spike soring neuropixel array data on the NYU HPC

## Requirements/Setup

1. To run this on the NYU HPC, you will need an account. Talk to Paul or Manu, but this will require getting a faculty to approve you getting an HPC account. Once you have an account, you should be able to use the following pipeline.

2. For best results, adjust your ~/.ssh/config file (on your home machine) to include the following:
~~~~
## HPC/PRINCE
Host hpctunnel-gw
  HostName gw.hpc.nyu.edu
  ForwardX11 yes
  User yourHPCNAME
  #LocalForward 8026 prince.hpc.nyu.edu:22 

Host prince
  #Port 8026
  ForwardX11 yes
  User yourHPCNAME
  #ProxyCommand ssh -q hpctunnel-gw /usr/bin/nc prince 22
  Proxycommand ssh -aqW%h:22 hpctunnel-gw
~~~~
This will allow you to simply 
~~~~
ssh prince
~~~~
from a terminal window to access the prince HPC; further, ForwardX11 will allow you to get any graphical interfaces on the cluster sent (i.e. forwarded) to your home machine. For details on X11, see [https://uisapp2.iu.edu/confluence-prd/pages/viewpage.action?pageId=280461906](this guide).

3. Our shared folder for VNL/ is /beegfs/work/movshon/. We have a (mini)conda install here, as well as all necessary packages and mountainsort/lab dependencies. For your own ease, you can add the following line to your bash profile (~/.bash_profile) on the HPC:
~~~~
alias cdMov='cd /beegfs/work/movshon/'
~~~~

4. The mountainsort_examples folder (within /beegfs/work/movshon/) is linked with [our git repository](https://github.com/VisualNeuroscienceLaboratory/mountainsort_examples), so this will be up-to-date with any changes we make. Once you go to this folder, you are ready to activate the mountainlab environment:
~~~~
cat prepareEnv.sh
~~~~
then copy/paste those commands into the command line. This conda environment is described in environment.yml.

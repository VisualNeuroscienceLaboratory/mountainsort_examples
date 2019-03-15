# Spike soring neuropixel array data

## Requirements

For spike sorting you’ll just need a terminal window. For visualizing the output of the spike
sorting process you’ll need to use klingsor, farzana, or another mac (I’m working on setup
instructions for any mac). Just for now limit yourself to recordings where we did a channel map
of 1-384. I need to make more geom files to do the others (referenced below).

## Background:

For m676, we recorded activity using neuropixels arrays. The data is written out in two .bin files,
one for action potentials labeled ap and one for lfp. Multiple tests have suggested that it’s best
to sort subsets of files. I’ll take an example joint tuning experiment and walk through the steps.
The files from m676 are stored on arindal at /experiments/m676_V1V2/recordings/

## Steps

1 . ssh into arindal, preferably as stimulus. Something like this will do
ssh stimulus@arindal.cns.nyu.edu
cd /experiments/
2 . Create a folder for relevant files. Say we wish to sort a joint tuning file
m676p3#11_dir24_sf14_g1_t0.imec.ap.bin (notice the AP). We need to create a place
where the raw output of this file along with its associated files will be stored. These need to
be stored in /experiments/ms4binaries/.
mkdir /experiments/ms4binaries/m676/m676p3#11/
3 . Copy the file, changing it to a .dat file. And shortening the naming convention
cp /experiments/m676_V1V2/recordings/m676p3#11_dir24_sf14_g1_t0.imec.ap.bin
/experiments/ms4binaries/m676/m676p3#11/m676p3#11.dat
Step 3: Activate mountainlab.
As stimulus execute the following
conda activate mlab


Step 4: Convert array to .mda format used as input into mountainlab. The last argument is a
channels argument where you have to actually manually enter the 0 indexed channels you want
to sort from. It is an enormous pain in the ass. I am working on getting this automated. In this
example we are sorting channels 270-334 (remember channels start at 0!).
cd /experiments/ms4binaries/m676/m676p3#
ml-run-process ephys.convert_array --inputs input:m676p3#11.dat --outputs
output:raw.mda --parameters dtype:int16 dimensions:385,-
channels:270,271,272,273,274,275,276,277,278,279,280,281,282,283,284,285,286,
,288,289,290,291,292,293,294,295,296,297,298,299,300,301,302,303,304,305,306,307,
308,309,310,311,312,313,314,315,316,317,318,319,320,321,322,323,324,325,326,327,
328,329,330,331,332,333,
Step 5: Create a geom file. Okay this is a legitimate headache. In
/experiments/ms4binaries/config_files there is an .csv file called npx_1_384.csv.
For the channels you selected in step 4, copy those corresponding rows of the csv to a
new file entitled geom.csv and store it in /experiments/ms4binaries/m676/m676p3#11.
The file **must** be called geom.csv
Assuming you don't want to do this by hand or in matlab, you can run the following shell
function:
sed -n '{1st channel},{Nth channel}p' npx_1_384.csv > geom.csv. F
For example sticking to our example you would execute:
sed -n '271,335p' npx_1_384.csv > geom.csv
cp /experiments/ms4binaries/config_files/geom.csv
/experiments/ms4binaries/m676/m676p3#
Step 6: Copy other configuration files to the folder from /experiments/ms4binaries/config_files
cp /experiments/ms4binaries/config_files/params.json
/experiments/ms4binaries/m676/m676p3#11/
cp /experiments/ms4binaries/config_files/template.ipynb
/experiments/ms4binaries/m676/m676p3#11/
Step 7: Open the python pipeline. In the terminal window where mlab activated execute


jupyter notebook --no-browser --port=
In a second terminal window execute
ssh -N -f -L localhost:8888:localhost:8889 stimulus@arindal.cns.nyu.edu
Go to your browser and go to localhost:8888, a jupyter notebook will pop up
Step 8: Run the python pipeline
Set things up to look only in the folder you are storing things in.
Run the cells of the jupyter notebook.
Step 9: After sorting is completed, transfer the files to a computer with mountainview and go
over results. Let's take klingsor as an example
bash
conda activate mountainlab
navigate to where the files are stored.
qt-mountainview --raw=raw.mda --firings=firings.mda --samplerate=



from mountainlab_pytools import mdaio
from mountainlab_pytools import mlproc as mlp
import numpy as np
import os
import json
import warnings
import subprocess
import pdb

def sort_dataset(*,dataset_dir,output_dir,input_file,freq_min=300,freq_max=6000,adjacency_radius,detect_threshold,detect_interval,chan_range,geom_file='npx_1_384.csv',dtype='int16',n_chan=385,opts={},append_params=0):
    ''' From FlatironInstitute directly, but edits made by VNL
        suffix - added option which is added to base names (e.g. for the .mda (pre?) processing file so it isn't just "raw.mda"; instead raw[suffix].mda)
                   thus, we can have more than one saved file at a time (no overwrites with unique names)
        append_params: by default, leave the naming convention as is; but if =1, then append the adj radius (r), det. thresh. (t), and det. interval (i) to output names
    '''
    if not os.path.exists(output_dir):
        os.mkdir(output_dir)

    if len(chan_range) != 2:
      warnings.warn('Channel range should be [a,b], with a<b; defaulting to 100-130');
      chan_range = [100,129];
    suffix = '_%d_%d' % (chan_range[0], chan_range[1]);
    if append_params == 1:
        suffix = '%s_r%02d_t%02d_i%02d' % (suffix, adjacency_radius,detect_threshold,detect_interval)
    list_chans = lambda x: ",".join(map(str, np.arange(x[0], x[1]+1)))
    output_file = 'raw%s.mda' % suffix;
        
    # Dataset parameters
    ds_params=read_dataset_params(dataset_dir)
    shl_cmd = "sed -n '%d,%dp' %s > geom%s.csv" % (chan_range[0]+1, chan_range[1]+1, geom_file, suffix);
    
    curr_dir = os.getcwd();
    os.chdir(output_dir);
    subprocess.run(shl_cmd, shell=True);
    os.chdir(curr_dir);
    
    convert_array(
        dataset_dir=dataset_dir,
        input_file=input_file,
        channels=list_chans(chan_range),
        output_file=output_file,
        n_chan=n_chan,
        dtype=dtype,
        opts=opts
    )

    # Bandpass filter
    bandpass_filter(
        timeseries=dataset_dir+'/raw%s.mda' % suffix,
        timeseries_out=output_dir+'/filt%s.mda.prv' % suffix,
        samplerate=ds_params['samplerate'],
        freq_min=freq_min,
        freq_max=freq_max,
        opts=opts
    )
    
    # Whiten
    whiten(
        timeseries=output_dir+'/filt%s.mda.prv' % suffix,
        timeseries_out=output_dir+'/pre%s.mda.prv' % suffix,
        opts=opts
    )
    
    # Sort
    detect_sign=1
    if 'spike_sign' in ds_params:
        detect_sign=ds_params['spike_sign']
    if 'detect_sign' in ds_params:
        detect_sign=ds_params['detect_sign']
    ms4alg_sort(
        
        timeseries=output_dir+'/pre%s.mda.prv' % suffix,
        geom=dataset_dir+'/geom%s.csv' % suffix,
        firings_out=output_dir+'/firings_uncurated%s.mda' % suffix,
        adjacency_radius=adjacency_radius,
        detect_sign=detect_sign,
        detect_threshold=detect_threshold,
	detect_interval=detect_interval,
        opts=opts
    )
    
    # Compute cluster metrics
    compute_cluster_metrics(
        timeseries=output_dir+'/pre%s.mda.prv' % suffix,
        firings=output_dir+'/firings_uncurated%s.mda' % suffix,
        metrics_out=output_dir+'/cluster_metrics%s.json' % suffix,
        samplerate=ds_params['samplerate'],
        opts=opts
    )
    
    # Automated curation
    automated_curation(
        firings=output_dir+'/firings_uncurated%s.mda' % suffix,
        cluster_metrics=output_dir+'/cluster_metrics%s.json' % suffix,
        firings_out=output_dir+'/firings%s.mda' % suffix,
        opts=opts
    )
    
def read_dataset_params(dsdir):
    params_fname=mlp.realizeFile(dsdir+'/params.json')
    if not os.path.exists(params_fname):
        raise Exception('Dataset parameter file does not exist: '+params_fname)
    with open(params_fname) as f:
        return json.load(f)
    
def bandpass_filter(*,timeseries,timeseries_out,samplerate,freq_min,freq_max,opts={}):
    return mlp.addProcess(
        'ephys.bandpass_filter',
        {
            'timeseries':timeseries
        },{
            'timeseries_out':timeseries_out
        },
        {
            'samplerate':samplerate,
            'freq_min':freq_min,
            'freq_max':freq_max
        },
        opts
    )

def convert_array(*,dataset_dir,input_file,channels,output_file,n_chan,dtype,opts):
    return mlp.addProcess(
        'ephys.convert_array',
        {
            'input':dataset_dir+'/'+input_file
        },{
            'output':dataset_dir+'/'+output_file
        },{
            'dtype':dtype,
            'dimensions':'%d,-1' % n_chan,
            'channels':channels
        },
        opts
    )

def whiten(*,timeseries,timeseries_out,opts={}):
    return mlp.addProcess(
        'ephys.whiten',
        {
            'timeseries':timeseries
        },
        {
            'timeseries_out':timeseries_out
        },
        {},
        opts
    )

def ms4alg_sort(*,timeseries,geom,firings_out,detect_sign,adjacency_radius,detect_threshold=3,detect_interval,opts={}):
    pp={}
    pp['detect_sign']=detect_sign
    pp['adjacency_radius']=adjacency_radius
    pp['detect_threshold']=detect_threshold
    pp['detect_interval']=detect_interval
    mlp.addProcess(
        'ms4alg.sort',
        {
            'timeseries':timeseries,
            'geom':geom
        },
        {
            'firings_out':firings_out
        },
        pp,
        opts
    )
    
def compute_cluster_metrics(*,timeseries,firings,metrics_out,samplerate,opts={}):
    metrics1=mlp.addProcess(
        'ms3.cluster_metrics',
        {
            'timeseries':timeseries,
            'firings':firings
        },
        {
            'cluster_metrics_out':True
        },
        {
            'samplerate':samplerate
        },
        opts
    )['outputs']['cluster_metrics_out']
    metrics2=mlp.addProcess(
        'ms3.isolation_metrics',
        {
            'timeseries':timeseries,
            'firings':firings
        },
        {
            'metrics_out':True
        },
        {
            'compute_bursting_parents':'true'
        },
        opts
    )['outputs']['metrics_out']
    return mlp.addProcess(
        'ms3.combine_cluster_metrics',
        {
            'metrics_list':[metrics1,metrics2]
        },
        {
            'metrics_out':metrics_out
        },
        {},
        opts
    )

def automated_curation(*,firings,cluster_metrics,firings_out,opts={}):
    # Automated curation
    label_map=mlp.addProcess(
        'ms4alg.create_label_map',
        {
            'metrics':cluster_metrics
        },
        {
            'label_map_out':True
        },
        {},
        opts
    )['outputs']['label_map_out']
    return mlp.addProcess(
        'ms4alg.apply_label_map',
        {
            'label_map':label_map,
            'firings':firings
        },
        {
            'firings_out':firings_out
        },
        {},
        opts
    )

def synthesize_sample_dataset(*,dataset_dir,samplerate=30000,duration=600,num_channels=4,suffix='',opts={}):
    if not os.path.exists(dataset_dir):
        os.mkdir(dataset_dir)
    M=num_channels
    mlp.addProcess(
        'ephys.synthesize_random_waveforms',
        {},
        {
            'geometry_out':dataset_dir+'/geom%s.csv' % suffix,
            'waveforms_out':dataset_dir+'/waveforms_true%s.mda' % suffix
        },
        {
            'upsamplefac':13,
            'M':M,
            'average_peak_amplitude':100
        },
        opts
    )
    mlp.addProcess(
        'ephys.synthesize_random_firings',
        {},
        {
            'firings_out':dataset_dir+'/firings_true%s.mda' % suffix
        },
        {
            'duration':duration
        },
        opts
    )
    mlp.addProcess(
        'ephys.synthesize_timeseries',
        {
            'firings':dataset_dir+'/firings_true%s.mda' % suffix,
            'waveforms':dataset_dir+'/waveforms_true%s.mda' % suffix
        },
        {
            'timeseries_out':dataset_dir+'/raw%s.mda.prv' % suffix
        },{
            'duration':duration,
            'waveform_upsamplefac':13,
            'noise_level':10
        },
        opts
    )
    params={
        'samplerate':samplerate,
        'spike_sign':1
    }
    with open(dataset_dir+'/params.json', 'w') as outfile:
        json.dump(params, outfile, indent=4)

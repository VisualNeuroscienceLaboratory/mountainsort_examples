from mountainlab_pytools import mdaio
from mountainlab_pytools import mlproc as mlp
import os
import json

def sort_dataset(*,dataset_dir,output_dir,freq_min=300,freq_max=6000,adjacency_radius,detect_threshold,detect_interval,suffix='',opts={}):
    ''' From FlatironInstitute directly, but edits made by VNL
        suffix - added option which is added to base names (e.g. for the .mda (pre?) processing file so it isn't just "raw.mda"; instead raw[suffix].mda)
                   thus, we can have more than one saved file at a time (no overwrites with unique names)
    '''
    if not os.path.exists(output_dir):
        os.mkdir(output_dir)
        
    # Dataset parameters
    ds_params=read_dataset_params(dataset_dir)
    
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

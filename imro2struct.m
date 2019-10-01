function dataOUT = imro2struct(imroFilename)
% dataOUT = imro2struct(imroFilename) packages .imro file for Neuropixels 
%   channel switching using SpikeGLX
%
% Output is a structure with three fields:
% probeinfo: header containing probe number, ??, and number of channels
% chaninfo: (num channels)x5 matrix, with columns corresponding to channel
%   number, bank number, reference ID, gain factor, and spike band high 
%   pass cutoff
% sitenums: electrode/site numbers (effectively a channel map), where
%   (site number) = (channel+1) + bank*384
% 
% see also SpikeGLX UserManual


imro = importdata(imroFilename);
imro = strsplit(imro{1},')');

probeinfo = cellfun(@str2num,strsplit(imro{1}(2:end),','),'UniformOutput',false);
dataOUT.probeinfo = cat(2,probeinfo{:});

chaninfo = cellfun(@str2num,cellfun(@(x) x(2:end),imro(2:end-1),'UniformOutput',false),'UniformOutput',false);
dataOUT.chaninfo = cat(1,chaninfo{:});

dataOUT.sitenums = dataOUT.chaninfo(:,1)+1+dataOUT.chaninfo(:,2)*384;
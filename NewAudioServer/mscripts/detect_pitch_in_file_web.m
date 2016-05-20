function rfname=detect_pitch_in_file_web(fname,P)

addpath('~/ResearchMIT/CBMM/CMMMproj/PITCH/voicebox');
addpath('~/ResearchMIT/CBMM/CMMMproj/PITCH/yin');


addpath('~/ResearchMIT/toolboxes/jsonlab');
addpath('~/ResearchMIT/CBMM/CMMMproj/PITCH/')
addpath('~/ResearchMIT/toolboxes/Sound_Texture_Synthesis_Toolbox/');
addpath('~/ResearchMIT/toolboxes/SYNTH/');
addpath('~/ResearchMIT/toolboxes/create_tap_stim/');
addpath ('~/ResearchMIT/CBMM/CMMMproj/VSQR')


[myaudio,fs]=audioread(fname);

ISPLOT=false;
[fq,midi,start_stop]=detect_pitch_nori(myaudio,fs,ISPLOT);

if isfield(P,'donefilename')
    rfname=sprintf('res/%s',P.donefilename);
else
    rfname=sprintf('res/%s.mresults.json',fname);
end

fprintf('results of analysis:\n');
for I=1:length(fq)
    fprintf('note %2d\t\tfq= %4.1f\tmidi=%3.2f\tstart=%3.3f\tstop=%3.3f\n',I,fq(I),midi(I),start_stop(I,1),start_stop(I,2));
end

fprintf('saving pitch info to file: %s\n',rfname)
FID=fopen(rfname,'w');
P.fqs=fq;
P.midis=midi;
P.starts=start_stop(:,1);
P.stops=start_stop(:,2);
json=savejson('',P);
fprintf(FID,'%s\n',json);
fclose(FID);
fprintf('saving pitch to file: %s\n',rfname)


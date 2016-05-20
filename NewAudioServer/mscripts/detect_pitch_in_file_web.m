function rfname=detect_pitch_in_file_web(fname,P)

addpath('~/ResearchMIT/CBMM/CMMMproj/PITCH/voicebox');
addpath('~/ResearchMIT/CBMM/CMMMproj/PITCH/yin');


addpath('~/ResearchMIT/toolboxes/jsonlab');
addpath('~/ResearchMIT/CBMM/CMMMproj/PITCH/')
addpath('~/ResearchMIT/toolboxes/Sound_Texture_Synthesis_Toolbox/');
addpath('~/ResearchMIT/toolboxes/SYNTH/');
addpath('~/ResearchMIT/toolboxes/create_tap_stim/');
addpath ('~/ResearchMIT/CBMM/CMMMproj/VSQR')

fprintf('audio read...\n');
[myaudio,fs]=audioread(fname);

fprintf('audio : %3.3f sec\n trying to detect pitch\n',max(size(myaudio))/fs);

ISPLOT=false;
[fq,midi,start_stop]=detect_pitch_nori_yinonly(myaudio,fs,ISPLOT);

fprintf('done extracting pitch, pitch1 : %3.3f sec\n',fq(1));

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
P
P.fqs=fq;
P.midis=midi;
P.starts=start_stop(:,1);
P.stops=start_stop(:,2);
json=savejson('',P);
fprintf('json:%s\n',json);
fprintf(FID,'%s\n',json);
fclose(FID);
fprintf('saving pitch to file: %s\n',rfname)


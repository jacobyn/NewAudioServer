function rfname=pitch_stim_create(fname,P)

%%fname='temp.ogg';P=[];P.midi=48;P.duration=4;pitch_stim_create(fname,P)


if isfield(P,'donefilename')
    rfname=P.donefilename;
else
    if length(fname)>3 && (strfind(fname((end-3):(end)),'ogg')<1)
        rfname=sprintf('%s.ogg',fname);
    else
        rfname=sprintf('%s',fname);
    end
end

fprintf('trying to analyze pitch with filename: %s',rfname);

addpath('~/ResearchMIT/CBMM/CMMMproj/PITCH/')
addpath('~/ResearchMIT/toolboxes/Sound_Texture_Synthesis_Toolbox/');
addpath('~/ResearchMIT/toolboxes/SYNTH/');
addpath('~/ResearchMIT/toolboxes/create_tap_stim/');
addpath ('~/ResearchMIT/CBMM/CMMMproj/VSQR')

midi=P.midi;
duration=P.duration;
fs=44100; % sampling rate

P.atk=10;P.dec=10;
SYNTH=@SYNTH_make_note_pure;
Ps=P;

begsilence=0.1; 


CLICKS=1;%%%%midi=48;
midiS=ones(1,CLICKS)*midi;
[out1,~]=SYNTH_simple2sound(midiS,500,120,500,1,Ps,SYNTH,fs);
out=zeros(round(duration*fs),1);
out(1:length(out1))=out1;
out=[zeros(round(fs*begsilence),1);out];
fprintf('saving stim info to file: %s\n',rfname)
audiowrite(rfname,out,fs);
fprintf('saving stim to file: %s (SUCESS!)\n',rfname)

end

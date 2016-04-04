%%% nohup matlab -nodisplay -nodesktop -nosplash /r "fname=''BBB-MatlabAnal-fileToUpload5748-rnd-5107.wav''AudioInfo()"  >&  FILENAME.m.out &

%%% nohup matlab -nodisplay -nodesktop -nosplash -r "fname= 'uploads/BBB-MatlabAnal-fileToUpload5748-rnd-5107.wav'; AudioInfo(); exit" > temp.out

%%% matlab /r myscript
%%% fname= 'uploads/BBB-MatlabAnal-fileToUpload5748-rnd-5107.wav'
[y,fs]=audioread(fname);
fprintf('fs=%d and length=%g fname= %s\n',fs,max(size(y)),fname);


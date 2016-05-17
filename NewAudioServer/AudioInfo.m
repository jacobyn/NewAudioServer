function tfname=AudioInfo(ofname)
%%% nohup matlab -nodisplay -nodesktop -nosplash /r "fname=''BBB-MatlabAnal-fileToUpload5748-rnd-5107.wav''AudioInfo()"  >&  FILENAME.m.out &
%%% nohup matlab -nodisplay -nodesktop -nosplash -nojvm -r "AudioInfo('uploads/BBB-MatlabAnal-fileToUpload5748-rnd-5107.wav'); exit" > temp.out
%%% matlab /r myscript
%%% -nojvm -nodisplay
%%% fname= 'uploads/BBB-MatlabAnal-fileToUpload5748-rnd-5107.wav'
%%% /Applications/MATLAB_R2014b.app/bin/matlab -nodisplay -nodesktop -nosplash -nojvm -r "AudioInfo('uploads/BBB-4045-MatlabAnal-fileToUpload8027-rnd-4203.wav'); exit"
%%IN THE END:
%%%%matlab -nodisplay -nojvm -r "unix('DYLD_LIBRARY_PATH="";curl http://127.0.0.1:5000/blah');exit"

[y,fs]=audioread(ofname);
tfname=sprintf('%s.%d.mat',ofname,fs);
save(tfname,'fs')
fprintf('fs=%d and length=%g ofname= %s tfname=%s\n',fs,max(size(y)),ofname,tfname);

return 


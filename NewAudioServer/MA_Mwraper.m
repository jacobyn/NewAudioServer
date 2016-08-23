%%%%%%%
%%% This function wraps a matlab script, it sits on the audio server, read
%%% json param file (pfile) and parse it. It run the deisgnated command
%%% (mscript) and ping the done route (return_route) creats temporary files
%%% and also a done file (with parameters) using (donefilename).
%%%%%%
function MA_Mwraper(pfile)

addpath([pwd,'/mscripts']);
addpath('/var/www/NewAudioServer/NewAudioServer/mscripts')

fprintf('MWrap: reading basic params...\n');

%pfilename= 'MA1.session.7588.file.6308.todo.json' % en example of done
%file
par_fname_o=sprintf('res/%s',pfile); % get parameter file

par_text = fileread(par_fname_o); % parse this json file
par_content=parse_json(par_text);
par_content=par_content{1};
P=par_content; % write as struct

fprintf('MWrap: rreading json...\n');
% get internal params from struct
rfname=P.rfilename;
rec_fname=sprintf('res/%s',rfname); %recording filename
pfname=P.pfilename;
par_fname=sprintf('res/%s',pfname); %parameter file
session_id=P.session_id; %session id
file_id=P.file_id;
return_route=P.return_route; % this is the return route (to ping when done)
mscript=P.mscript;

donefilename=sprintf('res/%s',P.donefilename);  %done filename for output.

is_sucess=false; % life is hard...

fprintf('MWrap: security check...\n');
%make sure (security) that there is a script of this sort here
script=sprintf('mscripts/%s.m',mscript);
temp=dir(script);
assert(length(temp)==1)

fprintf('MWrap: run command...\n');
% create command
cmd=sprintf('%s (''%s'', P)', mscript,rec_fname);
fprintf('MWrap: trying to run command: %s\n',cmd)
try
    ofname=eval(cmd); % output (response analyzed) filename (this is where the analysis data can be found)
    is_sucess=true;
    fprintf('MWrap: tried and it worked!');
catch ME
    is_sucess=false;
    ofname=pfile;
    msgText = getReport(ME);
    fprintf('MWrap: ERORR(NORI):%s\n',msgText);
end

% fprintf('MWrap: ping final route...\n');
% cmsg='/usr/bin/curl';
% if ismac
%     cmsg='curl';
% end
% rcmd=sprintf('DYLD_LIBRARY_PATH=\"\";%s %s%d/%s', cmsg,return_route,is_sucess,pfname);
% unix(rcmd)

%% do not ping return route
%wcmd=sprintf('%s/%d/%s',return_route,is_sucess,pfile); %return filename of parameters not of anlyzed data since the output file do exist in the data
%webread(wcmd)



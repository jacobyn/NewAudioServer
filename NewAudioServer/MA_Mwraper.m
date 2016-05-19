function MA_Mwraper(pfile)
%clc
%pfilename= 'MA1.session.7588.file.6308.todo.json'
par_fname_o=sprintf('res/%s',pfile);


par_text = fileread(par_fname_o);
par_content=parse_json(par_text);
par_content=par_content{1};
P=par_content;

rfname=P.rfilename;
rec_fname=sprintf('res/%s',rfname);
pfname=P.pfilename;
par_fname=sprintf('res/%s',pfname);
session_id=P.session_id;
file_id=P.file_id;
return_route=P.return_route;
mscript=P.mscript;

is_sucess=false;



%make sure (security) that there is a script of this sort here
script=sprintf('%s.m',mscript);
temp=dir(script);
assert(length(temp)==1)

% create command
cmd=sprintf('%s (''%s'')', mscript,rec_fname);
try 
    rfname=eval(cmd)
    is_sucess=true;
    
catch 
    is_sucess=false;
    msgText = getReport(ME);
    fprintf('ERORR(NORI):%s\n',msgText);
end

cmsg='/usr/bin/curl';
if ismac
    cmsg='curl';
end

rcmd=sprintf('DYLD_LIBRARY_PATH=\"\";%s %s%d/%s', cmsg,return_route,is_sucess,pfname);
unix(rcmd)



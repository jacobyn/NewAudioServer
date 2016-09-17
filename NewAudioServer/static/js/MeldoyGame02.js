// Java script for audio client
//constants
var burl="http://audio.norijacoby.com/res/"
var audio_url="http://audio.norijacoby.com/notset"
//more
var TIME_RECORD_BEFORE_PLAY=200
var TIME_RECORD_AFTER_PLAY=4000
var TIME_BEFORE_STIM_AVILABLE=8000
var TIME_INSTRUCT = 1000
var TIME_START_RESULT=1000
var TIME_REFRESH_RESULT=3000
var audio_context;
var recorder;
var my_node_id=9998
var LOWER_MIDI_NOTE=undefined
var HIGHER_MIDI_NOTE=undefined
var MIDI_NOTE=60;
var err_time=0;
var durl="";
var params;
var experiments;
var current_experiment = 0;
var current_status_experiment = 'NOT FINISHED'
var current_status_all = 'NOT FINISHED'
var is_still_trying_to_load= true;
var current_trial = 0;
var current_trial_index;
var current_url
var temp_jsn



var participant_id="particip-1"


var vid = document.getElementById("audioPlayer");
vid.controls = false;
var myaudio = document.getElementById("audioPlayer");

AUDIOfileName= ''

function print_progress_message() {
  msg1= "Experiment " + (current_experiment+1) + " of " + (experiments.length)
  msg2= "Trial " + (current_trial+1) + " of " + experiments[current_experiment].total_trials

  msg3= "<br><br> For debug: <br>-------------------------------------------"
  msg4= "Permutation position: " + current_trial_index
  msg5= "current_status_experiment:" + current_status_experiment
  msg6= "current_status_all:" + current_status_all

  msg7= "Current melody (stimulus) file: " + current_url
  msg8= "Result url (probably last and not current):" + durl

  msg_d= "<br>" + msg3 + "<br>" + msg4 + "<br>" + msg5 + "<br>"+ msg6 + "<br>"+ msg7 + "<br>" + msg8 + "<br>"
  msg= msg1 + "<br>" + msg2;
  document.getElementById("trial_info").innerHTML=msg;
  document.getElementById("trial_info").style.visibility='visible'
  document.getElementById("debug").innerHTML=msg_d;

  return msg

}

function trials_init() {
        current_experiment = 0;
        current_trial = 0;
        current_trial_index = experiments[current_experiment].perm[current_trial];
        current_url=get_new_stimulus_url();
        current_status_experiment = 'NOT FINISHED';
        current_status_all = 'NOT FINISHED';
        is_still_trying_to_load = true;
        document.getElementById("experiment_title").innerHTML=experiments[current_experiment].name;
        document.getElementById("general_instruct").innerHTML=experiments[current_experiment].description;

}

function trials_next() {
        //current_experiment = 0;

        current_trial++;
        if ((current_trial>= experiments[current_experiment].N_maxtrials) | (current_trial>= experiments[current_experiment].stim_list.length)) {
          current_status_experiment = 'FINISHED';
          current_experiment++;
          current_trial=0;
        } else {
          current_status_experiment = 'NOT FINISHED';
        }
        if (current_experiment>=experiments.length) {
          current_status_all = 'FINISHED';
          document.getElementById("the_action").disabled = true;
        } else {
          current_trial_index = experiments[current_experiment].perm[current_trial];
          current_url=get_new_stimulus_url();
        }
        if (current_status_all === 'NOT FINISHED'){
          document.getElementById("experiment_title").innerHTML=experiments[current_experiment].name;
          document.getElementById("general_instruct").innerHTML=experiments[current_experiment].description;
        }

        if (current_status_all==="FINISHED") {
            show_results();
        }

        if ((current_status_experiment==="FINISHED") & (!(current_status_all==="FINISHED"))) {
            document.getElementById('experiment').style.visibility='hidden'
           document.getElementById('experiment_end').style.visibility='visible'
           document.getElementById("trial_info").style.visibility='hidden'
           document.getElementById("instruct").innerHTML=""

         }

}


function get_params() {
   reqwest ({
    // /get_trial_params/<int:node_id>/<int:participant_id>", methods=["GET"])
     url: '/get_params/' + participant_id  ,
     method: 'get',
     type: 'json',
    success: function (resp) {
        params=resp;
        console.log('I got global parameters');
        experiments=params.experiments;

        // randomize order of the experiments
        for (e=0;e<experiments.length;e++) {
          n = experiments[e].stim_list.length;
          experiments[e].perm = make_perm(n);
          experiments[e].results = new Array(n);
          experiments[e].total_trials=Math.min(experiments[e].stim_list.length,experiments[e].N_maxtrials);
          for (i=0;i<n;i++) {
            experiments[e].results[i]={};
          }
        }

        trials_init();




      },
      error: function (err) {
        console.log(err);

    }
});
}

function getRandomInt (mmin, mmax) {
    return Math.floor(Math.random() * (mmax - mmin + 1)) + mmin;
}

function restart_game() {
  document.getElementById("results").innerHTML="";
  document.getElementById("log").innerHTML="";
  document.getElementById("the_action").innerHTML="preparing..."
  document.getElementById("the_action").disabled = true;
  document.getElementById("the_restart").innerHTML="Restart"

  pitch_create_stimulus();

}

function change_range() {
  document.getElementById("the_action").disabled = true;
  document.getElementById("the_action").innerHTML="not ready"
  document.getElementById("the_restart").innerHTML="Please restart"
  document.getElementById("the_restart").disabled = false;
  clearTimeout(err_time);
}

function pitch_create_stimulus() {
  LOWER_MIDI_NOTE=parseInt(document.getElementById("LowerMidiNote").value);
  HIGHER_MIDI_NOTE=parseInt(document.getElementById("HigherMidiNote").value);
  MIDI_NOTE=getRandomInt (LOWER_MIDI_NOTE, HIGHER_MIDI_NOTE);
  document.getElementById("the_action").disabled = true;
  document.getElementById("the_restart").innerHTML="Restart"


  console.log('preparing stimulus (this will take a few seconds)...');

    console.log ("trying to create stimulus...");
    midi= MIDI_NOTE
    console.log(midi)
      reqwest ({
       url: "/createpitch/" + midi ,
       method: 'get',
       type: 'json',
    success: function (resp) {
        console.log("got response that seems ok")

        //document.getElementById("res").innerHTML= JSON.stringify(resp);
        afile=resp.donefilename;

        audio_url=burl+afile
        console.log("audio url:" + audio_url)

        err_time=setTimeout(function(){
            document.getElementById("the_action").disabled = false;
            document.getElementById("the_action").innerHTML = "Play the tone!";
            console.log ("trying to make record avilable");
            console.log("stimulus is ready to play");
          },TIME_BEFORE_STIM_AVILABLE
        );

    },
     error: function (err) {
         console.log(err);
    }
});
}



function getAudioFileName_andPlayRecordUpload() {
 print_progress_message();
 recorder.clear()
 myaudio.src=current_url
 console.log('Stimulus filename:' + current_url);
 console.log('setting up wait for audio to load...');
 myaudio.oncanplay=function () {
          console.log("can play! so starting...");

          do_play_record_upload_audio()
        }
 myaudio.load()

}

function get_new_stimulus_url() {
    perm=experiments[current_experiment].perm;
    url=experiments[current_experiment].stim_list[perm[current_trial]];

    current_url=url;
    return url
}

function compute_note_mod_accuracy(target,source) {
  mymin=999999;
  myo=99999;
  for (o=-2;o<=2;o++) {
    acc=Math.abs(target-(source-12*o))
    if (acc<mymin) {
      myo=o;
      acc=Math.round(acc*100.0)/100.0;
      mymin=acc;

    }
  }
  mresp={};
  mresp.acc=mymin;
  mresp.octave=myo;
  return mresp
}

function run_compute_results() {
  // envoke all the results if they exists
  is_still_trying_to_load= false;

          for (e=0; e<experiments.length;e++){
            for (t=0;t<experiments[e].results.length;t++) {
              murl=experiments[e].results[t].res_url;
                if (murl) {
                  if (!(experiments[e].results[t].result)) {
                    console.log('....................Trying to load e= '+ e + " t= "+ t)
                     get_result_url_and_save (e,t);
                     is_still_trying_to_load=true;
                   }
                }

            }
          }
}

function show_results_message() {
          run_compute_results();
          console.log('Show results_message...')
          msg=''; total_acc=0;cnt_acc=0;

          if (is_still_trying_to_load) {
            msg = msg + '<br>Analysis make take up to 20 secs:<br><br>'
            msg = msg + '<button type="button" id="show_results_action"    onClick="show_results_message();"> Refresh results...</button> <br>'
          }  else {
            msg = 'Finished analyzing: <br>'
          }


          for (e=0; e<experiments.length;e++){
              for (t=0;t<experiments[e].results.length;t++) {
                  msg=msg+ "<br>";
                  true_t =experiments[e].results[t].trial_order;
                  msg= msg + "Experiment " + (e+1) + " [ "+ experiments[e].name + " ] trial " + (t+1) + " " ;
                  msg= msg + " True-order: " + (true_t+1) + " ";
                  murl=experiments[e].results[t].res_url;
                  if (murl) {
                      mresp=experiments[e].results[t].result;
                      if (mresp) {
                        num_notes=experiments[e].results[t].result.midis.length;
                        msg=msg +  "|| num_notes = " + num_notes +" midi notes = ["

                          for (n=0;n<=num_notes -2 ; n++) {
                            note=experiments[e].results[t].result.midis[n][0];
                            note=Math.round(note*100.0)/100.0;
                            last_note=note;
                            if (n>0) {
                              msg=msg+ ", ";
                            }
                              msg=msg+ String(note);
                          }
                          msg=msg+ "]   ";
                          n=num_notes-1;
                          note=experiments[e].results[t].result.midis[n][0];
                          note=Math.round(note*100.0)/100.0;
                          msg=msg+ "last note: " + note
                          if ((num_notes-1)==experiments[e].num_notes[t])  {
                            msg= msg + " <font color='green'> OK </font> "
                          } else {
                            msg= msg + " WRONG NUMBER OF NOTES (reminder: do not use headphones)"
                          }

                          if (num_notes==2) {
                            best_match=compute_note_mod_accuracy(last_note,note);

                            acc=Math.round(Math.round(best_match.acc*100.0));
                            octave=best_match.octave;
                            total_acc=total_acc+acc;
                            cnt_acc++;
                            msg= msg + "accuracy(cents): " + acc + " octave shifts: " + octave;
                          }

                         // if experiments[e]

                        //String(experiments[e].results[t].result.midis);
                      }
                      else {
                        msg= msg+ "url:" + murl + " <font color='red'> (analyzing...) </font>"
                      }
                  } else {
                       msg= msg+ "Did not run"
                  }
               }
          }
          msg=msg + "<br> Average accuracy (cents) [for experiment 1 only]: " + Math.round(1.0*total_acc/cnt_acc);
          document.getElementById("results").innerHTML= msg;
          return msg
}
function show_results() {
        document.getElementById("experiment").style.visibility = "hidden";
        document.getElementById("results").style.visibility = "visible";
        //document.getElementById("show_results_action").innerHTML  ="Refresh results";
        document.getElementById("results").innerHTML= "<font color='red'> Loading results... </font>";
        run_compute_results();

        result_timer = setTimeout(function(){
          show_results_message()
        },TIME_START_RESULT);

        for (i=2;i<=10;i++) {
          setTimeout(function(){

          show_results_message();
          },TIME_REFRESH_RESULT*i + TIME_START_RESULT );
        }
}

function do_play_record_upload_audio() {

  document.getElementById("the_action").disabled = true;
  document.getElementById("instruct").innerHTML="<p align='center'>Playing...<\p>"
  console.log('start recording...');
  recorder && recorder.record();
  setTimeout( function(){
    console.log('start playing...');
    myaudio.onloaddata="";
    myaudio.play();
    myaudio.onended = function () {
      console.log("...end playing...");

      msg="<p align='center'>"+ params.experiments[current_experiment].trial_messages[0] +  "<\p>"
      document.getElementById("instruct").innerHTML=msg
      //"<p align='center'> Sing the note you think comes next! <\p>"

      setTimeout( function(){
       console.log("...end of stimulus recording");
       recorder.stop()
       console.log("...stop recording...");
       msg="<p align='center'>"+ params.experiments[current_experiment].trial_messages[1] +  "<\p>"
       document.getElementById("instruct").innerHTML=msg
         upload_audio();
        }, TIME_RECORD_AFTER_PLAY);


    }
  }, TIME_RECORD_BEFORE_PLAY);
}

function make_perm(n) {
  array=Array.apply(null, Array(n)).map(function (_, i) {return i;});
  var currentIndex = array.length, temporaryValue, randomIndex;

  // While there remain elements to shuffle...
  while (0 !== currentIndex) {

    // Pick a remaining element...
    randomIndex = Math.floor(Math.random() * currentIndex);
    currentIndex -= 1;

    // And swap it with the current element.
    temporaryValue = array[currentIndex];
    array[currentIndex] = array[randomIndex];
    array[randomIndex] = temporaryValue;
  }

  return array;
}


function startUserMedia(stream) {
  var input = audio_context.createMediaStreamSource(stream);
  console.log('Media stream created.');

  recorder = new Recorder(input);
  console.log('Recorder initialised.');
}

function upload_audio() {
        document.getElementById("the_action").disabled = true;
        console.log('trying to upload audio...');
        recorder && recorder.exportWAV(function(blob) {
        var formData = new FormData();
        //nblob=encode_mp3_mono (oblob)


        formData.append("file", blob);
        my_current_experiment=current_experiment;
        my_current_trial_index=current_trial_index;
        var request = new XMLHttpRequest();
        request.onreadystatechange = function() {
        if (request.readyState == 4 && request.status == 200) {
          console.log('upload seems to be OK');

          console.log('analyzing recording... (this will take a few seconds)');


          //document.getElementById("result").innerHTML = request.responseText;
          jsn=JSON.parse(request.responseText);
          durl=jsn.donefilename;

          experiments[my_current_experiment].results[my_current_trial_index].res_url=durl;
          experiments[my_current_experiment].results[my_current_trial_index].trial_order=current_trial;

          trials_next();
          print_progress_message();
          document.getElementById("the_action").disabled = false;
          my_e=my_current_experiment;
          my_i=my_current_trial_index;
          get_result_url_and_save (my_e,my_i);
          // rfile=durl;
          // console.log ("waiting for results to come...");
          //  err_time21=setTimeout(function(){
          //    console.log ("trying to run results...");
          //    get_result_url (rfile)

          //   },TIME_BEFORE_STIM_AVILABLE*1
          // );

          // err_time2=setTimeout(function(){
          //    console.log ("trying to run results...");
          //    get_result_url (rfile)

          //   },TIME_BEFORE_STIM_AVILABLE*2
          // );
          // err_time25=setTimeout(function(){
          //    console.log ("trying to run results...");
          //    get_result_url (rfile)

          //   },TIME_BEFORE_STIM_AVILABLE*2.5
          // );
          // err_time3=setTimeout(function(){
          //    console.log ("trying to run results...");
          //    get_result_url (rfile)

          //   },TIME_BEFORE_STIM_AVILABLE*3
          // );


          //document.getElementById("resul")=request.donefilename;


          }
        };
        request.open("POST", "/uploadP/" + participant_id);
        request.send(formData);
      });
}

function upload_json (myjson) {
  var xmlhttp = new XMLHttpRequest();   // new HttpRequest instance
  xmlhttp.open("POST", "/saveOnSever/" + participant_id);
  xmlhttp.setRequestHeader("Content-Type", "application/json;charset=UTF-8");
  xmlhttp.send(JSON.stringify(myjson));
}

function get_result_url (murl) {
  console.log('trying to get result file...: ' + murl)

  reqwest ({
       url: '/get_results_file/' + murl  ,
       method: 'get',

      success: function (resp) {
        try {
        temp_jsn=resp;

        jsn=JSON.parse(resp.responseText);
        temp_jsn=jsn;

        console.log('finished analyzing.');

        len_midis=jsn.midis.length;


      }
      catch (e) {
          console.log('results are not ready... ( I tried to load the result file and there were not there or not yet, or format was wrong...)');
          //console.log(e);
      }

      // if (len_midis!=2) {
      //   msg="ERROR! number of recorded notes was not 2<br> " + resp.responseText;
      //   msg_red="<font color= \"red\">" + msg + "</font>"
      //   document.getElementById("results").innerHTML=msg_red;
      //   console.log('Error in analysis (wrong number of notes)');
      //   midi_orig=MIDI_NOTE;
      //   msg1= "Original midi note: " + String(midi_orig);
      //   console.log(msg1)

      // } else {
      // if (jsn.starts[0]<jsn.starts[1]) {
      //    midi_first=jsn.midis[0];
      //    midi_second=jsn.midis[1];
      //  } else {
      //    midi_first=jsn.midis[1];
      //    midi_second=jsn.midis[0];
      //  }
      //    midi_orig=MIDI_NOTE;
      //    accuracy=Math.abs(midi_second-midi_first)

      // msg1= "Original midi note: " + String(midi_orig) + "<br>"
      // msg2= "Meassured midi note: " + String(midi_first) + "<br>"
      // msg3= "Response midi note:  " + String(midi_second) + "<br>"
      // msg4= "Accuracy: " + String(accuracy) + "<br>"
      // msg5= "Accuracy(cents): " + String(Math.round(100*accuracy)) + "<br>"

      // msg=msg1+msg2+msg3+msg4+msg5;
      // document.getElementById("results").innerHTML=msg;
      // console.log('analysis OK! (see results)');
      // }

              },
     error: function (err) {
        console.log('error reading result file:')
         console.log(err);

    }
});
}

function get_result_url_and_save (experiment,trial) {

  murl=experiments[experiment].results[trial].res_url;
  console.log('trying to get result file...: ' + murl)
  reqwest ({
       url: '/get_results_file/' + murl  ,
       method: 'get',

      success: function (resp) {
        try {
        temp_jsn=resp;

        jsn=JSON.parse(resp.responseText);
        temp_jsn=jsn;

        //document.getElementById("results").innerHTML=resp.responseText;
        console.log('finished analyzing.');

        len_midis=jsn.midis.length;
        experiments[experiment].results[trial].result=jsn;
        //document.getElementById("results").innerHTML=String(jsn.midis);
      }
      catch (e) {
          console.log('results are not ready... ( I tried to load the result file and there were not there or not yet, or format was wrong...)');
          //console.log(e);
      }

              },
     error: function (err) {
        console.log('error reading result file:')
         console.log(err);

    }
});
}


window.onload = function init() {
  console.log('starting...');
  try {
    // webkit shim
    window.AudioContext = window.AudioContext || window.webkitAudioContext;
    navigator.getUserMedia = navigator.getUserMedia || navigator.webkitGetUserMedia;
    window.URL = window.URL || window.webkitURL;

    audio_context = new AudioContext;
    console.log('Audio context set up.');
    console.log('navigator.getUserMedia ' + (navigator.getUserMedia ? 'available.' : 'not present!'));
  } catch (e) {
    alert('No web audio support in this browser!');
  }

  navigator.getUserMedia({audio: true}, startUserMedia, function(e) {
    console.log('No live audio input: ' + e);
  });
  get_params();


 }

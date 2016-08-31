// Java script for audio client
//constants


var burl="http://audio.norijacoby.com/res/"
var audio_url="http://audio.norijacoby.com/notset"
//more
var TIME_RECORD_BEFORE_PLAY=200
var TIME_RECORD_AFTER_PLAY=3000
var TIME_BEFORE_STIM_AVILABLE=8000
var TIME_INSTRUCT = 1000
var audio_context;
var recorder;
var my_node_id=9998
var my_network_id=9998
var LOWER_MIDI_NOTE=document.getElementById("LowerMidiNote").value;
var HIGHER_MIDI_NOTE=document.getElementById("HigherMidiNote").value;
var MIDI_NOTE=60;
var err_time=0;
var durl

var temp_jsn

// variables of wallace line game

var TRIAL_WAIT_TIME=2000; // in between trials wait time
var MAX_TIME_TRIAL=20*1000;

var DEBUG=true; // plot internal variables (for debug puropose) on console
var DEBUG2=false; // plot internal variables on screen!


// outputs:
var results=[]; //output list
var result;    //the final output (NaN if incorrect)
var repeats=0; //number of repeats
var timeStarted;
var stage; // global variable holding the stage (canvas)

var timer_max_trial;
var GENERATION=-1;
var PARAMS


var vid = document.getElementById("audioPlayer");
vid.controls = false;
var myaudio = document.getElementById("audioPlayer");

AUDIOfileName= ''

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


  __log('preparing stimulus (this will take a few seconds)...');

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
            __log("stimulus is ready to play");
          },TIME_BEFORE_STIM_AVILABLE
        );

    },
     error: function (err) {
         console.log(err);
    }
});
}



function getAudioFileName_andPlayRecordUpload() {

 recorder.clear()
 myaudio.src=audio_url
 __log('Stimulus filename:' + audio_url);
 __log('setting up wait for audio to load...');
 myaudio.oncanplay=function () {
          __log("can play! so starting...");
          do_play_record_upload_audio()
        }
 myaudio.load()

}


function do_play_record_upload_audio() {

  __log('start recording...');
  recorder && recorder.record();
  setTimeout( function(){
    __log('start playing...');
    myaudio.onloaddata="";
    myaudio.play();
    myaudio.onended = function () {
      __log("...end playing...");

      setTimeout( function(){
       __log("...end of stimulus recording");
       recorder.stop()
       __log("...stop recording...");

         upload_audio();
        }, TIME_RECORD_AFTER_PLAY);


    }
  }, TIME_RECORD_BEFORE_PLAY);
}

function __log(e, data) {
  log.innerHTML += "\n" + e + " " + (data || '');
}


function startUserMedia(stream) {
  var input = audio_context.createMediaStreamSource(stream);
  __log('Media stream created.');

  recorder = new Recorder(input);
  __log('Recorder initialised.');
}

function upload_audio() {
__log('trying to upload audio...');
recorder && recorder.exportWAV(function(blob) {
        var formData = new FormData();
        //nblob=encode_mp3_mono (oblob)


        formData.append("file", blob);

        var request = new XMLHttpRequest();
        request.onreadystatechange = function() {
        if (request.readyState == 4 && request.status == 200) {
          __log('upload seems to be OK');

          document.getElementById("results").innerHTML= "analyzing recording... (this will take a few seconds)"
          __log('analyzing recording... (this will take a few seconds)');


          //document.getElementById("result").innerHTML = request.responseText;
          jsn=JSON.parse(request.responseText);
          durl=jsn.donefilename;

          rfile=durl;
          console.log ("waiting for results to come...");
           err_time21=setTimeout(function(){
             console.log ("trying to run results...");
             get_result_url (rfile)

            },TIME_BEFORE_STIM_AVILABLE*1
          );

          err_time2=setTimeout(function(){
             console.log ("trying to run results...");
             get_result_url (rfile)

            },TIME_BEFORE_STIM_AVILABLE*2
          );
          err_time25=setTimeout(function(){
             console.log ("trying to run results...");
             get_result_url (rfile)

            },TIME_BEFORE_STIM_AVILABLE*2.5
          );
          err_time3=setTimeout(function(){
             console.log ("trying to run results...");
             get_result_url (rfile)

            },TIME_BEFORE_STIM_AVILABLE*3
          );


          //document.getElementById("resul")=request.donefilename;


          }
        };
        request.open("POST", "/upload");
        request.send(formData);
      });
}

function get_result_url (durl) {
  console.log('I am here')
  reqwest ({
       url: '/get_results_file/' + durl  ,
       method: 'get',

    success: function (resp) {
      jsn=JSON.parse(resp.responseText);
      temp_jsn=jsn
      document.getElementById("results").innerHTML=resp.responseText;
      __log('finished analyzing.');

      len_midis=jsn.midis.length;
      if (len_midis!=2) {
        msg="ERROR! number of recorded notes was not 2<br> " + resp.responseText;
        msg_red="<font color= \"red\">" + msg + "</font>"
        document.getElementById("results").innerHTML=msg_red;
        __log('Error in analysis (wrong number of notes)');
        midi_orig=MIDI_NOTE;
        msg1= "Original midi note: " + String(midi_orig);
        __log(msg1)

      } else {
      if (jsn.starts[0]<jsn.starts[1]) {
         midi_first=jsn.midis[0];
         midi_second=jsn.midis[1];
       } else {
         midi_first=jsn.midis[1];
         midi_second=jsn.midis[0];
       }
         midi_orig=MIDI_NOTE;
         accuracy=Math.abs(midi_second-midi_first)

      msg1= "Original midi note: " + String(midi_orig) + "<br>"
      msg2= "Meassured midi note: " + String(midi_first) + "<br>"
      msg3= "Response midi note:  " + String(midi_second) + "<br>"
      msg4= "Accuracy: " + String(accuracy) + "<br>"
      msg5= "Accuracy(cents): " + String(Math.round(100*accuracy)) + "<br>"

      msg=msg1+msg2+msg3+msg4+msg5;
      document.getElementById("results").innerHTML=msg;
      __log('analysis OK! (see results)');
      }

              },
     error: function (err) {
         console.log(err);
    }
});
}



window.onload = function init() {
  __log('starting...');
  try {
    // webkit shim
    window.AudioContext = window.AudioContext || window.webkitAudioContext;
    navigator.getUserMedia = navigator.getUserMedia || navigator.webkitGetUserMedia;
    window.URL = window.URL || window.webkitURL;

    audio_context = new AudioContext;
    __log('Audio context set up.');
    __log('navigator.getUserMedia ' + (navigator.getUserMedia ? 'available.' : 'not present!'));
  } catch (e) {
    alert('No web audio support in this browser!');
  }

  navigator.getUserMedia({audio: true}, startUserMedia, function(e) {
    __log('No live audio input: ' + e);
  });

  // pitch_create_stimulus();
  // setTimeout(function(){
  //           document.getElementById("instruct").innerHTML="You will hear a tone, right after the tone please sing back..."
  //         },TIME_INSTRUCT
  //       );
 }





/////////////// LINE GAME FROM HERE /////////////////
/////////////// LINE GAME FROM HERE /////////////////
/////////////// LINE GAME FROM HERE /////////////////

function create_agent () {

    results=[]; //output list



    if (DEBUG) {
        console.log ("(1) create agent");
    }

    reqwest({
        url: "/node/" + participant_id,
        method: 'post',
        type: 'json',
        success: function (resp) {
            if (DEBUG) {
               console.log ("--->(1) trial:" + current_trial + " repeats:" + repeats + " reqwest: " + "node");
            }

            my_node_id = resp.node.id;
            my_network_id = resp.node.network_id;

            getParams();

        },
        error: function (err) {
            console.log(err);
            err_response = JSON.parse(err.response);
            if (err_response.hasOwnProperty('html')) {
                $('body').html(err_response.html);
            } else {
                allow_exit();
                go_to_page("debriefing/debrief-1");
            }
        }
    });
};

/// not only the controling parameters (of the experiment) but also all the properties of this info!!
function getParams() {
    if (DEBUG) {
        console.log ("(2) get params for my_network_id= "+ String(my_network_id));
    }
   reqwest ({
    url: "/get_params/" + my_network_id +"/" + my_node_id,
    method: 'get',
    type: 'json',
    success: function (resp) {
        if (DEBUG) {
               console.log ("--->(2) reqwest: " + "getParams (sucess)");
            }

        PARAMS=resp

       //   startInit();
      },
      error: function (err) {

        console.log(err);
        clearTimeout(err_time);
        err_time=setTimeout(function(){create_agent();},WAIT_TIME*2);
    }
});
}



// // get the seed from server:
// function startInit() {
//     if (DEBUG) {
//         console.log ("(3) trial:" + current_trial + " repeats:" + repeats + " function: " + "startInit");
//     }

//     reqwest ({
//         url: "/node/" + my_node_id + "/received_infos",
//         method: 'get',
//         type: 'json',
//         success: function (resp) {
//             if (DEBUG) {
//                console.log ("---> (3) trial:" + current_trial + " repeats:" + repeats + " reqwest: " + "received_infos");
//             }

//             TRUE_RATIO=Number(resp.infos[0].contents)
//             if (IS_FEEDBACK) { // if practice randomize from scratch each time
//               TRUE_RATIO=RANGE_MIN + Math.floor(Math.random()*(RANGE_MAX-RANGE_MIN + 1));
//              }

//             init();
//         },
//         error: function (err) {
//         console.log(err);
//         clearTimeout(err_time);
//         err_time=setTimeout(function(){create_agent();},WAIT_TIME*2);
//         }
//     });
// };


// // draw things on the screen
// function init() {
//     if (DEBUG) {
//         console.log ("(4) +-> trial:" + current_trial + " repeats:" + repeats + " function: " + "init");
//     }
//     stage = new createjs.Stage("demoCanvas");

//     var square = new createjs.Shape();
//     square.graphics.setStrokeStyle(2).beginStroke("black").beginFill("gray").drawRoundRect(SQ_X, SQ_Y, SQ_W, SQ_H,SQ_R,SQ_R,SQ_R,SQ_R);
//     stage.addChild(square);
//     stage.update();
//     timeStarted=performance.now();
//     square.addEventListener("click", handleClick);
//     document.getElementById("Target").innerHTML= "Target: "+ TRUE_RATIO + " % ";
//     document.getElementById("Target").style.color = "green";
//     document.getElementById("Feedback").style.color = "black";
//     document.getElementById("Feedback").innerHTML="Segment the bar according to the target percentage:"
//     currentRepeat=repeats;
//     getTrialNum();
//     do_not_click_again=false;

// }

// send result to server
function finished(){
    if (DEBUG) {
        console.log ("(6) trial:" + current_trial + " repeats:" + repeats + " function: " + "finished");

    }
    if (do_not_click_again) {
        if (DEBUG) {
            console.log("exiting because do not click again");
        }
        return 0;
    };

    do_not_click_again=true;
    clearTimeout(timer_max_trial);

   reqwest({
    url: "/info/" + my_node_id,
    method: 'post',
    type: 'json',
    data: {
        contents: result,
        info_type: "AudioInfo", ////////// NEED TO GET ALL PARAMS FROM NODE
            property1: repeats, // number of failed trials
            property2: reactionTime, // bandit_id
            property3: TRUE_RATIO, // remembered
            property4: results.toString(),
            property5: GENERATION
        },
        success: function (resp) {
             if (DEBUG) {
               console.log ("(6) --> trial:" + current_trial + " repeats:" + repeats + " reqwest: " + "info");
            }

            setTimeout(function(){create_agent();},WAIT_TIME);
        },
        error: function (err) {
            console.log(err);
            clearTimeout(err_time);

            err_time=setTimeout(function(){create_agent();},WAIT_TIME/2);

        }
  });
}

// // cant wait so long... abort and send NaN result
// function timeOver() {

//     if (DEBUG) {
//         console.log ("trial:" + current_trial + " repeats:" + repeats + " function: " + "timeOver");
//     }
//     //if (current_repeat!=repeats){return;}
//     document.getElementById("Feedback").innerHTML= "Time over! You only have " + Math.round(MAX_TIME_TRIAL/1000) + " seconds to complete the trial!";
//     document.getElementById("Counter").innerHTML="You may lose bonus.";
//     document.getElementById("Feedback").style.color = "red";
//     result="NaN";
//     //results.push(result);


//     reactionTime=Math.round((performance.now()-timeStarted)*10)/10;
//     var square = new createjs.Shape();
//     square.graphics.setStrokeStyle(5).beginStroke("red").beginFill("gray").drawRoundRect(SQ_X, SQ_Y, SQ_W, SQ_H,SQ_R,SQ_R,SQ_R,SQ_R);
//     stage.addChild(square);
//     stage.update();
//     do_not_click_again=false;
//     finished();
// }



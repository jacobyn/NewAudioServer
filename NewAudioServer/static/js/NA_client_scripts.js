// Java script for audio client

var TIME_RECORD_BEFORE_PLAY=200
var TIME_RECORD_AFTER_PLAY=3000
var audio_context;
var recorder;
var my_node_id=9998

var vid = document.getElementById("audioPlayer");
vid.controls = false;
var myaudio = document.getElementById("audioPlayer");

AUDIOfileName= ''

function load_play_record_stim() {
  __log('Try to get stimulus filename...');
  AUDIOfileName = getAudioFileName();



}
// function encode_mp3_mono (oblob) {
//   var samples;
//   var fileReader = new FileReader();
//   fileReader.onload = function() {
//       samples = this.result;
//   };
//   fileReader.readAsArrayBuffer(oblob);

//   channels = 1; //1 for mono or 2 for stereo
//   sampleRate = 44100; //44.1khz (normal mp3 samplerate)
//   kbps = 128; //encode 128kbps mp3
//   mp3encoder = new lamejs.Mp3Encoder(channels, sampleRate, kbps);
//   var mp3Data = [];

//   //samples = new Int16Array(44100); //one second of silence (get your data from the source you have)
//   sampleBlockSize = 1152; //can be anything but make it a multiple of 576 to make encoders life easier

//   var mp3Data = [];
//   for (var i = 0; i < samples.length; i += sampleBlockSize) {
//     sampleChunk = samples.subarray(i, i + sampleBlockSize);
//     var mp3buf = mp3encoder.encodeBuffer(sampleChunk);
//     if (mp3buf.length > 0) {
//         mp3Data.push(mp3buf);
//     }
//   }
//   var mp3buf = mp3encoder.flush();   //finish writing mp3

//   if (mp3buf.length > 0) {
//       mp3Data.push(new Int8Array(mp3buf));
//   }

//   var blob = new Blob(mp3Data, {type: 'audio/mp3'});
//   console.log('MP3 URl: ', url);

//   return blob
// }

function getAudioFileName_andPlayRecordUpload() {
 recorder.clear()
 reqwest ({
    url: "/getAudioFileName",
    method: 'get',
    type: 'json',
    success: function (resp) {
        AUDIOfileName =resp.fname;
        __log('Stimulus filename:' + AUDIOfileName);
         __log('seeting up wait for audio to load...');

        myaudio.src=AUDIOfileName;
        myaudio.oncanplay=function () {
          __log("can play! so starting...");
          do_play_record_upload_audio()
        }
        myaudio.load()

      },

      error: function (err) {
        console.log(err);
        __log('error finding filename from server.\n' + err);
        // AUDIOfileName ='uploads/stim1.ogg'
        // __log('Stimulus filename:' + AUDIOfileName);
        // var myaudio = document.getElementById("audioPlayer"); //IMPORTANT: eventually delete
        // myaudio.onloaddata="do_play_record_audio()"//IMPORTANT: eventually delete
        // myaudio.src=AUDIOfileName;//IMPORTANT: eventually delete
        // err_response = JSON.parse(err.response);
        // if (err_response.hasOwnProperty('html')) {
        //     $('body').html(err_response.html);
        // } else {
        //     allow_exit();
        //     window.location = "/debrief/1?hit_id=" + hit_id + "&assignment_id=" + assignment_id + "&worker_id=" + worker_id + "&mode=" + mode;
        // }
        }
    });
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
          }
        };
        request.open("POST", "/upload");
        request.send(formData);
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
};

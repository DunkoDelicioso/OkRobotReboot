//Example STT - "watson"

const exec = require('child_process').execSync;
const util = require('util');

function listen(something){
  const user = "USER";
  const password = "PASS";
  var data = "@" + something;
  command = util.format('curl -X POST -u \"%s:%s\" -H \"Content-Type: audio/flac\" --data-binary %s \"https://stream.watsonplatform.net/speech-to-text/api/v1/recognize?timestamps=true&max_alternatives=3\" | grep -m1 \"transcript\" ', user,password,data);
  output = exec(command, function(error, stdout, stderr){console.log('stdout: ' + stdout);});
  return output.toString().trim();
}

console.log(listen("_audio/audio-file.flac"));

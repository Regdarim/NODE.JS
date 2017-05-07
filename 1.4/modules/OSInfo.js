var os = require('os');



function getOSinfo() {
    var type = os.type();
    if(type === 'Darwin') {
        type = 'OSX';
    } else if(type === 'Windows_NT') {
        type = 'Windows';
    }
    var release = os.release();
    var cpu = os.cpus()[0].model;
    var uptime = os.uptime();
    var userInfo = os.userInfo();
    console.log('System:', type);
    console.log('Release:', release);
    console.log('CPU model:', cpu);
    time();
    console.log('User name:', userInfo.username);
    console.log('Home dir:', userInfo.homedir);

    function time() {
var uptime = os.uptime();
var h = Math.floor(uptime/3600);
var min =0;
var s = 0;
if(uptime%3600!==0){ 
    min = Math.floor((uptime - 3600*h)/60);
    if(((uptime - 3600*h)/60)%60!==0){
        s= uptime -h*3600 -min*60;
}
}
    console.log('Uptime: '+h+'h, '+min+'min, '+s+'s');

}
}





exports.print = getOSinfo;
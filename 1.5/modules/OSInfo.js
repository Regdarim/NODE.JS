var os = require('os');
var colors = require('colors');

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
    console.log(colors.grey('System: '), type);
    console.log(colors.red('Release:'), release);
    console.log(colors.blue('CPU model:'), cpu);
    time();
    console.log(colors.yellow('User name:'), userInfo.username);
    console.log(colors.grey('Home dir:'), userInfo.homedir);

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
        console.log(colors.green('Uptime: ')+h+'h, '+min+'min, '+s+'s');
    }
}

exports.print = getOSinfo;
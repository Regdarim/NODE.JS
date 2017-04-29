var os = require('os');
process.stdin.setEncoding('utf-8');

process.stdin.on('readable', function() {
     var input = process.stdin.read();  
     if(input !== null) {
        var instruction = input.toString().trim();
        var version = process.versions.node;
        var lang = process.env.LANG;
        switch(instruction) {
            case '/exit':
                process.stdout.write('Quitting app!\n’');
                process.exit();
                break;
            case '/sayhello':
                process.stdout.write('hello!\n');
                break;
            case '/info':
                process.stdout.write(version + '\n' + lang);
                break;
            default:
                process.stderr.write('Wrong instruction!\n');
        };
    }
});
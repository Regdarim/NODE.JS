var fs = require('fs');
var colors = require('colors');

fs.readdir('../', function(err, files){
	if(err){
		console.log(err);
	}
	console.log("Nazwy folderow:\n".red + files);
	var files = files;
	fs.writeFile('./new.txt', files, function(err){
		if(err){
			console.log(err);
		}
		console.log("zapisano!");
		fs.readFile('../new.txt', 'utf-8', function(err, data){
			if(err){
				console.log(err);
		}
			console.log("nazwy folderow zapisane w pliku .txt:\n" .green + data);
		});
	});
});
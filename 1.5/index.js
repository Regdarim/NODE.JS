var fs = require('fs');
var colors = require('colors');


fs.readdir('../', function(err, files){
	if(err){
		throw err;
	}
	console.log("Nazwy folderow:\n".red +files);
	var files = files;
	fs.writeFile('../new.txt',files, function(err){
		if(err){
			throw err;
		}
		console.log("zapisano!");
		fs.readFile('../new.txt', 'utf-8', function(err, data){
			console.log("\nnazwy folderow zapisane w pliku .txt:\n" .green + data);
		});
	});
});
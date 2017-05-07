var http = require('http');
var fs = require("fs");

var server = http.createServer();

server.on('request', function(request, response) {
            response.setHeader("Content-Type", "text/html; charset=utf-8");
            if (request.method == 'GET' && request.url === "/") {
                fs.readFile('./index.html', function(err, data) {
                    if (err)  console.log(err);
                    response.write(data);
                    response.end;
                });

            } else {

                fs.readFile('cat.jpg', function(err, data) {
                        if (err)  console.log(err); 
                        	response.statusCode = 404;
                            response.writeHead(200, {
                                'Content-Type': 'image/jpeg'
                            });
                            response.end(data); 
                        })
                    }
                });
            server.listen(8080);
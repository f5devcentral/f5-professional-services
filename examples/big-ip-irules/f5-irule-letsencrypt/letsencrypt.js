'use strict'

var f5 = require('f5-nodejs');

var ilx = new f5.ILXServer();

ilx.addMethod('jsonPost', function (req, res) {

  try {
    var jsonData = JSON.parse(req.params()[0])
  } catch (err) {
    console.log('Error with JSON.parse: ' + err.message);
    res.reply([1])
    return;
  }
  
  try {
      var challenge = jsonData['challenges'][0]
      var filename = challenge['fileName']
      var content = challenge['content']
      
      if (filename === undefined ) {
          throw Error ("'filename' property is missing")
      }
      
      if (content === undefined ) {
          throw Error ("'content' property is missing")
      }
      
  } catch (err) {
    console.log('HTTP-01 challenge not found: ' + err.message);
    res.reply([2])
    return;      
  }

  res.reply([0,filename,content]);
});

ilx.listen();

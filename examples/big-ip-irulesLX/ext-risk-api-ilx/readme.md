# External Risk Engine API iRuleLX
Custom iRuleLX project created to make an external call to a risk engine during an APM per-session-policy that responds with a risk score and a decision on whether to allow the user or not.

#### Dependencies:
```javascript
var f5 = require('f5-nodejs');
var rest_client = require('node-rest-client').Client;
```
github: [aacerox/node-rest-client](https://github.com/aacerox/node-rest-client#readme)<br>
npmjs [REST Client for Node.js](https://www.npmjs.com/package/node-rest-client)

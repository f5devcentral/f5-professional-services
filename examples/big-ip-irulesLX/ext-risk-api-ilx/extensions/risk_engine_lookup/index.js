/*
 * iRulesLX RPC for Risk Engine(PDP) Evaluation
 *
 */

/* Import the f5-nodejs module. */
var f5 = require('f5-nodejs');
var rest_client = require('node-rest-client').Client;
var logger = new f5.ILXLogger();

/* Create a new rpc server for listening to TCL iRule calls. */
// logger.send('Instantiating a new listener for xTrust PDP API iRule');
var ilx = new f5.ILXServer();
ilx.listen();

/**
  * PDP API Lookup
  *
  * @params {String} host
  * @params {String} address
  * @return {Object} result
  */

ilx.addMethod('risk_engine_api_call', function(req, res) {
    /*logger.send('*** xTrust PDP API LX iRule Triggered ***')*/
    const pdp_host = req.params()[0];
    const sessionID = req.params()[1];
    const oidc_claim_oid = req.params()[2];
    const oidc_claim_preferred_username = req.params()[3];
    const app = req.params()[4];
    const vpn = req.params()[5];
    const ip_address = req.params()[6];
 
    var pdp_client = new rest_client();
    
    const pdp_client_args = {
    headers: { 'Authorization': 'Bearer ey...' },
	requestConfig: { timeout: 3000 },
	responseConfig: { timeout: 3000	},
	/*connection: {
		secureOptions: constants.SSL_OP_NO_TLSv1_2,
		ciphers: 'ECDHE-RSA-AES256-SHA:AES256-SHA:RC4-SHA:RC4:HIGH:!MD5:!aNULL:!EDH:!AESGCM',
		honorCipherOrder: true
	},*/
	rejectUnauthorized: false
    };
    
    //logger.send('Sending the PDP query');
    /** Example Call: http://ipcheck.organization.com/api/v1/ipcheck?ip=192.168.1.2&userid=bobsmith&session=1234abcd&event=start  */
    pdp_client.get(pdp_host + "?ip=" + ip_address + "&user=" + oidc_claim_preferred_username + "&session=" + sessionID + "&policy=" + app + "&oid=" + oidc_claim_oid + "&vpn=" + vpn, pdp_client_args, function (pdp_data, pdp_resp) {
        const unauthorized = pdp_data.hasOwnProperty('message');
        if(unauthorized) {
            logger.send('xTrust PDP query failed due to: ' + JSON.stringify(pdp_data));
            return res.reply(pdp_data.message);
        }
        else {
            //logger.send('xTrust PDP query completed - Data: ' + JSON.stringify(pdp_data));
            return res.reply(JSON.stringify(pdp_data.allow));
        }
	    }).on('error', function (err) {
	        logger.send('API Fatal error');
	        return res.reply("error");
        }).on('requestTimeout', function (req) {
	        logger.send('API request has expired');
	        //req.abort();
	        return res.reply("error");
	    }).on('responseTimeout', function (res) {
	        logger.send('API response has expired');
	        //res.abort();
	        return res.reply("error");
	    })});

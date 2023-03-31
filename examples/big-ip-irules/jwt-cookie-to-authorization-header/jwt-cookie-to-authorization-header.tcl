#Take JWT from cookie and insert as Authorization header for APM

when RULE_INIT {
   # Only use different than 0 in a Non-Production enviroment to troubleshoot iRule.  Never enable in Production! 
   set static::keydebug 0

   #Name of the cookie that the JWT will be stored in. Replace by cookie name
   set static::transmitcookiename "accessToken"  
}

when HTTP_REQUEST {

    #Check to see if cookie exists.

    if {[HTTP::cookie exists $static::transmitcookiename] } {
    	set jwt_in [HTTP::cookie $static::transmitcookiename]
		if { $static::keydebug > 0 } { log local0. "#####Initial Token in cookie is $jwt_in #####" }

    #F5 requires JWT be put in Aurhtorization header to validate 
		if { $static::keydebug > 0 } { log local0. "#####Inserting Aurhtorization Header - [HTTP::uri]  #####" }	
        HTTP::header insert Authorization "Bearer $jwt_in"  
        if { $static::keydebug > 0 } { log local0. "[HTTP::header value Authorization]" }
    #unset vars
		unset jwt_in

    }elseif {[HTTP::header exists "Authorization"] } {
    		if { $static::keydebug > 0 } {log local0. "##### Authorization  [HTTP::header "Authorization"] #####"}
    }
}
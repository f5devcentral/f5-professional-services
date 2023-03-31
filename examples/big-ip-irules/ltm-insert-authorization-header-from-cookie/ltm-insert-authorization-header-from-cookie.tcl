#ltm-insert-authorization-header-from-cookie.tcl
#this iRule insert authorization header from a cookie value

when RULE_INIT {
   # Debug for logging on ltm log set to 1
   set static::vardebug 0

   #Name of the cookie, replace by cookie_name
   set static::cookiename "cookie_name"  
}

when HTTP_REQUEST {

    #Check to see if cookie exists.

    if {[HTTP::cookie exists $static::cookiename] } {
    	set cookie_in [HTTP::cookie $static::cookiename]
		if { $static::vardebug > 0 } { log local0. "#####Cookie value is $cookie_in #####" }
    		
        HTTP::header insert Authorization "Authorization $cookie_in"  
        if { $static::vardebug > 0 } { log local0. "[HTTP::header value Authorization]" }
    #unset vars
		unset cookie_in

    }elseif {[HTTP::header exists "Authorization"] } {
    		if { $static::vardebug > 0 } {log local0. "##### Authorization Header exists [HTTP::header "Authorization"] #####"}
    }
}
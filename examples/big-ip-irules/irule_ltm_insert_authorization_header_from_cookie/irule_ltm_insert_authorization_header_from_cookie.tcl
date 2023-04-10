#ltm-insert-authorization-header-from-cookie.tcl
#this iRule insert authorization header from a cookie name value 

when RULE_INIT {
   #Name of the cookie, replace by the specific cookie_name
   set static::cookiename "cookie_name"  
}

when HTTP_REQUEST {
    #Check to see if cookie exists.
   if {[HTTP::cookie exists $static::cookiename] } {
		set cookie_in [HTTP::cookie $static::cookiename]
		HTTP::header insert Authorization "Authorization $cookie_in"  
        log local0. "Authorization Header from cookie [HTTP::header value Authorization]"
		#unset vars
		unset cookie_in
    }elseif {[HTTP::header exists "Authorization"] } {
    	log local0. "# Authorization Header exists [HTTP::header "Authorization"] #"
    }
}
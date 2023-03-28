when RULE_INIT {
    set static::letsencrypt_username "test"
    set static::letsencrypt_password "test"
    set static::letsencrypt_challenge_lifetime 3600
    set static::debug 1
}

when HTTP_REQUEST {

    set uri [HTTP::uri]
    set clientip [IP::client_addr]
    set letsencryptApi 0


    if { ($uri equals "/api/letsencrypt") and ([HTTP::method] equals "POST") } {
    
        set username [HTTP::header "username"]
        set password [HTTP::header "password"]
        
        # Return a 401 (Unauthorized) if the credentials are invalid
        if { not (($username equals $static::letsencrypt_username) and ($password equals $static::letsencrypt_password)) } {
        
            if { $static::debug } {
                log local0. "Authentication failed. Check the username and password."
            }
            
            HTTP::respond 401 content "\{\"status\":\"error\", \"message\":\"Credentials invalid or missing\"\}" "Content-Type" "application/json" "Cache-Control" "no-store"
            return
            
        }
        
        # Return a 415 (Unsupported Media Type) if the HTTP payload is not JSON
        if { [HTTP::header "Content-Type"] ne "application/json" } {
        
            if { $static::debug } {
                log local0. "Unsupported Media Type. Check if the request Content-Type is application/json"
            }
            
            HTTP::respond 415 content "\{\"status\":\"error\", \"message\":\"Only JSON payload is allowed\"\}" "Content-Type" "application/json" "Cache-Control" "no-store"
            return
        }
        
        # Return a 403 (Forbidden) if the Client IP is not allowed
        if { !([class match [getfield $clientip "%" 1] equals "/Common/dg-letsencrypt-api-allowed-ips"]) } {
        
            if { $static::debug } {
                log local0. "Access denied for the client IP $clientip. "
            }
            
            HTTP::respond 403 content "\{\"status\":\"error\", \"message\":\"Forbidden\"\}" "Content-Type" "application/json" "Cache-Control" "no-store"
            return
        
        }
    
        # Define the number of bytes that will be collected
        if { ([HTTP::header "Content-Length"] ne "") && ([HTTP::header "Content-Length"] <= 1048576) } {
            set content_length [HTTP::header "Content-Length"]
        } else {
            set content_length 1048576
        }
        
        if { $content_length > 0} {
            HTTP::collect $content_length
        }
        
        set letsencryptApi 1
        
    } elseif { $uri starts_with "/.well-known/acme-challenge/" } {
    
        set filename [URI::basename [HTTP::uri]]
        set content [ table lookup -subtable "acme-challenges" -notouch $filename]
        
        if { $static::debug } {
            log local0. "HTTP-01 acme challenge requested: $filename"
        }
        
        if { $content ne "" } {
        
            if { $static::debug } {
                log local0. "HTTP-01 acme challenge found: $content"
            }
            HTTP::respond 200 content $content "Content-Type" "text/plain"
            
        } else {
        
            if { $static::debug } {
                log local0. "HTTP-01 acme challenge not found"
            }
            HTTP::respond 404 content "Not found"
        }

    }
}

when HTTP_REQUEST_DATA {

    if { $letsencryptApi } {

        set handle [ILX::init "letsencrypt_pl" "letsencrypt_ext"]

        if { [catch {ILX::call $handle jsonPost [HTTP::payload]} result] } {
 
            log local0.error  "Client - $clientip, ILX failure: $result"
            HTTP::respond 400 content "There has been an error"
            return
      
        }
    
        if { [lindex $result 0] > 0 } { 
        
            switch [lindex $result 0] {
                1 { set error_msg "Invalid JSON" } 
                2 { set error_msg "HTTP-01 acme challenge not found" }
            }
            
            if { $static::debug } {
                log local0. "Error while processing the JSON: $error_msg."
            }
            
            HTTP::respond 400 content "\{\"status\":\"error\", \"message\":\"$error_msg\"\}" "Content-Type" "application/json" "Cache-Control" "no-store"
            
        } else {
        
            set filename [lindex $result 1]
            set content [lindex $result 2]
        
            table set -subtable "acme-challenges" $filename $content $static::letsencrypt_challenge_lifetime $static::letsencrypt_challenge_lifetime
            
            if { $static::debug } {
                log local0. "HTTP-01 acme challenge added to the session table (filename=$filename,content=$content)"
            }
            
            HTTP::respond 200 content "\{\"status\":\"success\", \"message\":\"The HTTP-01 acme challenge will be automatically removed in $static::letsencrypt_challenge_lifetime seconds.\"\}" "Content-Type" "application/json"
        
        }
    }
    
}
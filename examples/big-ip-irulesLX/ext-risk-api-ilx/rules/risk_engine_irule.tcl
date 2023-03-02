when RULE_INIT {
    #log local0.info "xTrust PDP iRule Instantiated"
}

when ACCESS_POLICY_AGENT_EVENT {
    if { [ACCESS::policy agent_id] eq "riskAPI" }
    {
    # Set the pdp host
    set pdp_host "https://ipcheck.organization.com/api/v1/ipcheck"
    set api_timeout 10000
    # Grab the APM session ID
    set session_id [ACCESS::session data get session.user.sessionid]
    # Grab the session parameters
    # set oidc_claim_oid [ACCESS::session data get session.oauth.client.last.id_token.oid]
    set oidc_claim_oid [ACCESS::session data get session.saml.last.attr.name.http://schemas.microsoft.com/identity/claims/objectidentifier]
    # set oidc_claim_preferred_username [ACCESS::session data get session.oauth.client.last.id_token.preferred_username]
    set oidc_claim_preferred_username [ACCESS::session data get session.saml.last.attr.name.http://schemas.xmlsoap.org/ws/2005/05/identity/claims/name]
    set app [ACCESS::session data get session.access.profile]
    set vpn [ACCESS::session data get session.server.network.name] 
    set ip_address [ACCESS::session data get session.user.clientip]
      
    # Initiate the ilx handler
    set ilx_handle [ILX::init "risk_engine_api_plugin" "risk_engine_lookup"] 
    # Verify that the IP address was set; error out otherwise
    if { [info exists oidc_claim_oid] && [info exists oidc_claim_preferred_username] && [info exists app] && [info exists ip_address] } {
        #log local0.info "xTrust PDP ($session_id): New query (PDP Host: $pdp_host, OID: $oidc_claim_oid, Session: $session_id, Username: $oidc_claim_preferred_username, App: $app, Client IP: $ip_address)"
    } else {
        log local0.error "xTrust PDP ($session_id): Query failure in iRule TCL: missing client parameter(s)"
        return
    }
    
    # Perform the PDP query
    if {[catch {ILX::call $ilx_handle -timeout $api_timeout "risk_engine_api_call" $pdp_host $session_id $oidc_claim_oid $oidc_claim_preferred_username $app $vpn $ip_address} response]} {
        log local0.error "PDP ($session_id): ILX Failure for [IP::client_addr], ILX failure: $response"
        set response "error"
        return
    } else {
        #log local0.info "PDP ($session_id): ILX process instantiated"
    }
    
	# Allow/deny session based on PDP response
    if { $response contains "true"} {
        #log local0.info "PDP ($session_id): Accepting session"
        ACCESS::session data set session.custom.userres true
    }
    elseif { $response contains "false"} {
        log local0.info "PDP ($session_id) | UserID: ($oidc_claim_preferred_username): Denying session due to risk score exceeding threshold"
        ACCESS::session data set session.custom.userres false
    } 
    elseif { $response contains "forbidden" | $response contains "unauthorized" | $response contains "error"} {
        log local0.error "PDP ($session_id) | UserID: ($oidc_claim_preferred_username): PDP Error response: $response, allowing session by default"
        ACCESS::session data set session.custom.userres true
    } else {
        log local0.error "PDP ($session_id) | UserID: ($oidc_claim_preferred_username): PDP failed to respond, allowing session by default"
        ACCESS::session data set session.custom.userres true
    }
}
}





#This iRule was created by F5 Neworks 
#The purpose of this rule is to bypass DNS Express for domains who's subdomains
#overlap with configured forward zones #under DNS cache.  
#List of domains to be bypassed can be found in the GUI interface at #System››File #Management:Data Group #File List››DNSX_bypass_domains List can be edited at same
#location

when DNS_REQUEST {
    if { [class match -name [DNS::question name] ends_with DNSX_bypass_domains] }{
        set dnsxQR [DNS::query dnsx [DNS::question name] [DNS::question type]]
            foreach rrs $dnsxQR {
                foreach rr $rrs {
                    if { [DNS::type $rr] == "SOA" }{
                      DNS::disable dnsx 
                      return
                }
            }
        }
    }
}
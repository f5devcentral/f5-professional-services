When you want to enable/disable all of the logging statements in your iRule, change the value of static::debug to 1 to enable them and 0 to disable them.
You can add more logging statements throughout the iRule at different places following the template: if { $static::debug } {log local0. "Message"}

This iRule is for HTTPS VIPs with Serverside SSL enabled.

Therefore, for any URI calls destined to HTTP pools, the serverside SSL needs to be disabled.

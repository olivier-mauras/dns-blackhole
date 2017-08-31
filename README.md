BlackHole
=========

Most of code comes from here: http://git.mauras.ch/Various/powerdns_recursor_ads_blocking.  
Check it for history.  

This script helps you create a blackhole zone for Unbound or PowerDNS Recursor, using some well known ads/tracking/malware lists.  

Features
--------

- Supports both [Unbound](https://www.unbound.net/) and [PowerDNS recursor](https://www.powerdns.com/recursor.html) configuration syntax
- Supports 3 different list format
    - Host file
    - [Easylist](https://easylist.to/)
    - [Disconnect](https://disconnect.me/)
- Lets you whitelist/blacklist domains
- YAML configuration file

Tested with python 2.7 and 3.6

Installation
------------
``` bash
cd /etc
git clone http://git.mauras.ch/Various/blackhole
```

### Unbound  

Requires unbound >= `1.6`, using the default zone file with unbound `1.5` will certainly make it eat all your ram and swap before getting killed.  

Add `include: "/etc/unbound/blackhole.zone"` before any forward option in your unbound configuration.  

### PowerDNS Recursor  

Add `forward-zones-file=/etc/pdns/blackhole.zone` in your recursor configuration.  
Ensure your don't have anything running on `127.0.0.2:6666` or change port details in configuration file.  

FAQ
---

### Why using forward-zones-file option instead of auth-zones in PowerDNS recursor?  

Syntax of the `auth-zones` is like this: `auth-zones=dom1=<zone>,dom2=<zone>,dom3=<zone>,etc`  
While this may work for 5000 black holed domains, for almost 700 000 the speed of generation is so slow that it takes several tens of minutes to complete. Even worse, with such a list, pdns-recursor is not even able to start and will crash.  
By using the `forward-zones-file` pdns-recursor takes around 5 more seconds to process the zone file.  

TODO
----

- Cache is not implemented yet
- Log is not implemented yet

BlackHole
=========

Most of code comes from here: http://git.mauras.ch/Various/powerdns_recursor_ads_blocking.  
Check it for history.  

This script helps you create a blackhole zone for your DNS server, using some well known ads/tracking/malware lists.  
As long as your DNS server allows to include a file containing one domain per line with its config syntax it should work.  
Right now known to work and tested:

- [Unbound](https://www.unbound.net/) 
- [PowerDNS recursor](https://www.powerdns.com/recursor.html) 
- [Dnsmasq](http://www.thekelleys.org.uk/dnsmasq/doc.html)

Generating an agregated host file is also possible.  

Features
--------

- Not bound to a specific DNS server, generates a file format of your choice
- Supports 3 different list format
    - Host file
    - [Easylist](https://easylist.to/)
    - [Disconnect](https://disconnect.me/)
- Lets you whitelist/blacklist domains
- YAML configuration file

While the shebang is set on python36, the script works fine on python 2.7

Installation
------------

The script requires `yaml` and `requests` modules.  

``` bash
cd /etc
git clone http://git.mauras.ch/Various/blackhole
```

#### Unbound  

Requires unbound >= `1.6`, using the default zone file with unbound `1.5` will certainly make it eat all your ram and swap before getting killed.  
Add `include: "/etc/unbound/blackhole.zone"` right after your `server:` block.  
Use the following `zone_data` in your `blackhole.yml` (default):

``` yaml
zone_data: 'local-zone: "{domain}" always_nxdomain'
```

`{domain}` wil be replaced by the blackholed domains

#### PowerDNS Recursor  

Add `forward-zones-file=/etc/pdns/blackhole.zone` in your recursor configuration.  
Ensure your don't have anything running on `127.0.0.2:6666` or change port details in configuration file.  
Use the following `zone_data` in your `blackhole.yml`:

``` yaml
zone_data: '{domain}=127.0.0.2:6666'
```

`{domain}` wil be replaced by the blackholed domains

#### Dnsmasq  

Add `conf-dir=/etc/dnsmasq.d` in your dnsmasq config and point your `zone_file` option to `/etc/dnsmasq.d/blackhole.conf`  
Use the following `zone_data` in your `blackhole.yml`:

``` yaml
zone_data: 'server=/{domain}/'
```

`{domain}` wil be replaced by the blackholed domains  

#### Host file

Use the following `zone_data` in your `blackhole.yml`:

``` yaml
zone_data: '127.0.0.1 {domain}'
```

<br\>

Once you're happy with your configuration Just run `./blackhole.py`


Configuration
-------------

As the configuration file is in YAML, you can use YAML anchors

```yaml
blackhole:
  general:
    cache: /var/cache/blackhole
    log: /var/log/blackhole/blackhole.log
    whitelist: /etc/blackhole/whitelist
    blacklist: /etc/blackhole/blacklist
    blackhole_lists:
      hosts:
        - http://someonewhocares.org/hosts/hosts
        - https://hosts-file.net/download/hosts.txt
        - http://winhelp2002.mvps.org/hosts.txt
        - http://www.malwaredomainlist.com/hostslist/hosts.txt
        - https://pgl.yoyo.org/adservers/serverlist.php?hostformat=hosts;showintro=0
      easylist: &bh_easy
        - https://easylist.to/easylist/easylist.txt
        - https://raw.githubusercontent.com/paulgb/BarbBlock/master/BarbBlock.txt
      disconnect: &bh_disconnect
        url: https://services.disconnect.me/disconnect-plaintext.json
        categories: # Advertising, Analytics, Disconnect, Social
          - Advertising
          - Analytics
  config:
    zone_file: /etc/unbound/blackhole.zone
    # {domain} will be replaced by the blackholed domain, do not change it here
    zone_data: 'local-zone: "{domain}" always_nxdomain'
    blackhole_lists:
      hosts:
        - http://winhelp2002.mvps.org/hosts.txt
      easylist: *bh_easy
      disconnect: *bh_disconnect
```

In this example you would keep `easylist` and `disconnect` lists, but would remove all host file lists except mvps.

FAQ
---

#### Why using forward-zones-file option instead of auth-zones in PowerDNS recursor?  

Syntax of the `auth-zones` is like this: `auth-zones=dom1=<zone>,dom2=<zone>,dom3=<zone>,etc`  
While this may work for 5000 black holed domains, for almost 700 000 the speed of generation is so slow that it takes several tens of minutes to complete. Even worse, with such a list, pdns-recursor is not even able to start and will crash.  
By using the `forward-zones-file` pdns-recursor takes around 5 more seconds to process the zone file.  

TODO
----

- Cache is not implemented yet
- Log is not implemented yet

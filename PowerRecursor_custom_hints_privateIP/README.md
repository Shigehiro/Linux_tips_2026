# PowerDNS Recursor: Using custom hints in a private IP address range

A small tip.

When using PowerDNS Recursor in an environment with private IP addresses, pay attention to the "dont_query" option.<br>
[outgoing.dont_query](https://docs.powerdns.com/recursor/yamlsettings.html#outgoing-dont-query)

PowerDNS Recursor 5.4.7<br>

recursor.conf
```yaml
carbon:
dnssec:
   aggressive_nsec_cache_size: 0
   #negative_trustanchors: []
   negative_trustanchors:
   - name: internal.lan
   validation: off
ecs:
incoming:
   allow_from:
   - 0.0.0.0/0
   listen:
   - 0.0.0.0
logging:
nod:
outgoing:
   dont_query: []
   source_address:
   - 0.0.0.0
packetcache:
recordcache:
recursor:
   #allow_trust_anchor_query: false
   hint_file: '/usr/local/etc/root.hints'
   qname_minimization: false
   security_poll_suffix: 
snmp:
webservice:
```
# check_mk bird check

Checks the status, memory and protocols of the BIRD Internet Routing Daemon.

BIRD and BIRD6 are supported.

Also available as mkp package on check_mk Exchange: [bird-1.1.mkp](https://mathias-kettner.de/check_mk_exchange_file.php?HTML=&file=bird-1.1.mkp)

See checkman pages for more details:

* [bird.status](checkman/bird.status)
* [bird.memory](checkman/bird.memory)
* [bird.protocols](checkman/bird.protocols)

## Install
Install the plugin on your check_mk servers:
```bash
wget -O bird-1.1.mkp "https://mathias-kettner.de/check_mk_exchange_download.php?HTML=&file=bird-1.1.mkp"
[ "$(sha256sum bird-1.1.mkp)" == "039e233e05f6a994dfa0a9af261b0d419b9972ca3e50d06457c6274f38656e13  bird-1.1.mkp" ] && check_mk -vP install bird-1.1.mkp
```

Install the agent plugin on your bird servers:
```bash
wget -O /usr/lib/check_mk_agent/plugins/bird "https://raw.githubusercontent.com/freddy36/check_mk_extensions/master/bird/agents/plugins/bird"
chmod 755 /usr/lib/check_mk_agent/plugins/bird
```

Optionaly you might want to add a service dependency like this to your main.mk:
```python
service_dependencies = [
 ("BIRD%s Status", ALL_HOSTS, ["BIRD(.*) Protocol .*", "BIRD(.*) Memory"]),
]
```

To enable the "Time since last state change" graph for protocols, ``timeformat protocol iso long;`` must be added to your bird config.

Finaly just re-inventorize your hosts.

## Changelog
### Version 1.1

 * Fix agent plugin for Debian wheezy
 * Fix for clustered services
 * Fix OSPF support for BIRD Version >= 1.5
 
### Version 1.0

 * initial release
 

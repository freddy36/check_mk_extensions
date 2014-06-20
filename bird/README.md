# check_mk bird check

Checks the status, memory and protocols of the BIRD Internet Routing Daemon.

BIRD and BIRD6 are supported.

Also available as mkp package on check_mk Exchange: [bird-1.0.mkp](http://exchange.check-mk.org/index.php?option=com_remository&Itemid=59&func=fileinfo&id=144)

See checkman pages for more details:

* [bird.status](checkman/bird.status)
* [bird.memory](checkman/bird.memory)
* [bird.protocols](checkman/bird.protocols)

## Install
Install the plugin on you check_mk server:
```bash
wget -O bird-1.0.mkp "http://exchange.check-mk.org/index.php?option=com_remository&Itemid=53&func=download&id=144&chk=6cee28d076a6ec9d6c6a9c065ac14f4f&no_html=1"
[ "$(sha256sum bird-1.0.mkp)" == "ad7332515c3e6cb4dac659894095ba232c87ec816687bc2fdeb26605506e35cf  bird-1.0.mkp" ] && check_mk -vP install bird-1.0.mkp
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

To enable the "Time since last state change" graph for protocols, ``timeformat route iso long;`` must be added to your bird config.

Finaly just re-inventorize your hosts.

## Changelog

### Version 1.0

 * initial release
 

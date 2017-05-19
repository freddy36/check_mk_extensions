# check_mk bird check

Checks the status, memory and protocols of the BIRD Internet Routing Daemon.

BIRD and BIRD6 are supported.

See checkman pages for more details:

* [bird.status](checkman/bird.status)
* [bird.memory](checkman/bird.memory)
* [bird.protocols](checkman/bird.protocols)

## Install

To enable the "Time since last state change" graph for protocols, ``timeformat protocol iso long;`` must be added to your bird config.


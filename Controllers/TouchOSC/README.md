# Kasm TouchOSC -> Unify

Expected setup is

TouchOSC -> UDP 9000 -> Protokol
Protokol -> Forwards to UDP 9001 -> Unify

Note right now stand alone Unify only
(apparently VST/AU coming but some port 
juggling is needed)

OSC messages...

MacroKnobs:

/macro/1/(x)
/macro/2/(x)
...
/macro/16/(x)
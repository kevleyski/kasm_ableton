#!/bin/bash

# Kasm patch file fixups


duplicates() {
  EXT=${1:-aupreset}
  find . -name "*-1.${EXT}" -exec rm {} \;
  find . -name "*-2.${EXT}" -exec rm {} \;
  find . -name "*-3.${EXT}" -exec rm {} \;
  find . -name "*-4.${EXT}" -exec rm {} \;
  find . -name "*-5.${EXT}" -exec rm {} \;
  find . -name "*-6.${EXT}" -exec rm {} \;
  find . -name "*-7.${EXT}" -exec rm {} \;
  find . -name "*-8.${EXT}" -exec rm {} \;
  find . -name "*-9.${EXT}" -exec rm {} \;
}

replacer() {
  WHAT=$1
  WITH=$2
  UPPER=$(tr '[:lower:]' '[:upper:]' <<<"${WHAT}")
  CAP=$(tr '[:lower:]' '[:upper:]' <<< "${WHAT:0:1}")${WHAT:1}

    mmv "${WHAT} - *" "${WITH} #1"
    mmv "${WHAT} *" "${WITH} #1"
    mmv "${WHAT}_*" "${WITH} #1"
    mmv "${UPPER} - *" "${WITH} #1"
    mmv "${UPPER} *" "${WITH} #1"
    mmv "${UPPER}_*" "${WITH} #1"
    mmv "${CAP} - *" "${WITH} #1"
    mmv "${CAP} *" "${WITH} #1"
    mmv "${CAP}_*" "${WITH} #1"
}

#BA : Bass
#ARP : Arpeggiated
#BR : Brass
#CH : Automatic Chords
#KY : Keys ( Not only EP, Organs and pianos, but chordal, played with standard keyboard techniques, stabs etc )
#LD : Leads ( Dance stuff as well as soloing/chorusing stuff, usually mono )
#PD : Pads
#ATM : Atmospheres, soundscapes
#WI : Winds, woodwinds
#OR : Orchestral ( Like Strings + Brass )
#ST : Strings
#SQ : Sequences ( Monophonic or Polyphonic ) and automatic lines
#FX : Effects
#PC : Percussions, including drums
#SY : Synths ( not obvious leads, bass or keys, pacds, etc )
#PL : Plucked, including guitarslike, keytars, harps, dulcimers etc

kasm_errors() {
    mmv -d "* .aupreset" "#1.aupreset" 
    mmv -d "] *.aupreset" "#1.aupreset" 
    mmv -d ") *.aupreset" "#1.aupreset"
    mmv -d "| *.aupreset" "#1.aupreset"
    mmv -d "• *.aupreset" "#1.aupreset"
    mmv -d "- *.aupreset" "#1.aupreset"
    mmv -d "\" *.aupreset" "#1.aupreset"
    mmv -d "\* *.aupreset" "#1.aupreset"
}

kasm_folders() {
    mmv --makedirs "40s Very Own - Drums - *" "DM 40s Very Own Drums/#1"
    mmv --makedirs "40s Very Own - Keys - *" "KY 40s Very Own Keys/#1"
    mmv --makedirs "Abbey Road 50s Drummer - *" "DM Abbey Road/50s Drummer/#1"
    mmv --makedirs "Abbey Road 60s Drummer - *" "DM Abbey Road/60s Drummer/#1"
    mmv --makedirs "Abbey Road 70s Drummer - *" "DM Abbey Road/70s Drummer/#1"
    mmv --makedirs "Abbey Road 80s Drummer - *" "DM Abbey Road/80s Drummer/#1"
    mmv --makedirs "Abbey Road Modern Drummer - *" "DM Abbey Road/Modern Drummer/#1"
    mmv --makedirs "Abbey Road Vintage Drummer - *" "DM Abbey Road/Vintage Drummer/#1"
    mmv --makedirs "Absynth 5 - *" "SY Absynth 5/#1"
    mmv --makedirs "Action Strikes - *" "FX Action Strikes/#1"
    mmv --makedirs "Action Strings 2 - *" "OC Action Strings/#1"
    mmv --makedirs "Alicias Keys - *" "KY Alicias Keys/#1"
    mmv --makedirs "Amati Viola - *" "OC Amati Viola/#1"
    mmv --makedirs "Amplified Funk - *" "FX Amplified Funk/#1"
    mmv --makedirs "Analog Dreams - *" "PD Analog Dreams/#1"
    mmv --makedirs "Anthology Strings - *" "OC Anthology Strings/#1"
    mmv --makedirs "Aquarius Earth - *" "PD Aquarius Earth/#1"
    mmv --makedirs "Ashlight - *" "PD Ashlight/#1"
    mmv --makedirs "Astral Flutter - *" "PD Astral Flutter/#1"
    mmv --makedirs "Atomic Pack - *" "SY Atomic Pack/#1"
    mmv --makedirs "Backyard Jams - *" "DM Backyard Jams/#1"
    mmv --makedirs "Balinese Gamelan - *" "KY Balinese Gamelan/#1"
    mmv --makedirs "Band - *" "OC Band/#1"
    mmv --makedirs "Basement Era - *" "FX Basement Era/#1"
    mmv --makedirs "Battery 4 Factory - *" "DM Battery 4/#1"
    mmv --makedirs "Beam - *" "FX Beam/#1"
    mmv --makedirs "Beats - *" "DM Beats/#1"
    mmv --makedirs "Blocks Base - *" "SY Blocks Base/#1"
    mmv --makedirs "Blocks Primes - *" "SY Blocks Primes/#1"
    mmv --makedirs "Body Mechanik - *" "FX Body Mechanik/#1"
    mmv --makedirs "Bounce - *" "FX Bounce/#1"
    mmv --makedirs "Bump - *" "FX Bump/#1"
    mmv --makedirs "Bumpin Flava - *" "FX Bumpin Flava/#1"
    mmv --makedirs "Butch Vig Drums - *" "DM Butch Vig Drums/#1"
    mmv --makedirs "Byte Riot - *" "FX Byte Riot/#1"
    mmv --makedirs "CAGE Bundle - *" "OC CAGE Bundle/#1"
    mmv --makedirs "Carbon Decay - *" "FX Carbon Decay/#1"
    mmv --makedirs "Caribbean Current - *" "FX Caribbean Current/#1"
    mmv --makedirs "Cavern Floor - *" "FX Cavern Floor/#1"
    mmv --makedirs "Century Ensemble Brass Bundle - *" "OC Century Ensemble/Brass Bundle/#1"
    mmv --makedirs "Century Ostinato Strings - *" "OC Century Ensemble/Ostinato Strings/#1"
    mmv --makedirs "Charge - *" "FX Charge/#1"
    mmv --makedirs "Cloud Supply - *" "FX Cloud Supply/#1"
    mmv --makedirs "Cuba - *" "OC Cuba/#1"
    mmv --makedirs "Damage - *" "DM Damage/#1"
    mmv --makedirs "Decoded Forms - *" "FX Decoded Forms/#1"
    mmv --makedirs "Deep Matter - *" "FX Deep Matter/#1"
    mmv --makedirs "Deep Solo Violin - *" "OC Deep Solo Violin/#1"
    mmv --makedirs "Deft Lines - *" "FX/Deft Lines/#1"
    mmv --makedirs "Dorico Example Projects - *" "Dorico Example Projects/#1"
    mmv --makedirs "Drive - *" "FX/Drive/#1"
    mmv --makedirs "Drop Squad - *" "FX Drop Squad/#1"
    mmv --makedirs "Drum Lab - *" "DM Drum Lab/#1"
    mmv --makedirs "Drum Lab - *" "DM Drum Lab/#1"
    mmv --makedirs "East Asia - *" "OC East Asia/#1"
    mmv --makedirs "Elastic Thump - *" "FX Elastic Thump/#1"
    mmv --makedirs "Emotive Strings - *" "OC Emotive Strings/#1"
    mmv --makedirs "Empire Breaks - *" "DM Empire Breaks/#1"
    mmv --makedirs "Ethereal Earth - *" "PAD - Ethereal Earth/#1"
    mmv --makedirs "Fade - *" "FX Fade/#1"
    mmv --makedirs "Faded Reels - *" "FX Faded Reels/#1"
    mmv --makedirs "Flesh - *" "FX Flesh/#1"
    mmv --makedirs "Form - *" "FX Form/#1"
    mmv --makedirs "Free Form - *" "FX Free Form/#1"
    mmv --makedirs "Garritan - *" "KY Garritan/#1"
    mmv --makedirs "George Duke Soul Treasures - *" "GT George Duke Soul Treasures/#1"
    mmv --makedirs "Glaze - *" "FX Glaze/#1"
    mmv --makedirs "Global Shake - *" "FX Global Shake/#1"
    mmv --makedirs "Golden Kingdom - *" "FX Golden Kingdom/#1"
    mmv --makedirs "Guarneri Violin - *" "OC Guarneri Violin/#1"
    mmv --makedirs "Halcyon Sky - *" "PD Halcyon Sky/#1"
    mmv --makedirs "Haze - *" "FX Haze/#1"
    mmv --makedirs "Hybrid Keys - *" "KY Hybrid Keys/#1"
    mmv --makedirs "Hybrid Tools 4 - *" "FX Hybrid Tools/#1"
    mmv --makedirs "Ignition Keys - *" "KY Ignition Keys/#1"
    mmv --makedirs "India - *" "OC India/#1"
    mmv --makedirs "Indigo Dust - *" "FX Indigo Dust/#1"
    mmv --makedirs "Infinite Escape - *" "FX Infinite Escape/#1"
    mmv --makedirs "Intimate Studio Strings - *" "OC Intimate Studio Strings/#1"
    mmv --makedirs "Jacob Collier Audience Choir - *" "VX Jacob Collier Audience Choir/#1"
    mmv --makedirs "Kinetic Metal - *" "FX Kinetic Metal/#1"
    mmv --makedirs "Kinetic Toys - *" "FX Kinetic Toys/#1"
    mmv --makedirs "Kinetic Treats - *" "FX Kinetic Treats/#1"
    mmv --makedirs "Kino - *" "FX Kino/#1"
    mmv --makedirs "Kontakt Factory - *" "#1"
    mmv --makedirs "Kontakt Factory 2 - *" "#1"
    mmv --makedirs "Kontakt Factory Selection - *" "#1"
    mmv --makedirs "Kontakt Instruments - *" "#1"
    mmv --makedirs "Kontakt - *" "#1"
    mmv --makedirs "Kontour - *" "Kontour/#1"
    mmv --makedirs "Lacrimosa Choir - *" "VX Lacrimosa Choir/#1"
    mmv --makedirs "Lazer Dice - *" "FX Lazer Dice/#1"
    mmv --makedirs "Lilac Glare - *" "FX Lilac Glare/#1"
    mmv --makedirs "Liquid Energy - *" "FX Liquid Energy/#1"
    mmv --makedirs "Lo-Fi Glow - *" "FX Lo-Fi Glow/#1"
    mmv --makedirs "London Grit - *" "FX London Grit/#1"
    mmv --makedirs "Lucid Mission - *" "FX Lucid Mission/#1"
    mmv --makedirs "Magnetic Coast - *" "FX Magnetic Coast/#1"
    mmv --makedirs "Majestica Professional - *" "FX Majestica Professional/#1"
    mmv --makedirs "Mallet Flux - *" "KY Mallet Flux/#1"
    mmv --makedirs "Marble Rims - *" "FX Marble Rims/#1"
    mmv --makedirs "Massive X - *" "SY Massive X/#1"
    mmv --makedirs "Massive X Factory - *" "SY Massive X/#1"
    mmv --makedirs "Massive - *" "SY Massive/#1"
    mmv --makedirs "Mechanix - *" "FX Mechanix/#1"
    mmv --makedirs "Melda - *" "FX Melda/#1"
    mmv --makedirs "Melted Vibes - *" "FX Melted Vibes/#1"
    mmv --makedirs "Middle East - *" "OC Middle East/#1"
    mmv --makedirs "Mikro Prism - *" "FX Mikro Prism/#1"
    mmv --makedirs "Modular Icons - *" "SY Modular Icons/#1"
    mmv --makedirs "Moebius - *" "FX Moebius/#1"
    mmv --makedirs "Molten Veil - *" "FX Molten Veil/#1"
    mmv --makedirs "Monark - *" "SY Monark/#1"
    mmv --makedirs "Mother Board - *" "FX Mother Board/#1"
    mmv --makedirs "Mysteria - *" "FX Mysteria/#1"
    mmv --makedirs "Neo Boogie - *" "DM Neo Boogie/#1"
    mmv --makedirs "Neon Drive - *" "FX Neon Drive/#1"
    mmv --makedirs "Nocturnal State - *" "FX Nocturnal State/#1"
    mmv --makedirs "Noire - *" "KY Piano Noire/#1"
    mmv --makedirs "Ondes Martenot - *" "FX Theramin/#1"
    mmv --makedirs "Our House - *" "FX Our House/#1"
    mmv --makedirs "Pharlight - *" "PD Pharlight/#1"
    mmv --makedirs "Platinum Bounce - *" "FX Platinum Bounce/#1"
    mmv --makedirs "Play Series Selection - *" "FX Play Series/#1"
    mmv --makedirs "Playbox - *" "FX Playbox/#1"
    mmv --makedirs "Polyplex - *" "FX Polyplex/#1"
    mmv --makedirs "Prismatic Bliss - *" "FX Prismatic Bliss/#1"
    mmv --makedirs "Pulse - *" "FX Pulse/#1"
    mmv --makedirs "Pure Drip - *" "FX Pure Drip/#1"
    mmv --makedirs "Queensbridge Story - *" "FX Queensbridge Story/#1"
    mmv --makedirs "Quest - *" "FX Quest/#1"
    mmv --makedirs "Reaktor 6 - *" "SY Reaktor 6/#1"
    mmv --makedirs "Reaktor Factory - *" "SY Reaktor/#1"
    mmv --makedirs "Reaktor Factory Selection R2 - *" "SY Reaktor/#1"
    mmv --makedirs "Reaktor Prism - *" "SY Reaktor Prism/#1"
    mmv --makedirs "Reaktor Spark R2 - *" "SY Reaktor Spark R2/#1"
    mmv --makedirs "Requiem Light - *" "VX Requiem/#1"
    mmv --makedirs "Requiem Professional - *" "VX Requiem/#1"
    mmv --makedirs "Retro Machines Mk2 - *" "SY Retro Machines/#1"
    mmv --makedirs "Rhythm Source - *" "DM Rhythm Source/#1"
    mmv --makedirs "Rise and Hit - *" "FX Rise and Hit/#1"
    mmv --makedirs "Rising Crescent - *" "FX Rising Crescent/#1"
    mmv --makedirs "Rounds - *" "FX Rounds/#1"
    mmv --makedirs "Rush - *" "FX Rush/#1"
    mmv --makedirs "Sasha - *" "FX Sasha/#1"
    mmv --makedirs "Scarbee A-200 - *" "KY Scarbee A-200/#1"
    mmv --makedirs "Scarbee Clavinet Pianet - *" "KY Scarbee Clavinet Pianet/#1"
    mmv --makedirs "Scarbee Jay-Bass - *" "BA Scarbee Jay-Bass/#1"
    mmv --makedirs "Scarbee MM-Bass Amped - *" "BA Scarbee MM-Bass/#1"
    mmv --makedirs "Scarbee MM-Bass - *" "BA Scarbee MM-Bass/#1"
    mmv --makedirs "Scarbee Mark I - *" "KY Scarbee Mark I/#1"
    mmv --makedirs "Scarbee Pre-Bass Amped - *" "BA Scarbee Pre-Bass/#1"
    mmv --makedirs "Scarbee Pre-Bass - *" "BA Scarbee Pre-Bass/#1"
    mmv --makedirs "Scarbee Rickenbacker Bass - *" "BA Scarbee Rickenbacker Bass/#1"
    mmv --makedirs "Scene - *" "FX Scene/#1"
    mmv --makedirs "SemanticDanielou - *" "FX SemanticDanielou/#1"
    mmv --makedirs "Sequis - *" "FX Sequis/#1"
    mmv --makedirs "Session Bassist - Prime Bass - *" "BA Session Bassist/Prime Bass/#1"
    mmv --makedirs "Session Guitarist - Electric Mint - *" "GT Session Guitarist/Electric Mint/#1"
    mmv --makedirs "Session Guitarist - Electric Sunburst Deluxe - *" "GT Session Guitarist/Electric Sunburst Deluxe/#1"
    mmv --makedirs "Session Guitarist - Electric Sunburst - *" "GT Session Guitarist/Electric Sunburst/#1"
    mmv --makedirs "Session Guitarist - Electric Vintage - *" "GT Session Guitarist/Electric Vintage/#1"
    mmv --makedirs "Session Guitarist - Picked Acoustic - *" "GT Session Guitarist/Picked Acoustic/#1"
    mmv --makedirs "Session Guitarist - Picked Nylon - *" "GT Session Guitarist/Picked Nylon/#1"
    mmv --makedirs "Session Guitarist - Strummed Acoustic 2 - *" "GT Session Guitarist/Strummed Acoustic/#1"
    mmv --makedirs "Session Guitarist - Strummed Acoustic - *" "GT Session Guitarist/Strummed Acoustic/#1"
    mmv --makedirs "Session Horns - *" "OC Session Horns/#1"
    mmv --makedirs "Session Horns Pro - *" "OC Session Horns Pro/#1"
    mmv --makedirs "Session Strings 2 - *" "OC Session Strings 2/#1"
    mmv --makedirs "Session Strings Pro 2 - *" "OC Session Strings Pro 2/#1"
    mmv --makedirs "Skanner XT - *" "FX Skanner XT/#1"
    mmv --makedirs "Solar Breeze - *" "FX Solar Breeze/#1"
    mmv --makedirs "Soul Magic - *" "FX Soul Magic/#1"
    mmv --makedirs "Soul Sessions - *" "FX Soul Sessions/#1"
    mmv --makedirs "Soundiron Didgeridoos - *" "OC Didgeridoos/#1"
    mmv --makedirs "Spectrum Quake - *" "FX Spectrum Quake/#1"
    mmv --makedirs "Spitfire - *" "OC Spitfire/#1"
    mmv --makedirs "Spitfire Audio - Olafur Arnalds Composer Toolkit - *" "OC Olafur Arnalds/Composer Toolkit/#1"
    mmv --makedirs "Spitfire Olafur Arnalds Chamber Evolutions - *" "OC Olafur Arnalds/Chamber Evolutions/#1"
    mmv --makedirs "Stacks - *" "FX Stacks/#1"
    mmv --makedirs "Stadium Flex - *" "FX Stadium Flex/#1"
    mmv --makedirs "Straylight - *" "PD Straylight/#1"
    mmv --makedirs "Studio Drummer - *" "DM Studio Drummer/#1"
    mmv --makedirs "Sunvox - *" "FX Sunvox/#1"
    mmv --makedirs "Super 8 - *" "SY Super 8/#1"
    mmv --makedirs "TRK-01 - *" "BA TRK-01/#1"
    mmv --makedirs "TRK-01 Bass - *" "BA TRK-01 Bass/#1"
    mmv --makedirs "TRK-01 Kick - *" "DM TRK-01 Kick/#1"
    mmv --makedirs "The Finger R2 - *" "KY The Finger/#1"
    mmv --makedirs "The Gentleman - *" "KY Piano The Gentleman/#1"
    mmv --makedirs "The Giant - *" "KY Piano The Giant/#1"
    mmv --makedirs "The Grandeur - *" "KY Piano The Grandeur/#1"
    mmv --makedirs "The Maverick - *" "KY Piano The Maverick/#1"
    mmv --makedirs "The Mouth - *" "FX The Mouth/#1"
    mmv --makedirs "Thrill - *" "FX Thrill/#1"
    mmv --makedirs "Toll - *" "OC Toll/#1"
    mmv --makedirs "True School - *" "FX True School/#1"
    mmv --makedirs "Una Corda - *" "KY Piano Una Corda/#1"
    mmv --makedirs "Velvet Lounge - *" "FX Velvet Lounge/#1"
    mmv --makedirs "Vintage Organs - *" "KY Vintage Organs/#1"
    mmv --makedirs "Wake - *" "FX Wake/#1"
    mmv --makedirs "Warped Symmetry - *" "FX Warped Symmetry/#1"
    mmv --makedirs "West Africa - *" "OC West Africa/#1"
}

kasm_names() {
    mmv "ELS_*" "#1"
    mmv "AOKI_serum_*" "#1"

    replacer "lead" "LD"
    replacer "ld" "LD"

    replacer "fx" "FX"
    replacer "sfx" "FX"

    replacer "bass" "BA"
    replacer "ba" "BA"

    replacer "arp" "ARP"

    replacer "synth" "SY"
    replacer "syn" "SY"
    replacer "sy" "SY"

    replacer "pluck" "PL"
    replacer "pl" "PL"

    replacer "keys" "KY"
    replacer "key" "KY"
    replacer "ky" "KY"

    replacer "pad" "PD"
    replacer "pd" "PD"

    replacer "drum" "DM"

    mmv "REESE BASS - *" "BA Reese #1"
    mmv "808 - *" "BA 808 #1"
    mmv "ACID - *" "BA Acid #1"
    mmv "Flute *" "OC Flute #1"
    mmv "Oboe *" "OC Oboe #1"
    mmv "String*" "OC String#1"

}

duplicates "aupreset"
duplicates "adg"
kasm_errors
kasm_folders
kasm_names

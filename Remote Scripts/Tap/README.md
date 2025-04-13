# Tap
Version: 1.1

An Ableton Live MIDI remote script for the iOS app 7III Tap by project7III.

More info: https://project7iii.com/tap

## 1. Add the Tap MIDI Remote Script
1. Manually create a folder called `Remote Scripts` within your User Library if it does not already exist. The default User Library locations are:

   - **Windows:** `\Users\[username]\Documents\Ableton\User Library`
   - **Mac:** `Macintosh HD/Users/[username]/Music/Ableton/User Library`
   
2. Place the remote script folder called `Tap` (the folder you found this README.md in) into the `Remote Scripts` folder you just created.

## 2. Connect your Device
Note: If you have a Mac, MIDI over USB is the best way to connect your iPhone or iPad to Live. If you are never using MIDI over WiFi, you can disable `MIDI over WiFi enabled` in options.

### Over USB (Mac Only)
1. Connect your device to your Mac using a USB cable.
2. Open the app **Audio MIDI Setup**.
3. Open the `Audio Devices` window.  
   → If it is not already visible, select the `Window` → `Audio Devices` menu to display it.
4. Find your iOS device in the sidebar and click the `Enable` button.

### Over WiFi
1. Connect your device to the same WiFi as your computer (best would be an ad hoc WiFi network).
2. Configure RTP-MIDI:

   **Windows**
   1. Download [rtpMIDI](https://www.tobias-erichsen.de/wp-content/uploads/2020/01/rtpMIDISetup_1_1_14_247.zip).
   2. Follow this [guide](https://www.tobias-erichsen.de/software/rtpmidi/rtpmidi-tutorial.html) to install rtpMIDI and connect your device (no **Advanced Configuration** necessary).

   **Mac**
   1. Simply follow this [guide](https://support.apple.com/en-ca/guide/audio-midi-setup/ams1012/mac) (no need to do **Step 9**).

## 3. Set Up Live
1. Launch Live.
2. Open Live's Preferences and navigate to the **MIDI** tab.
3. Select the script `Tap` using the dropdown menu in the Control Surface column.
4. Assign your device or Network Session as input and output ports.
5. Activate `Track` and `Remote` for your active MIDI Ports.
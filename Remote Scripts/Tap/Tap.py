# 7III Tap

from __future__ import with_statement
import Live
from _Framework.ControlSurface import ControlSurface
from _Framework.MixerComponent import MixerComponent
from _Framework.TransportComponent import TransportComponent
from _Framework.SessionComponent import SessionComponent
from _Framework.EncoderElement import *
from _Framework.ButtonElement import ButtonElement
from _Framework.SliderElement import SliderElement
from _Framework.InputControlElement import MIDI_NOTE_TYPE, MIDI_NOTE_ON_STATUS, MIDI_NOTE_OFF_STATUS, MIDI_CC_TYPE
from _Framework.DeviceComponent import DeviceComponent
from ableton.v2.base import listens, liveobj_valid, liveobj_changed

import time
import threading
import random
from itertools import zip_longest


mixer, transport, session_component = None, None, None
quantize_grid_value = 5
quantize_strength_value = 1.0
swing_amount_value = 0.0


class Tap(ControlSurface):

    def __init__(self, c_instance):
        ControlSurface.__init__(self, c_instance)
        with self.component_guard():
            global mixer
            global transport
            global session_component
            self.mixer_status = False
            self.mixer_reset = True
            self.device_status = True
            track_count = 127
            return_count = 12  # Maximum of 12 Sends and 12 Returns
            max_clip_slots = 800  # Adjust this number based on your needs
            self.playing_position_listeners = [None] * max_clip_slots
            self.current_clip_notes = []
            self.current_clip = None
            self.last_raw_notes = None
            self.currently_playing_notes = [False] * 128
            self.last_playing_position = 0.0
            mixer = MixerComponent(track_count, return_count)
            transport = TransportComponent()
            session_component = SessionComponent()
            self.old_clips_array = []

            self.was_initialized = False
            # connection check button
            connection_check_button = ButtonElement(1, MIDI_NOTE_TYPE, 15, 94)
            connection_check_button.add_value_listener(self._connection_established)
            # send project again button
            send_project_button = ButtonElement(1, MIDI_NOTE_TYPE, 15, 88)
            send_project_button.add_value_listener(self._send_project)

    def _setup_device_control(self):
        self._device = DeviceComponent()
        self._device.name = 'Device_Component'
        device_controls = []
        for index in range(8):
            control = EncoderElement(MIDI_CC_TYPE, 8, 72 + index, Live.MidiMap.MapMode.absolute)
            control.name = 'Ctrl_' + str(index)
            device_controls.append(control)
        self._device.set_parameter_controls(device_controls)
        nav_left_button = ButtonElement(1, MIDI_CC_TYPE, 0, 33)
        nav_right_button = ButtonElement(1, MIDI_CC_TYPE, 0, 32)
        self._device.set_bank_nav_buttons(nav_left_button, nav_right_button)
        self._on_device_changed.subject = self._device
        self.set_device_component(self._device)
        # Register button listeners for navigation buttons
        nav_left_button.add_value_listener(self._on_nav_button_pressed)
        nav_right_button.add_value_listener(self._on_nav_button_pressed)

    def _on_nav_button_pressed(self, value):
        if value:
            self._on_device_changed()

    def _find_drum_rack_in_track(self, track):
        for device in track.devices:
            if device.can_have_drum_pads:
                return device
            elif isinstance(device, Live.RackDevice.RackDevice):
                # If the device is a RackDevice (e.g., Instrument Rack), recursively search inside its chains
                for chain in device.chains:
                    drum_rack = self._find_drum_rack_in_track(chain)
                    if drum_rack is not None:
                        return drum_rack
        return None

    @subject_slot('device')
    def _on_device_changed(self):
        if liveobj_valid(self._device):
            # device = self._device.device()  # Retrieve the Device object
            # get and send name of bank and device
            selected_track = self.song().view.selected_track
            selected_device = selected_track.view.selected_device
            # device_name = selected_device.name
            available_devices = selected_track.devices
            # find out if track has a drum rack.
            track_has_drums = 0
            drum_rack_device = self._find_drum_rack_in_track(selected_track)
            if drum_rack_device is not None:
                track_has_drums = 1

            # find index of device
            selected_device_index = self._find_device_index(selected_device, available_devices)
            # self.log_message("Selected Device Index: {}".format(selected_device_index))
            # bank names, list and if has drum
            bank_name_drum = self._device._bank_name + ";" + str(track_has_drums)
            bank_names_list = ','.join(str(name) for name in self._device._parameter_bank_names())
            # sending sysex of bank name, device name, bank names
            self._send_sys_ex_message(bank_name_drum, 0x6D)
            self._send_sys_ex_message(bank_names_list, 0x5D)
            # sending the index instead of name for device.
            self._send_sys_ex_message(selected_device_index, 0x4D)
            # Get all available devices of the selected track
            available_devices = [device.name for device in selected_track.devices]
            available_devices_string = ','.join(available_devices)
            # self.log_message("devices: {}".format(available_devices))
            self._send_sys_ex_message(available_devices_string, 0x01)

            if hasattr(selected_device, 'parameters') and selected_device.parameters:
                # TODO: make this prettier!
                parameter_names = [control.mapped_parameter().name if control.mapped_parameter() else ""
                                for control in self._device._parameter_controls]
                parameter_names = [name for name in parameter_names if name]  # Remove empty names
                if parameter_names:
                    # self.log_message("Parameter Names: {}".format(parameter_names))
                    # send a MIDI SysEx message with the names
                    self._send_parameter_names(parameter_names)
                else:
                    parameter_names = ""
                    self._send_parameter_names(parameter_names)
            else:
                parameter_names = ""
                self._send_parameter_names(parameter_names)
        else:
            # no device
            # sending sysex of bank name, device name, bank names
            bank_name_drum = ";0"
            bank_names_list = ""
            available_devices_string = ""
            parameter_names = ""
            self._send_sys_ex_message(bank_name_drum, 0x6D)
            self._send_sys_ex_message(bank_names_list, 0x5D)
            self._send_sys_ex_message(available_devices_string, 0x01)
            self._send_parameter_names(parameter_names)

    def _find_device_index(self, device, device_list):
        for index, d in enumerate(device_list):
            if device == d:
                return str(index)
        return "not found"  # Device not found

    def _send_parameter_names(self, parameter_names):
        if parameter_names == "":
            name_string = ""
        else:
            name_string = ','.join(parameter_names)
        self._send_sys_ex_message(name_string, 0x7D)

    def _send_sys_ex_message(self, name_string, manufacturer_id):
        status_byte = 0xF0  # SysEx message start
        end_byte = 0xF7  # SysEx message end
        device_id = 0x01
        data = name_string.encode('ascii')
        max_chunk_length = 250
        if len(data) <= max_chunk_length:
            sys_ex_message = (status_byte, manufacturer_id, device_id) + tuple(data) + (end_byte, )
            self._send_midi(sys_ex_message)
        else:
            num_of_chunks = (len(data) + max_chunk_length - 1) // max_chunk_length
            for chunk_index in range(num_of_chunks):
                start_index = chunk_index * max_chunk_length
                end_index = start_index + max_chunk_length
                prefix = "$"
                if chunk_index == num_of_chunks - 1:
                    prefix = "_"
                chunk_data = prefix.encode('ascii') + data[start_index:end_index]

                sys_ex_message = (status_byte, manufacturer_id, device_id) + tuple(chunk_data) + (end_byte, )
                self._send_midi(sys_ex_message)

    def _initialize_buttons(self):
        transport.set_play_button(ButtonElement(1, MIDI_CC_TYPE, 0, 118))
        transport.set_stop_button(ButtonElement(1, MIDI_CC_TYPE, 0, 117))
        transport.set_metronome_button(ButtonElement(1, MIDI_CC_TYPE, 0, 58))
        session_component.set_stop_all_clips_button(ButtonElement(1, MIDI_NOTE_TYPE, 15, 96))
        self.capture_button = ButtonElement(True, MIDI_NOTE_TYPE, 15, 100)
        self.capture_button.add_value_listener(self._capture_button_value)
        self.quantize_button = ButtonElement(True, MIDI_NOTE_TYPE, 15, 99)
        self.quantize_button.add_value_listener(self._quantize_button_value)
        # duplicate the active clip to a free slot
        self.duplicate_button = ButtonElement(True, MIDI_NOTE_TYPE, 15, 98)
        self.duplicate_button.add_value_listener(self._duplicate_button_value)
        # duplicate scene
        self.duplicate_scene_button = ButtonElement(True, MIDI_NOTE_TYPE, 15, 95)
        self.duplicate_scene_button.add_value_listener(self._duplicate_scene_button_value)
        # a session recording button
        self.sesh_record_button = ButtonElement(1, MIDI_CC_TYPE, 0, 119)
        self.sesh_record_button.add_value_listener(self._sesh_record_value)
        # quantize grid size button
        quantize_grid_button = ButtonElement(1, MIDI_CC_TYPE, 1, 0)
        quantize_grid_button.add_value_listener(self._quantize_grid_value)
        # quantize strength
        quantize_strength_button = ButtonElement(1, MIDI_CC_TYPE, 1, 1)
        quantize_strength_button.add_value_listener(self._quantize_strength_value)
        # swing percentage button
        swing_amount_button = ButtonElement(1, MIDI_CC_TYPE, 1, 2)
        swing_amount_button.add_value_listener(self._swing_amount_value)
        # # periodic check
        # periodic_check_button = ButtonElement(1, MIDI_NOTE_TYPE, 15, 97)
        # periodic_check_button.add_value_listener(self._periodic_check)
        # redo button
        self.redo_button = ButtonElement(1, MIDI_NOTE_TYPE, 15, 102)
        self.redo_button.add_value_listener(self._redo_button_value)
        # undo button
        self.undo_button = ButtonElement(1, MIDI_NOTE_TYPE, 15, 101)
        self.undo_button.add_value_listener(self._undo_button_value)
        # device selection
        device_selection_button = ButtonElement(1, MIDI_CC_TYPE, 1, 3)
        device_selection_button.add_value_listener(self._select_device_by_index)
        # track selection
        track_selection_button = ButtonElement(1, MIDI_CC_TYPE, 1, 4)
        track_selection_button.add_value_listener(self._select_track_by_index)
        # return and master track selection
        return_track_selection_button = ButtonElement(1, MIDI_CC_TYPE, 1, 5)
        return_track_selection_button.add_value_listener(self._select_return_track_by_index)
        # scene launch
        scene_launch_button = ButtonElement(1, MIDI_CC_TYPE, 1, 14)
        scene_launch_button.add_value_listener(self._fire_scene)
        # clip / scene select
        clip_scene_select_button = ButtonElement(1, MIDI_CC_TYPE, 1, 15)
        clip_scene_select_button.add_value_listener(self._select_clip_scene)
        # scene delete
        scene_delete_button = ButtonElement(1, MIDI_CC_TYPE, 1, 16)
        scene_delete_button.add_value_listener(self._delete_scene)
        # random device add button
        random_device_button = ButtonElement(1, MIDI_NOTE_TYPE, 15, 93)
        random_device_button.add_value_listener(self._add_random_sound)
        # random audio effect button
        random_effect_button = ButtonElement(1, MIDI_NOTE_TYPE, 15, 92)
        random_effect_button.add_value_listener(self._add_random_effect)
        # random synth button
        random_synth_button = ButtonElement(1, MIDI_NOTE_TYPE, 15, 103)
        random_synth_button.add_value_listener(self._add_random_synth)
        # random drums button
        random_drums_button = ButtonElement(1, MIDI_NOTE_TYPE, 15, 104)
        random_drums_button.add_value_listener(self._add_random_drums)
        # delete device button
        delete_device_button = ButtonElement(1, MIDI_CC_TYPE, 1, 17)
        delete_device_button.add_value_listener(self._delete_device)
        # move device left
        move_device_left_button = ButtonElement(1, MIDI_CC_TYPE, 1, 18)
        move_device_left_button.add_value_listener(self._move_device_left)
        # move device right
        move_device_right_button = ButtonElement(1, MIDI_CC_TYPE, 1, 19)
        move_device_right_button.add_value_listener(self._move_device_right)
        # add midi track
        add_midi_track_button = ButtonElement(1, MIDI_CC_TYPE, 1, 21)
        add_midi_track_button.add_value_listener(self._add_midi_track)
        # delete midi track
        delete_midi_track_button = ButtonElement(1, MIDI_CC_TYPE, 1, 22)
        delete_midi_track_button.add_value_listener(self._delete_midi_track)
        # add return track
        add_return_track_button = ButtonElement(1, MIDI_NOTE_TYPE, 15, 91)
        add_return_track_button.add_value_listener(self._add_return_track)
        # delete return track
        delete_return_track_button = ButtonElement(1, MIDI_CC_TYPE, 1, 23)
        delete_return_track_button.add_value_listener(self._delete_return_track)
        # mixer view status
        mixer_view_status = ButtonElement(1, MIDI_NOTE_TYPE, 15, 90)
        mixer_view_status.add_value_listener(self._update_mixer_status)
        # device view status
        device_view_status = ButtonElement(1, MIDI_NOTE_TYPE, 15, 89)
        device_view_status.add_value_listener(self._update_device_status)

    def send_note_on(self, note_number, channel, velocity):
        channel_byte = channel & 0x7F
        note_byte = note_number & 0x7F
        velocity_byte = velocity & 0x7F
        midi_note_on_message = (0x90 | channel_byte, note_byte, velocity_byte)
        self._send_midi(midi_note_on_message)

    def send_note_off(self, note_number, channel, velocity):
        channel_byte = channel & 0x7F
        note_byte = note_number & 0x7F
        velocity_byte = velocity & 0x7F
        midi_note_off_message = (0x80 | channel_byte, note_byte, velocity_byte)
        self._send_midi(midi_note_off_message)

    def _connection_established(self, value):
        if value:            
            self.log_message("Connection App to Ableton (still) works!")
            # send midi note on channel 3, note number 1 to confirm handshake
            midi_event_bytes = (0x90 | 0x03, 0x01, 0x64)
            self._send_midi(midi_event_bytes)
            
            # initializing everything else if this is not just the handshake
            if self.was_initialized is False:
                self.was_initialized = True
                self.old_clips_array = []
                self._on_tracks_changed()
                song = self.song()
                self._initialize_buttons()
                self._update_mixer_and_tracks()
                self._set_selected_track_implicit_arm()
                selected_track = song.view.selected_track
                self._send_selected_track_index(selected_track)
                self._on_selected_track_changed.subject = song.view
                # updating scale
                self._on_scale_changed()

                # track = self.song().view.selected_track
                # track.view.add_selected_device_listener(self._on_selected_device_changed)
                song.add_tracks_listener(self._on_tracks_changed)  # hier für return tracks: .add_return_tracks_listener()
                # self.song().view.add_selected_scene_listener(self._on_selected_scene_changed)
                song.add_scale_name_listener(self._on_scale_changed)
                song.add_root_note_listener(self._on_scale_changed)
                self._setup_device_control()
                self._register_clip_listeners()
                self.periodic_timer = 1
                self._periodic_execution()

    def _send_project(self, value):
        if value:
            self.old_clips_array = []
            self._update_mixer_and_tracks()
            self._update_clip_slots()
    
    def _periodic_execution(self):
        self._periodic_check()
        if self.periodic_timer == 1:
            threading.Timer(0.3, self._periodic_execution).start()

    def _periodic_check(self):
        # update clip slots
        # we only need to update clip slots periodically when we are in clip slots view
        if self.device_status is False and self.mixer_status is False:
            self._update_clip_slots()

    def _redo_button_value(self, value):
        if value != 0:
            song = self.song()
            if song.can_redo:
                song.redo()
                # self._periodic_check()

    def _undo_button_value(self, value):
        if value != 0:
            song = self.song()
            if song.can_undo:
                song.undo()
                # self._periodic_check()

    def _sesh_record_value(self, value):
        if value != 0:
            record = self.song().session_record
            if record == False:
                self.song().session_record = True
            else:
                self.song().session_record = False

    def _capture_button_value(self, value):
        if value != 0:
            self.song().capture_midi()

    def _quantize_grid_value(self, value):
        global quantize_grid_value
        quantize_grid_value = value

    def _quantize_strength_value(self, value):
        global quantize_strength_value
        quantize_strength_value = value / 100.0

    def _swing_amount_value(self, value):
        global swing_amount_value
        # 100% swing amount did strange things, so I went down to 10% max
        swing_amount_value = value / 1000.0

    def _quantize_button_value(self, value):
        if value != 0:
            clip = self.song().view.detail_clip
            if clip:
                # need to set the swing amount first (0.00-1.00)
                self.song().swing_amount = swing_amount_value
                # grid (int 1 == 1/4, 2 == 1/8, 5 == 1/16, 8 = 1/32), strength (0.50 == 50%)
                clip.quantize(quantize_grid_value, quantize_strength_value)

    def _duplicate_button_value(self, value):
        if value != 0:
            self._duplicate_clip()

    def _duplicate_scene_button_value(self, value):
        if value != 0:
            song = self.song()
            selected_scene = song.view.selected_scene
            all_scenes = song.scenes
            current_index = list(all_scenes).index(selected_scene)
            song.duplicate_scene(current_index)

    def _duplicate_clip(self):
        song = self.song()
        selected_track = song.view.selected_track

        if selected_track is None:
            return

        selected_scene = song.view.selected_scene
        all_scenes = song.scenes
        scene_index = list(all_scenes).index(selected_scene)
        track_index = list(song.tracks).index(selected_track)
        destination_scene_index = len(all_scenes)

        # checking if clip was playing
        was_playing = song.view.highlighted_clip_slot.is_playing == 1

        # check if there is a free clip slot after the current clip
        for index, clip_slot in enumerate(selected_track.clip_slots):
            if index <= scene_index:
                continue
            if clip_slot.has_clip:
                continue
            destination_scene_index = index
            break

        if destination_scene_index == len(all_scenes):
            # create a new scene if there is no free slot after the current slot
            song.create_scene(-1)

        self._copy_paste_clip(track_index, scene_index, track_index, destination_scene_index)

        # select newly created clip
        song.view.selected_scene = song.scenes[destination_scene_index]
        # fire the new clip if the old clip was playing
        if was_playing:
            song.view.highlighted_clip_slot.fire(force_legato=True)

    @subject_slot('selected_track')
    def _on_selected_track_changed(self):
        selected_track = self.song().view.selected_track
        track_has_midi_input = 0
        if selected_track and selected_track.has_midi_input:
            self._set_selected_track_implicit_arm()
            track_has_midi_input = 1
        self._set_up_notes_playing(selected_track)
        # update device thing when we have no device on the selected track
        # TODO: check if wee need this!
        if selected_track.has_midi_output or not selected_track.has_midi_input:
            self._on_device_changed()
        self._set_other_tracks_implicit_arm()
        # send new index of selected track
        self._send_selected_track_index(selected_track)
        self._on_selected_scene_changed()
        # send sys ex of track midi input status.
        self._send_sys_ex_message(str(track_has_midi_input), 0x0B)
        # TODO: this part doesn't seem to work? how can I make this work with master and return?
        device_to_select = selected_track.view.selected_device
        if device_to_select is None and len(selected_track.devices) > 0:
            device_to_select = selected_track.devices[0]
        if device_to_select is not None:
            self.song().view.select_device(device_to_select)
        self._device_component.set_device(device_to_select)

    def _set_up_notes_playing(self, selected_track):
        if selected_track != "clip":
            # remove old clip playing position listeners
            for track in self.song().tracks:
                if track != selected_track:
                    for (clip_index, clip_slot) in enumerate(track.clip_slots):
                        if clip_slot is not None and clip_slot.has_clip:
                            if clip_slot.clip.playing_position_has_listener(self.playing_position_listeners[clip_index]):
                                # self.log_message("removing pos listener: {}".format(clip_index))
                                clip_slot.clip.remove_playing_position_listener(self.playing_position_listeners[clip_index])
        else:
            selected_track = self.song().view.selected_track

        if selected_track.has_midi_input:
            for (clip_index, clip_slot) in enumerate(selected_track.clip_slots):
                if clip_slot is not None and clip_slot.has_clip:
                    if not clip_slot.clip.playing_position_has_listener(self.playing_position_listeners[clip_index]):
                        # self.log_message("adding pos listener: {}".format(clip_index))
                        listener = lambda index=clip_index: self._clip_pos_changed(index)
                        self.playing_position_listeners[clip_index] = listener
                        clip_slot.clip.add_playing_position_listener(listener)

    def _clip_pos_changed(self, clip_index):
        # Only check and send things if we are in device view
        if self.device_status:
            selected_track = self.song().view.selected_track

            if clip_index < len(selected_track.clip_slots):
                clip_slot = selected_track.clip_slots[clip_index]

                if clip_slot is not None and clip_slot.has_clip:
                    clip_playing = clip_slot.clip
                    
                    start_time = clip_playing.start_marker
                    time_span = clip_playing.length

                    try:
                        # Get all the notes in the clip
                        current_raw_notes = clip_playing.get_notes_extended(0, 128, start_time, time_span)

                        # if the current clip has different notes save the new notes.
                        if current_raw_notes != self.last_raw_notes:
                            self.last_raw_notes = current_raw_notes

                            # Reset the current clip notes array
                            self.current_clip_notes = []
                            # add all the notes to the array
                            for midi_note in current_raw_notes:
                                pitch = midi_note.pitch
                                duration = midi_note.duration
                                start_time = midi_note.start_time
                                # Process note properties as needed
                                # self.log_message("Note: Pitch {}, Start Time {}, Duration {}".format(pitch, start_time, duration))
                                end_time = start_time + duration
                                self.current_clip_notes.append([pitch, start_time, end_time])

                        # check which notes are playing at position
                        # if we detect changes send them out to app
                        clip_position = clip_playing.playing_position

                        # making sure we have the right starting position
                        if self.last_playing_position > clip_position:
                            loop_start = clip_playing.loop_start
                            if clip_position >= loop_start:
                                self.last_playing_position = loop_start
                            else:
                                self.last_playing_position = clip_playing.start_marker

                        # check if currently playing notes are still playing in this playing position
                        for (note_index, is_playing) in enumerate(self.currently_playing_notes):
                            if is_playing:
                                # Initialize a flag to indicate if a playing note was found
                                found_playing_note = False

                                # Find the notes that stopped playing in since the last update
                                for note in self.current_clip_notes:
                                    pitch, start_time, end_time = note

                                    if start_time <= self.last_playing_position and clip_position < end_time and pitch == note_index:
                                        # Note is still playing
                                        found_playing_note = True
                                        break

                                # If no playing note was found, update the state
                                if not found_playing_note:
                                    self.currently_playing_notes[note_index] = False
                                    # send note off for note_index note.
                                    # self.log_message("Note off: {}".format(note_index))
                                    self.send_note_off(note_index, 0, 100)

                        # check current clip notes array which notes are on for that playing position
                        for note in self.current_clip_notes:
                            pitch, start_time, end_time = note
                            if self.last_playing_position <= start_time <= clip_position:
                                # note starts playing
                                self.currently_playing_notes[pitch] = True
                                # send midi note on
                                # self.log_message("Note on: {}".format(pitch))
                                self.send_note_on(pitch, 0, 100)
                        # update last playing position
                        self.last_playing_position = clip_position
                    except:
                        pass
                # else:
                    # self.log_message("No valid clip in the slot.")

    def _send_selected_track_index(self, selected_track):
        track_list = self.song().tracks
        track_index = self._find_track_index(selected_track, track_list)
        self._send_sys_ex_message(track_index, 0x03)
        if track_index == "not found":
            return_tracks_list = self.song().return_tracks
            return_track_index = self._find_track_index(selected_track, return_tracks_list)
            if return_track_index == "not found":
                return_track_index = str(len(return_tracks_list))
            self._send_sys_ex_message(return_track_index, 0x08)
        else:
            self._send_sys_ex_message("none selected", 0x08)

    def _find_track_index(self, track, track_list):
        for index, t in enumerate(track_list):
            if track == t:
                return str(index)
        return "not found" # Track not found

    def _select_device_by_index(self, value):
        # self.log_message("Setting new device Index: {}".format(value))
        device_to_select = self.song().view.selected_track.devices[value]
        self.song().view.select_device(device_to_select)

    def _select_track_by_index(self, track_index):
        # self.log_message("Getting track: {}".format(track_index))
        song = self.song()
        if track_index >= 0 and track_index < len(song.tracks):
            song.view.selected_track = song.tracks[track_index]
        else:
            self.log_message("Invalid track index: {}".format(track_index))

    def _select_return_track_by_index(self, track_index):
        song = self.song()
        if track_index < len(song.return_tracks):
            return_track = song.return_tracks[track_index] 
            song.view.selected_track = return_track
        else:
            master_track = song.master_track 
            song.view.selected_track = master_track

    def _set_selected_track_implicit_arm(self):
        selected_track = self.song().view.selected_track
        if selected_track and selected_track.has_midi_input:
            try:
                selected_track.implicit_arm = True
            except:
                pass
        # else:
        #     try:
        #         self.song().tracks[0].implicit_arm = True
        #     except:
        #         pass

    def _set_other_tracks_implicit_arm(self):
        for track in self.song().tracks:
            if track != self.song().view.selected_track:
                try:
                    track.implicit_arm = False
                except:
                    pass

    def _on_tracks_changed(self):
        self._update_mixer_and_tracks()
        self._register_clip_listeners()
        self._update_clip_slots()

    def _make_color_string(self, color):
        red = (color >> 16) & 255
        green = (color >> 8) & 255
        blue = color & 255
        color_string = "({},{},{})".format(red, green, blue)
        return color_string

    def _on_color_name_changed(self):
        self._update_mixer_and_tracks()
        self._on_selected_track_changed()

    # Updating names and number of tracks
    def _update_mixer_and_tracks(self):
        tracks = self.song().tracks
        tracks_length = len(tracks)
        # # send track names
        # track_names = ",".join([track.name for track in tracks])
        # self._send_sys_ex_message(track_names, 0x02)
        track_names = []
        track_is_audio = []
        track_colors = []

        for index, track in enumerate(self.song().tracks):
            # track names
            track_names.append(track.name)
            # is audio track
            if track.has_audio_input:
                track_is_audio.append("1")
            else:
                track_is_audio.append("0")
            # track colors
            color_string = self._make_color_string(track.color)
            track_colors.append(color_string)

            # output meter listeners
            if track.has_audio_output:
                # self.log_message("Adding listener at {}".format(index))
                if not track.output_meter_left_has_listener(self._on_output_level_changed(index)):
                    track.add_output_meter_left_listener(lambda index=index: self._on_output_level_changed(index))
                if not track.output_meter_right_has_listener(self._on_output_level_changed(index)):
                    track.add_output_meter_right_listener(lambda index=index: self._on_output_level_changed(index))

            # other listeners
            if not track.color_has_listener(self._on_color_name_changed):
                track.add_color_listener(self._on_color_name_changed)

            if not track.name_has_listener(self._on_color_name_changed):
                track.add_name_listener(self._on_color_name_changed)

        # send track names
        track_names_string = ",".join(track_names)
        self._send_sys_ex_message(track_names_string, 0x02)

        # send is audio tracks
        has_audio_string = ",".join(track_is_audio)
        self._send_sys_ex_message(has_audio_string, 0x0C)

        # send track colors
        track_colors_string = "-".join(track_colors)
        self._send_sys_ex_message(track_colors_string, 0x04)

        return_track_names = []
        return_track_colors = []

        for index, return_track in enumerate(self.song().return_tracks):
            return_track_names.append(return_track.name)

            color_string = color_string = self._make_color_string(return_track.color)
            return_track_colors.append(color_string)

            # output meter listeners
            return_index = index + tracks_length
            if not return_track.output_meter_left_has_listener(self._on_output_level_changed(return_index)):
                return_track.add_output_meter_left_listener(lambda index=return_index: self._on_output_level_changed(index))
            if not return_track.output_meter_right_has_listener(self._on_output_level_changed(return_index)):
                return_track.add_output_meter_left_listener(lambda index=return_index: self._on_output_level_changed(index))

        # output meter listeners master track
        master_index = 127 # len(self.song().return_tracks) + tracks_length
        # self.log_message("master index: {}".format(master_index))
        master_track = self.song().master_track
        if not master_track.output_meter_left_has_listener(self._on_output_level_changed(master_index)):
                master_track.add_output_meter_left_listener(lambda index=master_index: self._on_output_level_changed(index))
        if not master_track.output_meter_right_has_listener(self._on_output_level_changed):
            master_track.add_output_meter_right_listener(lambda index=master_index: self._on_output_level_changed(index))

        # add master track color to the mix:
        color_string = self._make_color_string(master_track.color)
        return_track_colors.append(color_string)

        # send return track names
        return_track_names_string = ",".join(return_track_names)
        self._send_sys_ex_message(return_track_names_string, 0x06)

        # send return track colors + master track
        track_colors_string = "-".join(return_track_colors)
        self._send_sys_ex_message(track_colors_string, 0x07)


        # Channels
        for index, track in enumerate(self.song().tracks):

            strip = mixer.channel_strip(index)

            # Configure strip controls for each channel track

            # VolumeSlider control
            volume_slider = SliderElement(MIDI_CC_TYPE, 2, index)  # MIDI CC channel 2, index == CC number
            strip.set_volume_control(volume_slider)

            # Send1Knob control
            send1_knob = EncoderElement(MIDI_CC_TYPE, 3, index, Live.MidiMap.MapMode.absolute)

            # Send2Knob control
            send2_knob = EncoderElement(MIDI_CC_TYPE, 4, index, Live.MidiMap.MapMode.absolute)
            strip.set_send_controls((send1_knob, send2_knob,))

            # Pan
            pan_knob = EncoderElement(MIDI_CC_TYPE, 5, index, Live.MidiMap.MapMode.absolute)
            strip.set_pan_control(pan_knob)

            # TrackMuteButton control
            mute_button = ButtonElement(1, MIDI_CC_TYPE, 6, index)
            strip.set_mute_button(mute_button)

            # Solo button control
            solo_button = ButtonElement(1, MIDI_CC_TYPE, 7, index)
            strip.set_solo_button(solo_button)

            # Other strip controls can be configured similarly
            # strip.set_arm_button(...)
            # strip.set_shift_button(...)

        # Master / channel 7 cc 127
        mixer.master_strip().set_volume_control(SliderElement(MIDI_CC_TYPE, 0, 127))
        mixer.set_prehear_volume_control(EncoderElement(MIDI_CC_TYPE, 0, 126, Live.MidiMap.MapMode.absolute))
        mixer.master_strip().set_pan_control(EncoderElement(MIDI_CC_TYPE, 0, 125, Live.MidiMap.MapMode.absolute))

        # Return Tracks
        for index, returnTrack in enumerate(self.song().return_tracks):
            strip = mixer.return_strip(index)

            # VolumeSlider
            return_volume_slider = SliderElement(MIDI_CC_TYPE, 8, index)
            strip.set_volume_control(return_volume_slider)

            # TrackMuteButton control
            mute_button = ButtonElement(1, MIDI_CC_TYPE, 8, index + 12)
            strip.set_mute_button(mute_button)

            # Solo button control
            solo_button = ButtonElement(1, MIDI_CC_TYPE, 8, index + 24)
            strip.set_solo_button(solo_button)

            # Send1Knob control (A)
            send1_knob = EncoderElement(MIDI_CC_TYPE, 8, index + 36, Live.MidiMap.MapMode.absolute)

            # Send2Knob control (B)
            send2_knob = EncoderElement(MIDI_CC_TYPE, 8, index + 48, Live.MidiMap.MapMode.absolute)
            strip.set_send_controls((send1_knob, send2_knob,))

            # Pan
            pan_knob = EncoderElement(MIDI_CC_TYPE, 8, index + 60, Live.MidiMap.MapMode.absolute)
            strip.set_pan_control(pan_knob)

    def _on_output_level_changed(self, index):
        # self.log_message("output level sending: {}".format(index))
        if self.mixer_status:
            if not self.mixer_reset:
                self.mixer_reset = True
            song = self.song()
            tracks = song.tracks
            return_tracks = song.return_tracks
            if index < len(tracks):
                track = tracks[index]
            elif index - len(tracks) < len(return_tracks):
                track = return_tracks[index - len(tracks)]
            else:
                track = song.master_track

            if track.has_audio_output:
                left_channel = track.output_meter_left
                right_channel = track.output_meter_right
            else:
                left_channel = 0.0
                right_channel = 0.0

            value_left = int(round(left_channel * 100))
            value_right = int(round(right_channel * 100))

            # send midi cc left on channel 9, right on channel 10, cc == index, 
            # value == Int(left_channel * 100)

            status_byte_left = 0xB8 | 9  # MIDI CC message on channel 9
            midi_cc_message_left = (status_byte_left, index, value_left)
            self._send_midi(midi_cc_message_left)
            status_byte_right = 0xB8 | 10  # MIDI CC message on channel 10
            midi_cc_message_right = (status_byte_right, index, value_right)
            self._send_midi(midi_cc_message_right)

        elif self.mixer_reset:
            self.mixer_reset = False

            song = self.song()
            tracks = song.tracks
            return_tracks = song.return_tracks
            value = 0
            total_track_number = len(tracks) + len(return_tracks) + 1

            for index in range(total_track_number):
                status_byte_left = 0xB8 | 9  # MIDI CC message on channel 9
                midi_cc_message_left = (status_byte_left, index, value)
                self._send_midi(midi_cc_message_left)
                status_byte_right = 0xB8 | 10  # MIDI CC message on channel 10
                midi_cc_message_right = (status_byte_right, index, value)
                self._send_midi(midi_cc_message_right)

    # clipSlots
    def _register_clip_listeners(self):
        for track in self.song().tracks:
            for clip_slot in track.clip_slots:

                if clip_slot == None:
                    continue
                # do this to ignore return-tracks
                # if not clip_slot.has_stop_button:
                #     continue

                if not clip_slot.has_clip_has_listener(self._on_clip_has_clip_changed):
                    clip_slot.add_has_clip_listener(self._on_clip_has_clip_changed)

                if not clip_slot.is_triggered_has_listener(self._on_clip_playing_status_changed):
                    clip_slot.add_is_triggered_listener(self._on_clip_playing_status_changed)

                if clip_slot.has_clip and not clip_slot.clip.color_has_listener(self._on_clip_has_clip_changed):
                    clip_slot.clip.add_color_listener(self._on_clip_has_clip_changed)

                # if clip_slot.has_clip:
                #     if not clip_slot.clip.playing_position_has_listener(self._on_playing_position_changed):
                #         clip_slot.clip.add_playing_position_listener(self._on_playing_position_changed)


                                #     # if not clip_slot.playing_status_has_listener(self._on_clip_playing_status_changed):
                #     #     # self.log_message("adding a playing status listener")
                #     #     clip_slot.clip.add_playing_status_listener(self._on_clip_playing_status_changed)

    def _unregister_clip_and_audio_listeners(self):
        for track in self.song().tracks:
            for clip_slot in track.clip_slots:
                clip_slot.remove_is_triggered_listener(self._on_clip_playing_status_changed)
                clip_slot.remove_has_clip_listener(self._on_clip_has_clip_changed)
                if clip_slot.has_clip:
                    clip_slot.clip.remove_color_listener(self._on_clip_has_clip_changed)
                # if clip_slot.has_clip:
                #     # clip_slot.clip.remove_playing_status_listener(self._on_clip_playing_status_changed)
                #     clip_slot.clip.remove_playing_position_listener(self._on_playing_position_changed)
            # output meter listeners
            if track.has_audio_output:
                if track.output_meter_left_has_listener(self._on_output_level_changed):
                    track.remove_output_meter_left_listener(self._on_output_level_changed)
                if track.output_meter_right_has_listener(self._on_output_level_changed):
                    track.remove_output_meter_right_listener(self._on_output_level_changed)

        for return_track in self.song().return_tracks:
            if return_track.output_meter_left_has_listener(self._on_output_level_changed):
                return_track.remove_output_meter_left_listener(self._on_output_level_changed)
            if return_track.output_meter_right_has_listener(self._on_output_level_changed):
                return_track.remove_output_meter_right_listener(self._on_output_level_changed)

    # def _on_playing_position_changed(self):
    #     # self.log_message("trying to log the playing position")
    #     self._update_clip_slots()

    def find_different_indexes(self, arrays1, arrays2):
        different_indexes = []

        for index, (array1, array2) in enumerate(zip_longest(arrays1, arrays2)):
            if array1 != array2:
                different_indexes.append(index)

        return different_indexes

    def _on_clip_playing_status_changed(self):
        # self.log_message("clip playing status changed")
        self._update_clip_slots()

    def _on_clip_has_clip_changed(self):
        # self.log_message("has clip status changed")
        self._update_clip_slots()
        self._set_up_notes_playing("clip")

    def _update_clip_slots(self):
        try:
            track_clips = []

            for track in self.song().tracks:
                # track clip slots
                clip_slots = []
                for clip_slot in track.clip_slots:
                    clip_value = "0"
                    if clip_slot.is_triggered:
                        clip_value = "4"
                    elif clip_slot.is_recording:
                        clip_value = "3"
                    elif clip_slot.is_playing:
                        clip_value = "2"
                    elif clip_slot.has_clip:
                        clip_value = "1"

                    color_string_value = "0"

                    if clip_value != "0":
                        if clip_slot.clip.color is not None:
                            color_string_value = self._make_color_string(clip_slot.clip.color)
                    #     playing_position = clip_slot.clip.playing_position
                    #     length = clip_slot.clip.length
                    #     self.log_message("playing: {} triggering {}".format(is_playing_value, is_triggered_value))
                    # else:
                    #     playing_position = 0.0
                    #     length = 0.0

                    clip_string = "{}:{}".format(clip_value, color_string_value)
                    clip_slots.append(clip_string)
                clip_slots_string = "-".join(clip_slots)
                track_clips.append(clip_slots_string)

            # compare old track clips with new
            clips_difference = self.find_different_indexes(track_clips, self.old_clips_array)
            
            # safe new values
            self.old_clips_array = track_clips

            # send different tracks out
            # TODO: now this still does send out each track. not sure why. also it should only send out the clip that is changed and not the whole track I would say.
            if clips_difference != []:
                for track_index in clips_difference:
                    if int(track_index) < len(track_clips):
                        string_prefix = str(track_index) + "%"
                        track_string = string_prefix + str(track_clips[track_index])
                        self._send_sys_ex_message(track_string, 0x05)
                    else:
                        delete_clips = "DEL" + str(track_index)
                        self._send_sys_ex_message(delete_clips, 0x05)
        except:
            # need to stop threading or we get a fatal error.
            # self.periodic_timer = 0
            pass

    def _on_scale_changed(self):
        song = self.song()
        scale = song.scale_name
        root = song.root_note
        scale_string = "{};{}".format(scale, root)
        self._send_sys_ex_message(scale_string, 0x0A)

    def handle_sysex(self, message):
        # start stop clip
        if len(message) >= 2 and message[1] == 9:
            values = self.extract_values_from_sysex_message(message)
            if len(values) == 3:
                self._fire_clip(values[0], values[1], values[2])
        # delete clip
        if len(message) >= 2 and message[1] == 10:
            values = self.extract_values_from_sysex_message(message)
            if len(values) == 2:
                self._delete_clip(values[0], values[1])
        # copy paste clip
        if len(message) >= 2 and message[1] == 11:
            values = self.extract_values_from_sysex_message(message)
            if len(values) == 4:
                self._copy_paste_clip(values[0], values[1], values[2], values[3])
        # scale and rootnote
        if len(message) >= 2 and message[1] == 12:
            values = self.decode_sys_ex_scale_root(message)
            if len(values) == 2:
                self._set_scale_root_note(values[0], values[1])
        # duplicate loop
        if len(message) >= 2 and message[1] == 13:
            values = self.extract_values_from_sysex_message(message)
            if len(values) == 2:
                self._duplicate_loop(values[0], values[1])

    def decode_sys_ex_scale_root(self, message):
        scale_name_bytes = message[2:-2]
        scale_name_bytes = bytes(message[2:-2])
        scale_name = scale_name_bytes.decode('utf-8')
        root_note_index = message[-2]
        return scale_name, root_note_index

    def extract_values_from_sysex_message(self, message):
        # Extract the values from the SysEx message based on the message format
        # Replace this with your own logic to extract the desired values
        # For example, if your message is [0xF0, 0x09, value1, value2, ..., 0xF7]
        # you can extract values starting from index 2: values = message[2:-1]
        values = message[2:-1]
        return values

    def _fire_clip(self, fire, track_index, clip_index):
        track = self.song().tracks[track_index]
        clip_slot = track.clip_slots[clip_index]
        if fire == 1:
            if clip_slot.is_playing:
                clip_slot.stop()
            else:
                clip_slot.set_fire_button_state(1)
        else:
            clip_slot.set_fire_button_state(1)

    def _delete_clip(self, track_index, clip_index):
        track = self.song().tracks[track_index]
        clip_slot = track.clip_slots[clip_index]
        clip_slot.delete_clip()

    def _duplicate_loop(self, track_index, clip_index):
        track = self.song().tracks[track_index]
        clip_slot = track.clip_slots[clip_index]
        if clip_slot.has_clip:
            clip_slot.clip.duplicate_loop()

    def _copy_paste_clip(self, from_track, from_clip, to_track, to_clip):
        tracks = self.song().tracks

        copy_track = tracks[from_track]
        copy_clip_slot = copy_track.clip_slots[from_clip]

        paste_track = tracks[to_track]
        paste_clip_slot = paste_track.clip_slots[to_clip]

        copy_clip_slot.duplicate_clip_to(paste_clip_slot)

    def _set_scale_root_note(self, scale, root):
        song = self.song()
        song.scale_name = scale
        song.root_note = root

    def _fire_scene(self, value):
        scenes = self.song().scenes
        if value < len(scenes):
            scene = scenes[value]
            scene.fire()

    def _select_clip_scene(self, value):
        scenes = self.song().scenes
        if value < len(scenes):
            self.song().view.selected_scene = scenes[value]
        track = self.song().view.selected_track
        if value < len(track.clip_slots):
            self.song().view.highlighted_clip_slot = track.clip_slots[value]
        self._send_selected_clip_slot(value)

    def _delete_scene(self, value):
        self.song().delete_scene(value)

    def _on_selected_scene_changed(self):
        selected_scene = self.song().view.selected_scene
        scenes_list = self.song().scenes
        new_index = self._find_track_index(selected_scene, scenes_list)
        self._send_selected_clip_slot(new_index)

    def _send_selected_clip_slot(self, clip_index):
        self._send_sys_ex_message(str(clip_index), 0x10)

    def _delete_device(self, value):
        selected_track = self.song().view.selected_track
        selected_track.delete_device(value)
        self._on_device_changed()

    def _move_device_left(self, value):
        song = self.song()
        selected_track = song.view.selected_track
        selected_device = selected_track.devices[value]
        song.move_device(selected_device, selected_track, value - 1)

    def _move_device_right(self, value):
        song = self.song()
        selected_track = song.view.selected_track
        selected_device = selected_track.devices[value]
        song.move_device(selected_device, selected_track, value + 2)

    def _add_midi_track(self, value):
        song = self.song()
        song.create_midi_track(value)

    def _delete_midi_track(self, value):
        song = self.song()
        song.delete_track(value)

    def _add_return_track(self, value):
        if value:
            self.song().create_return_track()

    def _update_mixer_status(self, value):
        if value:
            self.mixer_status = True
        else:
            self.mixer_status = False

    def _update_device_status(self, value):
        if value:
            self.device_status = True
        else:
            self.device_status = False

    def _delete_return_track(self, value):
        song = self.song()
        song.delete_return_track(value)

    def _add_random_synth(self, value):
        if value:
            browser = self.application().browser
            # selecting an instrument from the instrument folder
            found_instrument = False
            instruments = browser.instruments
            inst_children = instruments.children

            while not found_instrument:
                random_number = random.randint(0, len(inst_children) - 1)
                rand_instrument = inst_children[random_number]
                if rand_instrument.name not in ["CV Instrument", "CV Triggers", "External Instrument", "Ext. Instrument", "Drum Rack", "Instrument Rack", "Sampler", "Simpler", "Impulse"]:
                    if rand_instrument.is_device:
                        found_instrument = True
                    else:
                        # open folder (Drum Synth)
                        children = rand_instrument.children
                        rand_index = random.randint(0, len(children) - 1)
                        rand_instrument = children[rand_index]
                        found_instrument = True

            browser.load_item(rand_instrument)
            self._on_tracks_changed()
            self._on_device_changed()

    def _add_random_drums(self, value):
        if value:
            browser = self.application().browser
            # selecting a drum rack
            drums = browser.drums.children
            number_of_drums = len(drums)
            found_drum = False
            while not found_drum:
                random_index = random.randint(0, number_of_drums - 1)
                random_drum = drums[random_index]
                if random_drum.name not in ["Drum Hits", "Drum Rack"]:
                    found_drum = True
            browser.load_item(random_drum)
            self._on_tracks_changed()
            self._on_device_changed()

    def _add_random_sound(self, value):
        if value:
            browser = self.application().browser
            # selecting a random device from the sounds folder
            sounds = browser.sounds
            number_of_sounds = len(sounds.children)
            random_index = random.randint(0, number_of_sounds - 1)
            selected_sounds_folder = sounds.children[random_index]
            number_of_sounds = len(selected_sounds_folder.children)
            random_sound_index = random.randint(0, number_of_sounds - 1)
            selected_sound = selected_sounds_folder.children[random_sound_index]
            browser.load_item(selected_sound)
            self._on_tracks_changed()
            self._on_device_changed()

    def _add_random_effect(self, value):
        if value:
            browser = self.application().browser
            # Tried loading max for live effects but gave up
            # random_index = random.randint(0, 1)
            # if random_index == 0:
            #     max_effects = browser.max_for_live.children
            #     max_number = len(max_effects)
            #     random_max = random.randint(0, max_number - 1)
            #     selected_folder = max_effects[random_max].children
            #     max_number = len(selected_folder)
            #     finished = False
            #     number_of_tries = 0
            #     if max_number == 0:
            #         selected_effect = selected_folder
            #         finished = True
            #     while not finished and number_of_tries < 10:
            #         random_max = random.randint(0, max_number - 1)
            #         selected_effect = selected_folder[random_max]
            #         number_of_tries += 1
            #         self.log_message("Selected Device: {}".format(selected_effect.name))
            #         if not any(selected_effect.name.lower().startswith(substring.lower()) for substring in ["IR", "Api", "Map8", "Max Audio Effect"]):
            #             finished = True

            # else:
            effects = browser.audio_effects
            effect_children = effects.children
            number_of_effects = len(effect_children)
            # check if effects are in folders or not
            if number_of_effects >= 10:
                random_effect_index = random.randint(0, number_of_effects - 1)
                selected_effect = effect_children[random_effect_index]
            else:
                finished = False
                while not finished:
                    random_folder_index = random.randint(0, number_of_effects - 1)
                    selected_folder = effect_children[random_folder_index]
                    self.log_message("Selected FOlder: {}".format(selected_folder.name))
                    if selected_folder.name != "Utilities":
                        finished = True

                folder_children = selected_folder.children
                number_folder_children = len(folder_children)
                random_folder_child_index = random.randint(0, number_folder_children - 1)
                selected_effect = folder_children[random_folder_child_index]
            browser.load_item(selected_effect)

    def disconnect(self):
        self.capture_button.remove_value_listener(self._capture_button_value)
        self.quantize_button.remove_value_listener(self._quantize_button_value)
        self.duplicate_button.remove_value_listener(self._duplicate_button_value)
        self.duplicate_scene_button.remove_value_listener(self._duplicate_scene_button_value)
        self.sesh_record_button.remove_value_listener(self._sesh_record_value)
        self.redo_button.remove_value_listener(self._redo_button_value)
        self.undo_button.remove_value_listener(self._undo_button_value)
        song = self.song()
        # periodic_check_button.remove_value_listener(self._periodic_check)
        song.remove_tracks_listener(self._on_tracks_changed)
        # self.song().view.remove_selected_track_listener(self._on_selected_track_changed)
        # self._unregister_clip_and_audio_listeners()
        # self.remove_midi_listener(self._midi_listener)
        # self.song().view.remove_selected_scene_listener(self._on_selected_scene_changed)
        song.remove_scale_name_listener(self._on_scale_changed)
        song.remove_root_note_listener(self._on_scale_changed)
        self.periodic_timer = 0
        super(Tap, self).disconnect()

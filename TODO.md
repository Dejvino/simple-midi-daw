# PoC: Live Play + Event Listening

> Play notes using a MIDI keyboard and a software synthesizer.

- [x] Spawn FluidSynth
- [x] Connect to FluidSynth to send custom notes
- [x] Connect to a MIDI source and print out events
- [x] Connect a MIDI keyboard to FluidSynth
- [x] MIDI keyboard plays music!

# Core: Live Play

> Reliable and easy to use synth for your MIDI keyboard.

## Features
- [ ] Configurable MIDI sources (keyboards)
    - [x] one default config (useful as a template)
    - [x] customizable key mapping
    - [ ] library of configs for known models
- [ ] Configurable FluidSynth
    - [ ] sound font (system default || specific file)
    - [ ] audio output module (`-a xxx`)
- [ ] Automated MIDI source discovery (subscribe to port changes)

## Requirements
- [x] Plug and play: Once I connect a MIDI keyboard and start the app, pressing the keys plays music.
- [ ] Re-plug and play: If I connect a MIDI keyboard later during runtime, it also plays music.
- [x] Keyboard config: I can map functions to my MIDI keyboard's keys in a config file.
- [ ] Manual key learning: I can enable a vebrose MIDI mode and use the output to build my own keyboard mapping config file.
- [ ] Keyboard detection: My MIDI keyboard (supported by this DAW) is recognized and the correct mapping config file is used.
- [x] Manual sound font selection: I can select what sound font the synthesizer should use by copying/linking it as `default.sf2`.

# DAW: Basics

> Record and play MIDI clips.

## Features
- [ ] Metronome
    - [x] Enable/Disable button
    - [x] Configurable defaults
    - [ ] Change of tempo or time throug MIDI
- [x] Record and play a MIDI clip
    - [x] Record MIDI to a file
    - [x] Play MIDI from a file once
    - [x] Play MIDI from a file repeatedly

## Requirements
- [ ] Metronome: I can enable and configure a metronome that drives the tempo.
- [x] Record and replay: MIDI clip can be recorded and replayed (once or in a loop) in time with the music.

# DAW: Extras

> Going beyond a simple Plug & Play MIDI Synthesizer.

## Features
- [x] Record and play MIDI clips (bank of buttons)
- [ ] Record the whole session (keyboard and clips) into MIDI file
- [ ] Configurable Faders/Pots mapping
- [ ] Multiple tracks support
- [ ] Configurable MIDI proxy (e.g. split keyboard for multiple instruments)
- [x] DAW mode support for specific MIDI keyboards
- [ ] Launchpad support:
    - [ ] playing clips
    - [ ] creating drum loops
- [ ] Different synths support
- [ ] Export to external storage
- [ ] Wave audio support (clips playback, backing track, mixed recording, ...)
- ...

## Requirements
- [x] Record and replay clips: Multiple MIDI clips can be recorded and replayed simultaniously.
- [ ] Master recording: I can record my whole session into a MIDI file.

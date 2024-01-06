# PoC: Live Play + Event Listening

> Play notes using a MIDI keyboard and a software synthesizer.

- [x] Spawn FluidSynth
- [x] Connect to FluidSynth to send custom notes
- [x] Connect to a MIDI source and print out events
- [x] Connect a MIDI keyboard to FluidSynth
- [x] MIDI keyboard plays music!

# Core: Live Play

> Reliable and easy to use synth for your MIDI keyboard.

- [ ] Configurable MIDI sources (keyboards)
    - [x] one default config (useful as a template)
    - [x] customizable key mapping
    - [ ] library of configs for known models
- [ ] Configurable FluidSynth
    - [ ] sound font (system default || specific file)
    - [ ] audio output module (`-a xxx`)
- [ ] Automated MIDI source discovery (subscribe to port changes)

# DAW: Basics

> Record and play MIDI clips.

- [ ] Metronome
    - [x] Enable/Disable button
    - [x] Configurable defaults
    - [ ] Change of tempo or time throug MIDI
- [x] Record and play a MIDI clip
    - [x] Record MIDI to a file
    - [x] Play MIDI from a file once
    - [x] Play MIDI from a file repeatedly


# DAW: Extras

> Going beyond a simple Plug & Play MIDI Synthesizer.

- [ ] Gappless MIDI playback of loops
- [ ] Record and play MIDI clips (bank of buttons)
- [ ] Record the whole session (keybeard ayd clips) into MIDI file
- [ ] Configurable Faders/Pots mapping
- [ ] Multiple tracks support
- [ ] Configurable MIDI proxy (e.g. split keyboard for multiple instruments)
- [ ] DAW mode support for specific MIDI keyboards
- [ ] Launchpad support:
    - [ ] playing clips
    - [ ] creating drum loops
- [ ] Different synths support
- [ ] Export to external storage
- [ ] Wave audio support (clips playback, backing track, mixed recording, ...)
- ...

# Simple MIDI DAW

Quick and easy way to make sounds with a MIDI keyboard and a Linux computer in CLI.
Headless, no GUI needed.


## Features

- [x] Play notes using a MIDI keyboard and a software synthesizer
- [x] Record and replay a MIDI clip (once or looped)
- [x] Record MIDI to a file
- [x] Metronome
- [x] Customizable key mapping (config file)
- [ ] Support for various MIDI keyboards out-of-the-box
- [ ] Split keyboard for multiple instruments

## Install

```shell
python -m venv .venv
source .venv/bin/activate
python -m pip install -r requirements.txt
```

Copy or symlink some soundfont to `./default.sf2`.

## Usage

Connect your MIDI keyboard and run:

```shell
./simple-midi-daw
```

The app spawns a synthesizer with a sound font (`default.sf2`),
connects any known MIDI keyboard to it
and starts listening for MIDI commands (e.g. Record).

## Known issues
- Plugging in a MIDI keyboard at runtime doesn't work

## Dependencies

- Python3
- [MIDO](https://github.com/mido/mido/) MIDI Objects python library, defaulting to the [RtMidi backend](https://mido.readthedocs.io/en/stable/backends/rtmidi.html)
- FluidSynth software synthesizer
- some SoundFont2 file of your choice


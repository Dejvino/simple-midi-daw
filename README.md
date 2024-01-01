# Simple MIDI DAW

Quick and easy way to make sounds with a MIDI keyboard and a Linux computer in CLI.
Headless, no GUI needed.


## Features

- [ ] Play notes using a MIDI keyboard and a software synthesizer
- [ ] Record and play back MIDI clips
- [ ] Record and play loops
- [ ] Save MIDI recordings for later
- [ ] Metronome
- [ ] Split keyboard for multiple instruments
- [ ] Customizable key mapping, support for various MIDI keyboards

## Install

```shell
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

## Usage

```shell
./simple-midi-daw
```

The app spawns a synthesizer with the right sound font,
connects any known MIDI keyboard to it
and starts listening for MIDI commands (e.g. Record).


## Dependencies

- Python3
- ALSA (with sequencer support enabled)
- [alsa-midi python library](https://pypi.org/project/alsa-midi/)
- FluidSynth software synthesizer
- [pyFluidSynth python library](https://github.com/nwhitehead/pyfluidsynth)
- some SoundFont2 file


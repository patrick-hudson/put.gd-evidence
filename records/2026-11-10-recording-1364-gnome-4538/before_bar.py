# Photograph the published pre-feature nightly bar with its actual pre-feature API.
# Same picture harness, with only the microphone calls/parameters absent on that build removed.
import sys
from pathlib import Path
base=Path.home()/'work/s1364s2';sys.path.insert(0,str(base/'lab'))
source=(base/'lab/recording_bar_shots.py').read_text()
source=source.replace("entry['microphones'] = cli('recording.microphones', {'device': device} if device else {})", "entry['microphones'] = {'notInThisBuild': True}")
source=source.replace("audio = {'system': False, 'microphone': state == 'on'}", "audio = {'system': False}")
source=source.replace("if device:\n                audio['microphoneDevice'] = device", "if False:\n                audio['microphoneDevice'] = device")
exec(compile(source,str(base/'lab/recording_bar_shots.py'),'exec'),{'__name__':'__main__','__file__':str(base/'lab/recording_bar_shots.py')})

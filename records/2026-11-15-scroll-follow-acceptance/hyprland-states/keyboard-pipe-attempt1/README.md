# Keyboard pipe setup error

The first native-key probe opened its keyboard stdin as binary, then attempted a string write before End. No End stimulus was sent. The helper was stopped and its local image retained; closing the host pipes ends its native input helpers. The owned Firefox was explicitly stopped before the corrected text-mode retry. All original source/results/logs are preserved here.

set -eu
modprobe uinput
printf '%s\n' 'lab ALL=(root) NOPASSWD: /usr/bin/python3 /home/lab/work/s5202/umouse.py, /usr/bin/python3 /home/lab/work/s5202/umouse.py --with-tablet, /usr/bin/python3 /home/lab/work/s5202/keyboard.py' > /etc/sudoers.d/scroll1520-r2
chmod 0440 /etc/sudoers.d/scroll1520-r2
visudo -cf /etc/sudoers.d/scroll1520-r2 > /dev/null

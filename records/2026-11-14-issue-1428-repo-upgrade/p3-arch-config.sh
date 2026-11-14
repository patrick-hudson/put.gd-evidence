set -eu
umask 022
key=/usr/share/putgd/repo/putgd-nightly.asc
fingerprint=4032E28D893BAF66F4AC23D9A11D38D55536B371
actual=$(gpg --show-keys --with-colons "$key" | awk -F: '$1 == "fpr" { print $10; exit }')
printf 'Expected fingerprint: %s\nActual fingerprint: %s\n' "$fingerprint" "$actual"
[ "$actual" = "$fingerprint" ]
pacman-key --add "$key"
pacman-key --lsign-key "$fingerprint"
if [ ! -e /etc/pacman.d/putgd.conf ]; then cp /usr/share/putgd/repo/putgd-nightly.conf /etc/pacman.d/putgd.conf; fi
chmod 0644 /etc/pacman.d/putgd.conf
if ! grep -qxF 'Include = /etc/pacman.d/putgd.conf' /etc/pacman.conf; then printf '\nInclude = /etc/pacman.d/putgd.conf\n' >> /etc/pacman.conf; fi
cat /etc/pacman.d/putgd.conf

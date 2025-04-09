sudo qemu-system-i386 --device e1000,netdev=eth0,mac=aa:bb:cc:dd:ee:ff \
	--netdev tap,id=eth0,script=custom-scripts/qemu-ifup \
	--kernel output/images/bzImage \
	--hda output/images/rootfs.ext2 \
	--nographic \
	--append "console=ttyS0 root=/dev/sda" 

# qemu-system-i386 \
#   -M pc \
#   -kernel output/images/bzImage \
#   -hda output/images/rootfs.ext2 \
#   -append "console=ttyS0 root=/dev/sda" \
#   -netdev user,id=net0,hostfwd=tcp::18080-:8080 \
#   -device e1000,netdev=net0 \
#   -nographic

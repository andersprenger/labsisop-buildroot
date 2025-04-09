#!/bin/sh

cp $BASE_DIR/../custom-scripts/S41network-config $BASE_DIR/target/etc/init.d
chmod +x $BASE_DIR/target/etc/init.d/S41network-config

cp $BASE_DIR/../custom-scripts/S50linuxstatus $BASE_DIR/target/etc/init.d
chmod +x $BASE_DIR/target/etc/init.d/S50linuxstatus

cp $BASE_DIR/../custom-scripts/linux_status.py $BASE_DIR/target/usr/bin
chmod +x $BASE_DIR/target/usr/bin/linux_status.py
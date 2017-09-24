# Howto boot Alpine Xen dom0 with EFI

This guide will create an installation of diskless Alpine with Xen dom0 support, bootable with EFI.

## Create EFI bootable dom0 medium

**NOTE:** the official Alpine installation medium doesn't support EFI, so create the installed medium by booting it with BIOS/compatibility mode.

This guide assumes `alpine-xen-3.6.2-x86_64.iso` is used as boot medium, and is booted before continuing.

### Partition disk

Set up internet connectivity and configure to use an Alpine repository mirror:
```
$ ifconfig eth0 up
$ udhcpc eth0
$ setup-apkrepos
$ apk update
```

Assumptions:
1. The destination disk is at `/dev/sda`.
1. The size of the dom0 disk is 1GiB.
1. The dom0 disk and EFI ESP is the same partition.

```
$ modprobe vfat
$ apk add parted dosfstools
$ parted /dev/sda
(parted) mklabel gpt
(parted) mkpart ESP fat32 1MiB 1GiB
(parted) set 1 boot on
(parted) quit
$ mkfs.vfat /dev/sda1
```

### Setup diskless Alpine

```
$ apk add syslinux
$ setup-bootable /dev/cdrom /dev/sda1
```

### Install EFI bootloader

This uses Gummiboot as bootloader, which is deprecated but the only way with Xen 4.8.
Xen 4.9 supports multiboot2, making it possible to use GRUB2 instead, and avoiding creating the configuration for `xen.efi`.

```
$ apk add gummiboot
$ mount -t vfat /dev/sda1 /media/sda1
$ mkdir -p /media/sda1/EFI/boot /media/sda1/loader/entries
$ cp /usr/lib/gummiboot/gummibootx64.efi /media/sda1/EFI/boot/bootx64.efi
```

### Configure gummiboot

Gummiboot will be configured with two boot options: `linux-hardened` (without Xen) and `xen`.

**TODO:** The options below could be read from `/etc/update-extlinux.conf`

Create file `/media/sda1/loader/entries/linux-hardened.conf`:
```
linux /boot/vmlinuz-hardened
initrd /boot/initramfs-hardened
options modules=loop,squashfs,sd-mod,usb-storage quiet nomodeset
```

Create file `/media/sda1/loader/entries/xen.conf`:
```
efi /boot/xen.efi
```

**NOTE:** The first boot will be without Xen, to setup Xen properly first.

Create file `/media/sda1/loader/loader.conf`:
```
default linux-hardened
timeout 5
```

### Reboot into UEFI

Reboot the machine and make sure it boots via UEFI and not BIOS.

## Setup Xen dom0

Refer to the base dom0 guide: https://community.riocities.com/alpine_dom0.html

### Setup base system

```
$ setup-alpine
$ lbu commit
```

### Install Xen

```
$ apk add xen xen-hypervisor
$ lbu commit
```

### Copy Xen boot files

**NOTE:** due to a bug in current Xen APKBUILD, the Xen efi files are stored in `/usr/lib64/efi/xen`. See PR [aports#1513](https://github.com/alpinelinux/aports/pull/1513) for discussion.

**NOTE:** since symlinks isn't supported on vfat, this wastes quite some space...

**TODO:** this needs to be run upon Xen updates, so should be put in a script and run with `update-kernel`.

```
$ mount -o remount,rw /media/sda1
$ cp -f /usr/lib64/efi/xen* /media/sda1/boot/
```

### Configure Xen EFI bootloader

The `xen.efi` is a bootloader itself, which requires a configuration file.
This is easier with Xen 4.9 which has multiboot2 support, but for now it needs to be configured.

*TODO:* kernel options should also be read from `/etc/update-extlinux.conf` instead.

Create `/media/sda1/boot/xen.cfg`:
```
[global]
default=XEN-linux-hardened

[XEN-linux-hardened]
options=dom0_mem=1024M
kernel=vmlinuz-hardened modules=loop,squashfs,sd-mod,usb-storage quiet nomodeset
ramdisk=initramfs-hardened
```

### Set Xen as default boot

Set Xen as the default Gummiboot target.

In `/media/sda1/loader/loader.conf`:
```
default xen
timeout 5
```

### Reboot into Xen

```
$ reboot
```

## Setup Xen dom0 essentials

The system is now like a Xen dom0 system booted with BIOS.

```
$ setup-xen-dom0
$ lbu commit
```

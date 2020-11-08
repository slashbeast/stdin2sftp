stdin2sftp
==========

A very simple pump from stdin to a remote file via sftp. Useful for when one cannot just pipe over ssh to ``cat`` or ``dd``, for example. when remote sftp provider is limited to sftp-only, like ``OpenSSH`` with ``ChrootDirectory`` and ``internal-sftp``, an ``rclone serve sftp`` or ``proftpd`` with ``mod_sftp``,

Why?
====
I had a need to make a efficient backups of virtual machines disk images, which means copy-on-write snapshot of disk image, then transfer over the network while applying compression, without the need to first locally save compressed disk image and without blocking the host system or guest virtual machine during the process. The solution for that is to use reflinks as a copy-on-write snapshots, and then stream the content of reflinked disk image while compressing in between, to remote server. Sadly, neither ``scp`` nor ``sftp`` support reading from pipe., dropping ``not a file' error``. This way the source image is not blocked and is immutable  during the backup process regardless how how long all of the compression and transfer take, at no point in tiem I have a whole copy of the disk image and there's no need to write whole image compressed to disk before transfer.

Real life usage
===============

Make zero-copy snapshot of the Virtual Machine disk image::

  cp -a --reflink=always vm_1.qcow2 vm_1.qcow2_snapshot

And upload it over the network, while adding compression to remote file::

  zstd -6 < vm_1.qcow2_snapshot | \
  stdin2sftp \
    -u backupuser \
    -H backuphost.example.com \
    -f "/mnt/backups/vm_dumps/vm_1/$(date '+%Y-%m-%d_%H-%M-%S').qcow2.zstd"

And if one is worried about saturating network link, an bandwidth limit can be applied with ``pv``. Since with reflink, the source disk image is not blocked regardless of how long the transfer takes::

  zstd -6 < vm_1.qcow2_snapshot | \
  pv -L 64M | \
  stdin2sftp \
    -u backupuser \
    -H backuphost.example.com \
    -f "/mnt/backups/vm_dumps/vm_1/$(date '+%Y-%m-%d_%H-%M-%S').qcow2.zstd"

after which the snapshot can be discarded::

  rm -f vm_1.qcow2_snapshot

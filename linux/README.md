This directory contains the code for a Linux kernel module named `binfmt_spym`
which will register the SPYM binary format with the operating system to allow
SPYM binaries to be directly executed via the `execve` syscall.

Note that this kernel module is 100% a learning exercise because Linux already
includes functionality for registering arbitrary binary formats with the
operating system via
[`binfmt_misc`](https://www.kernel.org/doc/Documentation/binfmt_misc.txt).

However, if you'd like to play with this, to build the kernel module, simple
run the following:

```bash
$ make
$ sudo insmod binfmt_spym.ko
```

After that, you will now be able to natively execute SPYM binaries,
for example via `chmod +x a.out; ./a.out`.

To remove the kernel module, run

```bash
$ sudo rmmod binfmt_spym
```

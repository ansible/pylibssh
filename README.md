
# pylibssh: Python bindings to client functionality of libssh

## Requirements

You need Python 2.7 or 3.5+

pylibssh requires libssh to be installed in particular:
- libssh version 0.9.0 and later.

To install libssh Refer: https://www.libssh.org/get-it/


## Building the module

Build the extension
```
git clone https://github.com/ansible/pylibssh.git
cd pylibssh
python3 setup.py build_ext --inplace
```

## License

This library is distributed under the terms of LGPL 2.1,
see file COPYING in this repository.

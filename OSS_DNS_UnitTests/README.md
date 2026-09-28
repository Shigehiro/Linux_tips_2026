# OSS DNS: How to Run Unit Tests

## Description

This document describes how to run unit tests for several open-source DNS software packages, such as BIND, Unbound and Knot resolver.

## Reference

- BIND
  - https://gitlab.isc.org/isc-projects/bind9/-/tree/main/bin/tests/system
- unbound
  - https://github.com/NLnetLabs/unbound/blob/master/doc/README.tests
  - https://docs.rs/domain/latest/domain/stelline/index.html
- Knot resolver
  - https://github.com/CZ-NIC/knot-resolver/tree/master/tests

## BIND

```
# cat /etc/centos-release 
CentOS Stream release 10 (Coughlan)
```

<br>From the top-level directory, build the code for the unit tests:
```bash
git clone https://github.com/isc-projects/bind9.git
cd bind9
meson setup build
meson compile -C build
meson compile -C build system-test-dependencies
```

<br>Go to the test directory and see the README.md file in that directory. It contains instructions on how to run the tests.
```bash
cd bin/tests/system/
```

<br>Example:

Configure IP addresses:
```bash
sh ifconfig.sh up
```

<br>Run the test:
```bash
# pytest allow_query/tests_sh_allow_query.py 

...
PASSED allow_query/tests_sh_allow_query.py::test_allow_query
```

<br>Or run the test with additional options:
```bash
pytest allow_query/tests_sh_allow_query.py --trace

pytest allow_query/tests_sh_allow_query.py --noclean
```

<br>By default, DNS processes use randomly assigned ports ranging from PORT_MIN to PORT_MAX.
If you would like to run the processes on the default DNS port (53), edit `ports.py` as shown below.<br>

bind9/bin/tests/system/isctest/vars/ports.py
```python
    20  PORT_VARS = {
    21      "PORT": "5300",
    22      "TLSPORT": "5301",
    23      "HTTPPORT": "5302",
    24      "HTTPSPORT": "5303",
    25      "EXTRAPORT1": "5304",
    26      "EXTRAPORT2": "5305",
    27      "EXTRAPORT3": "5306",
    28      "EXTRAPORT4": "5307",
    29      "EXTRAPORT5": "5308",
    30      "EXTRAPORT6": "5309",
    31      "EXTRAPORT7": "5310",
    32      "EXTRAPORT8": "5311",
    33      "CONTROLPORT": "5312",
    34  }
    35
    36
    37  def set_base_port(base_port: int):
    38      log.debug(f"setting base port {base_port}")
    39      #assert base_port >= PORT_MIN
    40      #assert base_port <= PORT_MAX
    41      #base_port = 53
    42      #PORT_VARS["PORT"] = str(base_port)
    43      PORT_VARS["PORT"] = str(53)
    44      PORT_VARS["TLSPORT"] = str(base_port + 1)
    45      PORT_VARS["HTTPPORT"] = str(base_port + 2)
    46      PORT_VARS["HTTPSPORT"] = str(base_port + 3)
    47      PORT_VARS["EXTRAPORT1"] = str(base_port + 4)
    48      PORT_VARS["EXTRAPORT2"] = str(base_port + 5)
    49      PORT_VARS["EXTRAPORT3"] = str(base_port + 6)
    50      PORT_VARS["EXTRAPORT4"] = str(base_port + 7)
    51      PORT_VARS["EXTRAPORT5"] = str(base_port + 8)
    52      PORT_VARS["EXTRAPORT6"] = str(base_port + 9)
    53      PORT_VARS["EXTRAPORT7"] = str(base_port + 10)
    54      PORT_VARS["EXTRAPORT8"] = str(base_port + 11)
    55      PORT_VARS["CONTROLPORT"] = str(base_port + 12)
    56      os.environ.update(PORT_VARS)
```

<br>Pytest stops the test environment after completing the tests. If you would like to keep it running, execute pytest with the --trace option.<br>
```shell
$ pytest nsec_wildcard_wrong_zone/tests_nsec_wildcard_wrong_zone.py --trace
```

<br>On another terminal.
```shell
$ ps aux |grep -E 'named|ans1' |grep -v grep
hattori     3054  0.0  0.2 475244 17276 pts/0    Sl+  01:57   0:00 /home/hattori/bind9/build/named -D nsec_wildcard_wrong_zone-tmp-5eb35kz1-ns2 -m record -c named.conf -d 99 -g -T maxcachesize=2097152
hattori     3068  0.0  0.7  74280 61844 pts/0    S+   01:57   0:00 /home/hattori/venv/bin/python3.14 -u -m nsec_wildcard_wrong_zone-tmp-5eb35kz1.ans1.ans 10.53.0.1 53
```

## unbound

```
# cat /etc/centos-release 
CentOS Stream release 10 (Coughlan)
```

<br>Get the source code and build it.
```bash
git clone https://github.com/NLnetLabs/unbound.git
cd unbound
libtoolize --copy --force
aclocal
autoconf
autoheader

dnf install ldns-utils libevent-devel expat-devel
./configure --enable-checking --enable-debug --with-libevent
make
```

<br>Run all unit tests:
```bash
make test

...
./testdata/version_bind_hide.rpl  OK
./testdata/version_bind.rpl  OK
./testdata/views.rpl  OK
test OK
```

<br>Or
```
make longtest
```

<br>Run a specific test:
```bash
./testbound -p testdata/rrsig_agr_wild.rpl 
```

<br>Or run the integration/system tests.
From the top-level directory:
```bash
sh testcode/do-tests.sh

...
** PASSED ** : tcp_req_timeout
** PASSED ** : tcp_reuse
** PASSED ** : tcp_sigpipe
** PASSED ** : tls_reuse_auth
** PASSED ** : tls_reuse
** PASSED ** : zonemd_reload
cache-size-1    average qps:    309739
cache-suffices  average qps:    312026
cache-toosmall  average qps:    45652.5
version-server  average qps:    355233
localhost-addr  average qps:    336393
```

```
# ss -uanp |grep ldns
UNCONN 0      0                     0.0.0.0:9445       0.0.0.0:*    users:(("ldns-testns",pid=140080,fd=3),("ldns-testns",pid=140079,fd=3),("ldns-testns",pid=140077,fd=3),("ldns-testns",pid=140076,fd=3),("ldns-testns",pid=140075,fd=3),("ldns-testns",pid=140073,fd=3),("ldns-testns",pid=140072,fd=3),("ldns-testns",pid=140071,fd=3),("ldns-testns",pid=140070,fd=3),("ldns-testns",pid=140068,fd=3))
```

<br>Or
```bash
sh testcode/run_vm.sh 
```

## Knot resolver

I switched to Ubuntu becasuse I could not run config tests, extra tests, pytest.
```
# lsb_release -a|grep ^Desc
Description:    Ubuntu 26.04 LTS
```

```
apt update
apt install -y \
meson ninja-build pkg-config build-essential python3.14-venv \
libknot-dev libuv1-dev luajit libluajit-5.1-dev liblmdb-dev cmocka* \
cmock libssl-dev faketime libfaketime python3-augeas libaugeas-dev
```

```
git clone --recursive https://gitlab.nic.cz/knot/knot-resolver.git
```

```
python3 -m venv venv
source venv/bin/activate
pip install pip --upgrade
pip install -r knot-resolver/doc/requirements.txt
pip install -r ./knot-resolver/tests/pytests/requirements.txt
```

### Unit test

https://github.com/CZ-NIC/knot-resolver/tree/master/tests#unit-tests

```
meson setup build_dir

# ninja -C build_dir
ninja: Entering directory `build_dir'
[258/258] Linking target tests/unit/ratelimiting-parallel

# meson test -C build_dir --suite unit
ninja: Entering directory `/root/knot-resolver/build_dir'
ninja: no work to do.
 1/11 unit - knot-resolver:unit.array                                       OK              0.01s
 2/11 unit - knot-resolver:unit.lru                                         OK              0.01s
 3/11 unit - knot-resolver:unit.pack                                        OK              0.01s
 4/11 unit - knot-resolver:unit.queue                                       OK              0.01s
 5/11 unit - knot-resolver:unit.trie                                        OK              0.01s
 6/11 unit - knot-resolver:unit.module                                      OK              0.01s
 7/11 unit - knot-resolver:unit.rplan                                       OK              0.00s
 8/11 unit - knot-resolver:unit.utils                                       OK              0.01s
 9/11 unit - knot-resolver:unit.zonecut                                     OK              0.01s
10/11 unit - knot-resolver:unit.ratelimiting                                OK              0.34s
11/11 unit+skip_valgrind - knot-resolver:unit.ratelimiting-parallel         OK              1.01s

Ok:                11
Fail:              0

Full log written to /root/knot-resolver/build_dir/meson-logs/testlog.txt
```

### Config test

```
apt install luarocks -y
luarocks install cqueues
luarocks install basexx
```

Go to the top directory:
```
cd knot-resolver/
meson setup build_dir -Dconfig_tests=enabled
ninja install -C build_dir
meson test -C build_dir --suite config
```

### Extra tests

```
apt install -y libaugeas-dev libxml2-dev pkg-config python3-dev
pip install python-augeas
cd knot-resolver/
pip install -r ./tests/integration/deckard/requirements.txt
meson setup build_dir --reconfigure -Dextra_tests=enabled
ninja install -C build_dir
meson test -C build_dir --suite integration
```

### pytest

Same as extra tests:
```
meson setup build_dir --reconfigure -Dextra_tests=enabled
ninja install -C build_dir
meson test -C build_dir --suite pytests
```

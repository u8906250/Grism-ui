Grism XML Format
================

Summary
-------
define filter, ouput, action, chain xml format

Filter XML format
-----------------

filter
* id : string, need to be unique, blank not allow
* name : string
* sessionBase : yes or no (optional, default yes)
* masking: yes or no (optional, default no);
 * only for hfa regex condition
 * no actual filter function, just masking, packet pass directly
 * add {t} first for start offset support, ex: {t}Accept
 * do not care for or, and, ==, !=, session base

or
* all finds relation is or

and
* all finds relation is and

find
* name : refer to wireshark filter function, but less item
* relation : ==, != (may be support >, <, ... in future), could be empty
* content : content of name, could be empty

| name          | info            | content example                        | content type    |
|---------------|-----------------|----------------------------------------|-----------------|
| eth.addr      | mac address     | 6c:71:d9:51:3e:07                      | string          |
| eth.src       | src mac address | 6c:71:d9:51:3e:07                      | string          |
| eth.dst       | dst mac address | 6c:71:d9:51:3e:07                      | string          |
| eth.type      | ethernet type   | 2048                                   | 2-bytes integer |
| vlan.id       | vlan id         | 32                                     | 3-bytes integer |
| vlan.l2.id    | vlan layer 2 id | 32                                     | 3-bytes integer |
| vlan.priority | vlan priority   | 1                                      | 0-7 integer     |
| ip.addr       | ip address      | 192.168.1.100                          | string          |
| ip.src        | src ip address  | 192.168.1.100                          | string          |
| ip.dst        | dst ip address  | 192.168.1.100                          | string          |
| ip.proto      | ip protocol     | 6                                      | 1-byte integer  |
| tcp           | tcp protocol    |                                        |                 |
| tcp.port      | tcp port        | 80                                     | 2-bytes integer |
| tcp.srcport   | tcp src port    | 80                                     | 2-bytes integer |
| tcp.dstport   | tcp dst port    | 80                                     | 2-bytes integer |
| udp           | udp protocol    |                                        |                 |
| udp.port      | udp port        | 123                                    | 2-bytes integer |
| udp.srcport   | udp src port    | 123                                    | 2-bytes integer |
| udp.dstport   | udp dst port    | 123                                    | 2-bytes integer |
| 5-tuple       | 5-tuple         | 74.125.204.10 192.168.1.203 33433 80 6 | string          |
| regex         | regular express | \b[A-Z0-9._%+-]+@[A-Z0-9.-]+\.[A-Z]{3} | string          |
| voip          | voice over ip   |                                        |                 |
| voip.account  | voip account    | 92663366@o.gentrice.net                | string          |
| voip.account  | voip from       | 92663366@o.gentrice.net                | string          |
| voip.account  | voip to         | 92663366@o.gentrice.net                | string          |

IP Format example
* 192.168.1.150
* 192.168.1.*
* 192.168.1-10.*
* 192.168.1.1,2,3,4,5
* 192.168-170.*.1-5

Port Range Format example
* 80-443

5-tuple example
support IP range (except ,) and port range
```xml
<?xml version="1.0" encoding="UTF-8"?>
<filter id="1" name="01" sessionBase="no">
<or>
    <find name="5-tuple" relation="==" content="74.125.204.* 192.168.1.203 - 80-443 -" />
    <find name="5-tuple" relation="==" content="192.168.1.100 - - - -" />
</or>
</filter>
```

example
```xml
<filter id="1" name="01">
<or>
    <find name="ip.addr" relation="!=" content="192.168.1.203" />
    <find name="tcp.port" relation="==" content="80" />
</or>
</filter>

<filter id="2" name="2">
<or>
        <find name="ip.addr" relation="!=" content="192.168.1.203" />
        <find name="tcp" relation="" content="" />
</or>
</filter>

<filter id="3" name="3">
<or>
        <find name="vlan.id" relation="==" content="100" />
</or>
</filter>

<filter id="4" name="4">
<or>
        <find name="regex" relation="==" content="\b[A-Z0-9._%+-]+@[A-Z0-9.-]+\.[A-Z]{2,4}\b" />
</or>
</filter>
```

Output XML format
-----------------

output packet process
* 可混和 tagging(vlan), stripping(vlan, mpls, payload), maxlen 以及 udpencap or nvgre or pcap 任選一種或都不選

vlan tagging example
```xml
<output id="1" name="1" type="mix">
	<port>P1</port>
	<Q type="replace">10</Q>
	<QinQ type="add">20</QinQ>
</output>
```

vlan stripping
```xml
<output id="4" name="4" type="mix">
<port>P2</port>
<stripping>vlan</stripping>
</output>
```

TCP/UDP payload stripping
```xml
<output id="4" name="4" type="mix">
<port>P2</port>
<stripping>vlan</stripping>
</output>
```

mpls stripping
```xml
<output id="4" name="4" type="mix">
<port>P2</port>
<stripping>mpls</stripping>
</output>
```

payload cutting
```xml
<output id="5" name="5" type="mix">
<port>P2</port>
<maxlen>70</maxlen>
</output>
```

UDP Encapsulation example
在原始封包前面加上UDP header 可傳到指定的IP (經由switch, router) 目前只有單向送出去
```xml
<output id="1" name="1" type="mix">
<port>P1</port>
<dip>192.168.1.201</dip>
<sport>3060</sport>
<dport>3060</dport>
</output>
```

NVGRE example
```xml
<output id="1" name="1" type="mix">
<port>P3</port>
<nvgre_dip>192.168.1.201</nvgre_dip>
</output>
```

save pcap in dir
```xml
<output id="1" name="1" type="mix">
<port>H2</port>
<dir timeout="86400">work1</dir>
</output>
```

mix example: mpls stripping, maxlen 70, save to pcap
```xml
<output id="6" name="6" type="mix">
<port>H1</port>
<stripping>mpls</stripping>
<maxlen>70</maxlen>
<dir>work1</dir>
```

Action XML format
---------------------

input packet process
* 可混和 tagging(vlan), stripping(vlan, mpls, payload), maxlen

input packet vlanid tagging
```xml
<action type="input-packet-process" id="1" name="1">
<port>P5</port>
<Q type="replace">10</Q>
<QinQ type="add">20</QinQ>
</action>
```

input packet stripping
```xml
<action type="input-packet-process" id="1" name="1">
<port>P5</port>
<stripping>vlan</stripping>
</action>
```

input packet maxlen
```xml
<action type="input-packet-process" id="1" name="1">
<port>P5</port>
<maxlen>60</maxlen>
</action>
```

input packet mix 
```xml
<action type="input-packet-process" id="2" name="2">
<port>P1</port>
<Q type="replace">10</Q>
<stripping>mpls</stripping>
<stripping>payload</stripping>
</action>
```

Chain XML format
----------------

* P0, P1, P2, P3, P4, P5, P6, P7, P8, P9 : port id, start from 0
* H1, H2 : Hard Disk (only for output)
* F1, F2, F3, F4 ... : refer to filter id
* 0 : DISCARD

in
port id

out
port id or hard disk or output id(come from Output XML)
* type : duplicate, loadBalance (optional, default duplicate)
* lbtype : session, ethtype, iptype, smac, dmac, sip, dip, rr, 5thash (default session)

next
* type: match(default), notmatch

example1
<pre>
P0,P1 -> F1 -> P2
            -> F2 -> P3,P4(LB)
</pre>
```xml
<chain id="1" name="01">
   <in>P0,P1</in>
   <fid>F1</fid>
   <out>P2</out>
   <next>
        <fid>F2</fid>
        <out type="loadBalance">P3,P4</out>
   </next>
</chain>
```

example2
<pre>
P0,P1 -> F1 -> P2
            -> F2 -> F4 ->P5
                  -> P3,P6
            -> F3 -> P4
</pre>
```xml
<chain id="2" name="02">
   <in>P0,P1</in>
   <fid>F1</fid>
   <out>P2</out>
   <next>
        <fid>F2</fid>
        <out>P3,P6</out>
        <next>
                <fid>F4</fid>
                <out>P5</out>
        </next>
   </next>
   <next>
        <fid>F3</fid>
        <out>P4</out>
   </next>
</chain>
```

example3
</pre>
```xml
<?xml version="1.0" encoding="UTF-8"?>
<chain id="1" name="01">
   <in>P0,P1</in>
   <fid>F1</fid>
   <next type="match">
        <fid>F2</fid>
        <out>P3</out>
   </next>
   <next type="notmatch">
        <out>P4</out>
   </next>
</chain>
```

run.xml example
---------------

* input from P3 stripping vlan
* filter ip address != 192.168.1.203 or tcp port == 80 
* output to P4 maxlen 70

```xml
<?xml version="1.0" encoding="UTF-8"?>
<run>
<filter id="1" name="01">
<or>
    <find name="ip.addr" relation="!=" content="192.168.1.203" />
    <find name="tcp.port" relation="==" content="80" />
</or>
</filter>
<filter id="2" name="2">
<or>
    <find name="tcp" relation="" content="" />
</or>
</filter>
<action type="input-packet-process" id="1" name="1">
<port>P3</port>
<stripping>vlan</stripping>
</action>
<output id="1" name="1" type="mix">
<port>P4</port>
<maxlen>70</maxlen>
</output>
<chain id="1" name="1">
<in>P3</in>
<fid>F1</fid>
<next>
    <fid>F2</fid>
    <out>O1</out>
</next>
</chain>
</run>
```

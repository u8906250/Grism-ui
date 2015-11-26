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


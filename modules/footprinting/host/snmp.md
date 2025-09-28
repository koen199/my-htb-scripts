# SNMP 

Simple Network Management Protocol (SNMP) was created to monitor network devices. In addition, this protocol can also be used to handle configuration tasks and change settings remotely.

## MIB

MIB is an independent format for storing device information. A MIB is a text file in which all queryable SNMP objects of a device are listed in a standardized tree hierarchy. 

## OID 

An OID represents a node in a hierarchical namespace. A sequence of numbers uniquely identifies each node, allowing the node's position in the tree to be determined. The longer the chain, the more specific the information.

SNMPv1: No authentication, No encryption
SNMPv2: Authentication via community string. No encryption.
SNMVv3: Authentication & Encryption

## Community strings

Community strings can be seen as passwords that are used to determine whether the requested information can be viewed or not.

## Footprinting services

* snmpwalk: enumerate MIB tree with all OIDS
* onsixtyone: brute force community strings
* braa: brute-force the individual OIDs and enumerate the information behind them.


```
snmpwalk -v2c -c public 10.129.14.128
```

```
onesixtyone -c /opt/useful/seclists/Discovery/SNMP/snmp.txt 10.129.14.128
```

```
braa public@10.129.14.128:.1.3.6.*

#or do an entire subnet
braa public@10.129.14.0/24:.1.3.6.1.2.1.1.5.0
```

Key Difference in Philosophy
* snmpwalk = deep dive into one device.
* braa = wide sweep across many devices.

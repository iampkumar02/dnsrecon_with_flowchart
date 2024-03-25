
# DNSRecon

DNSRecon is a Python port of a Ruby script that I wrote to learn the language and about DNS in early 2007. 
This time I wanted to learn about Python and extend the functionality of the original tool and in the process re-learn how DNS works and how could it be used in the process of a security assessment and network troubleshooting. 

This script provides the ability to perform:
* Check all NS Records for Zone Transfers.
* Enumerate General DNS Records for a given Domain (MX, SOA, NS, A, AAAA, SPF and TXT).
* Perform common SRV Record Enumeration.
* Top Level Domain (TLD) Expansion.
* Check for Wildcard Resolution.
* Brute Force subdomain and host A and AAAA records given a domain and a wordlist.
* Perform a PTR Record lookup for a given IP Range or CIDR.
* Check a DNS Server Cached records for A, AAAA and CNAME Records provided a list of host records in a text file to check.

# Python Version
DNSRecon requires python3.6+

# Flow Chart
```mermaid
graph TD;
    A[dnsrecon.py] -->|-d| B[Target Domain]
    B -->|-j| C[json file]
    C --> D[Save results in Json file]
    
    B -->|-o| E[output file]
    E -->|-w| F[wordlist]
    F --> G[Save results in output file]
    
    B --> H[Enumerate and Run a scan]
    
    B --> |-a/-t axfr|I[Zone Transfer]
    
    B --> |-a --db|J[dnsrecon-db/xml]
    J --> K[Saved dnsrecon-db/xml file]
    
    A --> |-d|X[Target IP]
    X --> Y["DNS (reverse lookups) Brute force subdomains"]

    A --> |-r|L[Target IP]
    L --> M[Reverse DNS lookup]
    
    B --> |-t| N[zonewalk]
    N --> O[Zone Walking]
    
    B --> |-t| P[rvl]
    P --> Q[Reverse lookup of a given CIDR]
    
    B --> |-t| S[srv]
    S --> T[SRV records]

    B --> |-t| U[goo]
    U --> V[Google search for subdomains]

    A --> |-n| AA[NS_SERVER]
    AA --> AB[Domain server to use. If none is given, the SOA of the target will be used]

    A --> |-D| BB[DICTIONARY]
    BB --> BC[Brute force domain lookup]
```

#!/usr/bin/env python
# -*- coding: utf-8 -*-

#    Copyright (C) 2010  Carlos Perez
#
#    This program is free software; you can redistribute it and/or modify
#    it under the terms of the GNU General Public License as published by
#    the Free Software Foundation; Applies version 2 of the License.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU General Public License for more details.
#
#    You should have received a copy of the GNU General Public License
#    along with this program; if not, write to the Free Software
#    Foundation, Inc., 51 Franklin St, Fifth Floor, Boston, MA  02110-1301  USA

from time import sleep
import dns.resolver
import dns.reversename
import dns.zone
import dns.query
from dns.dnssec import algorithm_to_text

class DnsHelper:
    def __init__(self,domain,ns_server = None,request_timeout = 1.0,):
        self._domain = domain
        if ns_server:
            print "[*] Changing to server: ", ns_server
            self._res = dns.resolver.Resolver(configure=False)
            self._res.nameservers = [ns_server]
        else:
            self._res = dns.resolver.Resolver(configure=True)
        # Set timing
        self._res.timeout = request_timeout
        self._res.lifetime = request_timeout
        
    def get_a(self,host_trg):
        """
        Function for resolving the A Record for a given host. Returns an Array of
        the IP Address it resolves to.
        """
        address = []
        try:
            ipv4_answers = self._res.query(host_trg, 'A')
            for ardata in ipv4_answers:
                address.append(ardata.address)
                return address
        except:
            return address


    def get_aaaa(self,host_trg):
        """
        Function for resolving the AAAA Record for a given host. Returns an Array of
        the IP Address it resolves to.
        """
        address = []
        try:
            ipv6_answers = self._res.query(host_trg, 'AAAA')
            for ardata in ipv6_answers:
                address.append(ardata.address)
                return address
        except:
            return address


    def get_mx(self):
        """
        Function for MX Record resolving. Returns all MX records. Returns also the IP
        address of the host both in IPv4 and IPv6. Returns an Array
        """
        mx_records = []
        answers = self._res.query(self._domain, 'MX')
        for rdata in answers:
            try:
                name = rdata.exchange.to_text()
                ipv4_answers = self._res.query(name, 'A')
                for ardata in ipv4_answers:
                    mx_records.append(['MX', name[:-1], ardata.address,
                                    rdata.preference])
            except:
                pass
        try:
            for rdata in answers:
                name = rdata.exchange.to_text()
                ipv6_answers = self._res.query(name, 'AAAA')
                for ardata in ipv6_answers:
                    mx_records.append(['MX', name[:-1], ardata.address,
                                      rdata.preference])
            return mx_records
        except:
            return mx_records


    def get_ns(self):
        """
        Function for NS Record resolving. Returns all NS records. Returns also the IP
        address of the host both in IPv4 and IPv6. Returns an Array.
        """
        ns_srvs = []
        answers = self._res.query(self._domain, 'NS')
        for rdata in answers:
            name = rdata.target.to_text()
            ipv4_answers = self._res.query(name, 'A')
            for ardata in ipv4_answers:
                ns_srvs.append(['NS', name[:-1], ardata.address])

        try:
            for rdata in answers:
                name = rdata.target.to_text()
                ipv6_answers = self._res.query(name, 'AAAA')
                for ardata in ipv6_answers:
                    ns_srvs.append(['NS', name[:-1], ardata.address])

            return ns_srvs
        except:
            return ns_srvs


    def get_soa(self):
        """
        Function for SOA Record resolving. Returns all SOA records. Returns also the IP
        address of the host both in IPv4 and IPv6. Returns an Array.
        """
        soa_records = []
        answers = self._res.query(self._domain, 'SOA')
        for rdata in answers:
            name = rdata.mname.to_text()
            ipv4_answers = self._res.query(name, 'A')
            for ardata in ipv4_answers:
                soa_records.extend(['SOA', name[:-1], ardata.address])

        try:
            for rdata in answers:
                name = rdata.mname.to_text()
                ipv4_answers = self._res.query(name, 'AAAA')
                for ardata in ipv4_answers:
                    soa_records.extend(['SOA', name[:-1], ardata.address])

            return soa_records
        except:
            return soa_records


    def get_spf(self):
        """
        Function for SPF Record resolving returns the string with the SPF definition.
        Prints the string for the SPF Record and Returns the string
        """
        spf_record = []

        try:
            answers = self._res.query(self._domain, 'SPF')
            for rdata in answers:
                name = rdata.strings
                spf_record.extend(['SPF', name])
        except:
            return None

        return spf_record


    def get_txt(self):
        """
        Function for TXT Record resolving returns the string.
        """
        txt_record = []
        try:
            answers = self._res.query(self._domain, 'TXT')
            for rdata in answers:
                name = "".join(rdata.strings)
                txt_record.extend(['TXT', name])
        except:
            return None

        return txt_record

    
    def get_ptr(self,ipaddress):
        """
        Function for resolving PTR Record given it's IPv4 or IPv6 Address.
        """
        found_ptr = []
        n = dns.reversename.from_address(ipaddress)
        try:
            answers = self._res.query(n, 'PTR')
            for a in answers:
                found_ptr.append(['PTR', a.target.to_text(),ipaddress])
            return found_ptr
        except:
            return None

    
    def get_ip(self,hostname):
        """
        Function resolves a host name to its given A and/or AAA record. Returns Array
        of found hosts and IPv4 or IPv6 Address.
        """
        found_ip_add = []
        ipv4 = self.get_a(hostname)
        sleep(0.2)
        if ipv4:
            for ip in ipv4:
                found_ip_add.append(["A",hostname,ip])
        ipv6 = self.get_aaaa(hostname)

        if ipv6:
            for ip in ipv6:
                found_ip_add.append(["AAAA",hostname,ip])

        return found_ip_add
        
    def get_srv(self,host):
        """
        Function for resolving SRV Records.
        """
        record = []
        try:
            answers = self._res.query(host, 'SRV')
            for a in answers:
                target = a.target.to_text()
                for ip in self.get_ip(target):
                    record.append(['SRV', host, a.target.to_text(), ip[2],
                                  str(a.port), str(a.weight)])
        except:
            return record
        return record
    def zone_transfer(self):
        """
        Function for testing for zone transfers for a given Domain, it will parse the
        output by record type.
        """
        # if anyone reports a record not parsed I will add it, the list is a long one
        # I tried to include those I thought where the most common.

        zone_records = []
        print '[*] Checking for Zone Transfer for', self._domain, \
            'name servers'
        ns_srvs = self.get_ns()
        for ns in ns_srvs:
            ns_srv = ''.join(ns[2])
            print '[*] Trying NS server', ns_srv
            try:
                zone = dns.zone.from_xfr(dns.query.xfr(ns_srv, self._domain))
                print '[*] Zone Transfer was successful!!'
                zone_records.append({'zone_transfer':'success','ns_server':ns_srv})
                for (name, rdataset) in \
                    zone.iterate_rdatasets(dns.rdatatype.SOA):
                    for rdata in rdataset:
                        print '[*]\t', 'SOA', rdata.mname.to_text()
                        zone_records.append({'zone_server':ns_srv,'type':'SOA',\
                                             'mname':rdata.mname.to_text()
                        })

                for (name, rdataset) in \
                    zone.iterate_rdatasets(dns.rdatatype.NS):
                    for rdata in rdataset:
                        print '[*]\t', 'NS', rdata.target.to_text()
                        zone_records.append({'zone_server':ns_srv,'type':'NS',\
                                             'mname':rdata.target.to_text()
                        })

                for (name, rdataset) in \
                    zone.iterate_rdatasets(dns.rdatatype.TXT):
                    for rdata in rdataset:
                        print '[*]\t', 'TXT', ''.join(rdata.strings)
                        zone_records.append({'zone_server':ns_srv,'type':'TXT',\
                                             'strings':''.join(rdata.strings)
                        })

                for (name, rdataset) in \
                    zone.iterate_rdatasets(dns.rdatatype.SPF):
                    for rdata in rdataset:
                        print '[*]\t', 'SPF', ''.join(rdata.strings)
                        zone_records.append({'zone_server':ns_srv,'type':'SPF',\
                                             'strings':''.join(rdata.strings)
                        })

                for (name, rdataset) in \
                    zone.iterate_rdatasets(dns.rdatatype.MX):
                    for rdata in rdataset:
                        print '[*]\t', 'MX', str(name) + '.' + self._domain, \
                            rdata.exchange.to_text()
                        zone_records.append({'zone_server':ns_srv,'type':'MX',\
                                             'name':str(name) + '.' + self._domain,\
                                             'exchange':rdata.exchange.to_text()
                        })

                for (name, rdataset) in \
                    zone.iterate_rdatasets(dns.rdatatype.AAAA):
                    for rdata in rdataset:
                        print '[*]\t', 'AAAA', str(name) + '.' + self._domain, \
                            rdata.address
                        zone_records.append({'zone_server':ns_srv,'type':'AAAA',\
                                             'name':str(name) + '.' + self._domain,\
                                             'address':rdata.address
                        })

                for (name, rdataset) in \
                    zone.iterate_rdatasets(dns.rdatatype.A):
                    for rdata in rdataset:
                        print '[*]\t', 'A', str(name) + '.' + self._domain, \
                            rdata.address
                        zone_records.append({'zone_server':ns_srv,'type':'A',\
                                             'name':str(name) + '.' + self._domain,\
                                             'address':rdata.address
                        })

                for (name, rdataset) in \
                    zone.iterate_rdatasets(dns.rdatatype.CNAME):
                    for rdata in rdataset:
                        print '[*]\t', 'CNAME', str(name) + '.'\
                             + self._domain, rdata.target.to_text()
                        zone_records.append({'zone_server':ns_srv,'type':'CNAME',\
                                             'name':str(name)+ '.' + self._domain,\
                                             'target':str(rdata.target.to_text())
                        })

                for (name, rdataset) in \
                    zone.iterate_rdatasets(dns.rdatatype.SRV):
                    for rdata in rdataset:
                        print '[*]\t', 'SRV', str(name)+ '.' + self._domain, rdata.target, \
                        str(rdata.port), str(rdata.weight)
                        zone_records.append({'zone_server':ns_srv,'type':'SRV',\
                                             'name':str(name) + '.' + self._domain,\
                                             'target':rdata.target.to_text(),\
                                             'port':str(rdata.port),\
                                             'weight':str(rdata.weight)
                        })

                for (name, rdataset) in \
                    zone.iterate_rdatasets(dns.rdatatype.HINFO):
                    for rdata in rdataset:
                        print '[*]\t', 'HINFO', rdata.cpu, rdata.os
                        zone_records.append({'zone_server':ns_srv,'type':'HINFO',\
                                             'cpu':rdata.cpu,'os':rdata.os
                        })

                for (name, rdataset) in \
                    zone.iterate_rdatasets(dns.rdatatype.WKS):
                    for rdata in rdataset:
                        print '[*]\t', 'WKS', rdata.address, rdata.bitmap, rdata.protocol
                        zone_records.append({'zone_server':ns_srv,'type':'WKS',\
                                             'address':rdata.address,'bitmap':rdata.bitmap,\
                                             'protocol':rdata.protocol
                        })

                for (name, rdataset) in \
                    zone.iterate_rdatasets(dns.rdatatype.RP):
                    for rdata in rdataset:
                        print '[*]\t', 'RP', rdata.mbox, rdata.txt
                        zone_records.append({'zone_server':ns_srv,'type':'RP',\
                                             'mbox':rdata.mbox,'txt':rdata.txt
                        })

                for (name, rdataset) in \
                    zone.iterate_rdatasets(dns.rdatatype.AFSDB):
                    for rdata in rdataset:
                        print '[*]\t', 'AFSDB', rdata.subtype, rdata.hostname
                        zone_records.append({'zone_server':ns_srv,'type':'AFSDB',\
                                             'subtype':rdata.subtype,'hostname':rdata.hostname
                        })

                for (name, rdataset) in \
                    zone.iterate_rdatasets(dns.rdatatype.X25):
                    for rdata in rdataset:
                        print '[*]', '\tX25', rdata.address
                        zone_records.append({'zone_server':ns_srv,'type':'X25',\
                                             'address':rdata.address
                        })

                for (name, rdataset) in \
                    zone.iterate_rdatasets(dns.rdatatype.ISDN):
                    for rdata in rdataset:
                        print '[*]\t', 'ISDN', rdata.address
                        zone_records.append({'zone_server':ns_srv,'type':'ISDN',\
                                             'address':rdata.address
                        })

                for (name, rdataset) in \
                    zone.iterate_rdatasets(dns.rdatatype.RT):
                    for rdata in rdataset:
                        print '[*]\t', 'RT', str(rdata.exchange), rdata.preference
                        zone_records.append({'zone_server':ns_srv,'type':'X25',\
                                             'address':rdata.address
                        })

                for (name, rdataset) in \
                    zone.iterate_rdatasets(dns.rdatatype.NSAP):
                    for rdata in rdataset:
                        print '[*]\t', 'NSAP', rdata.address
                        zone_records.append({'zone_server':ns_srv,'type':'NSAP',\
                                             'address':rdata.address
                        })


                for (name, rdataset) in \
                    zone.iterate_rdatasets(dns.rdatatype.SIG):
                    for rdata in rdataset:
                        print '[*]\t', 'SIG', algorithm_to_text(rdata.algorithm), rdata.expiration, \
                        rdata.inception, rdata.key_tag, rdata.labels, rdata.original_ttl, \
                        rdata.signature, str(rdata.signer), rdata.type_covered
                        zone_records.append({'zone_server':ns_srv,'type':'SIG',\
                                             'algorithm':algorithm_to_text(rdata.algorithm),\
                                             'expiration':rdata.expiration,\
                                             'inception':rdata.inception,\
                                             'key_tag':rdata.key_tag,\
                                             'labels':rdata.labels,\
                                             'original_ttl':rdata.original_ttl,\
                                             'signature':rdata.signature,\
                                             'signer':str(rdata.signer),\
                                             'type_covered':rdata.type_covered
                        })

                for (name, rdataset) in \
                    zone.iterate_rdatasets(dns.rdatatype.RRSIG):
                    for rdata in rdataset:
                        print '[*]\t', 'RRSIG', algorithm_to_text(rdata.algorithm), rdata.expiration, \
                        rdata.inception, rdata.key_tag, rdata.labels, rdata.original_ttl, \
                        rdata.signature, str(rdata.signer), rdata.type_covered
                        zone_records.append({'zone_server':ns_srv,'type':'RRSIG',\
                                             'algorithm':algorithm_to_text(rdata.algorithm),\
                                             'expiration':rdata.expiration,\
                                             'inception':rdata.inception,\
                                             'key_tag':rdata.key_tag,\
                                             'labels':rdata.labels,\
                                             'original_ttl':rdata.original_ttl,\
                                             'signature':rdata.signature,\
                                             'signer':str(rdata.signer),\
                                             'type_covered':rdata.type_covered
                        })

                for (name, rdataset) in \
                    zone.iterate_rdatasets(dns.rdatatype.DNSKEY):
                    for rdata in rdataset:
                        print '[*]\t', 'DNSKEY', algorithm_to_text(rdata.algorithm), rdata.flags, rdata.key,\
                        rdata.protocol
                        zone_records.append({'zone_server':ns_srv,'type':'DNSKEY',\
                                             'algorithm':algorithm_to_text(rdata.algorithm),\
                                             'flags':rdata.flags,\
                                             'key':rdata.key,\
                                             'protocol':rdata.protocol
                        })

                for (name, rdataset) in \
                    zone.iterate_rdatasets(dns.rdatatype.DS):
                    for rdata in rdataset:
                        print '[*]\t', 'DS', algorithm_to_text(rdata.algorithm), rdata.digest, \
                        rdata.digest_type, rdata.key_tag
                        zone_records.append({'zone_server':ns_srv,'type':'DS',\
                                             'algorithm':algorithm_to_text(rdata.algorithm),\
                                             'digest':rdata.digest,\
                                             'digest_type':rdata.digest_type,\
                                             'key_tag':rdata.key_tag
                        })

                for (name, rdataset) in \
                    zone.iterate_rdatasets(dns.rdatatype.NSEC):
                    for rdata in rdataset:
                        print '[*]\t', 'NSEC', algorithm_to_text(rdata.algorithm),rdata.flags,\
                        rdata.iterations, rdata.salt
                        zone_records.append({'zone_server':ns_srv,'type':'NSEC',\
                                             'algorithm':algorithm_to_text(rdata.algorithm),\
                                             'flags':rdata.flags,\
                                             'iterations':rdata.iterations,\
                                             'salt':rdata.salt
                        })

                for (name, rdataset) in \
                    zone.iterate_rdatasets(dns.rdatatype.NSEC3):
                    for rdata in rdataset:
                        print '[*]\t', 'NSEC3', algorithm_to_text(rdata.algorithm),rdata.flags,\
                        rdata.iterations, rdata.salt
                        zone_records.append({'zone_server':ns_srv,'type':'NSEC',\
                                             'algorithm':algorithm_to_text(rdata.algorithm),\
                                             'flags':rdata.flags,\
                                             'iterations':rdata.iterations,\
                                             'salt':rdata.salt
                        })

                for (name, rdataset) in \
                    zone.iterate_rdatasets(dns.rdatatype.NSEC3PARAM):
                    for rdata in rdataset:
                        print '[*]\t', 'NSEC3PARAM', algorithm_to_text(rdata.algorithm),rdata.flags,\
                        rdata.iterations, rdata.salt
                        zone_records.append({'zone_server':ns_srv,'type':'NSEC3PARAM',\
                                             'algorithm':algorithm_to_text(rdata.algorithm),\
                                             'flags':rdata.flags,\
                                             'iterations':rdata.iterations,\
                                             'salt':rdata.salt
                        })

                for (name, rdataset) in \
                    zone.iterate_rdatasets(dns.rdatatype.IPSECKEY):
                    for rdata in rdataset:
                        print '[*]\t', 'IPSECKEY', algorithm_to_text(rdata.algorithm), rdata.gateway, \
                        rdata.gateway_type, rdata.key, rdata.precedence
                        zone_records.append({'zone_server':ns_srv,'type':'IPSECKEY',\
                                             'algorithm':algorithm_to_text(rdata.algorithm),\
                                             'gateway':rdata.gateway,\
                                             'gateway_type':rdata.gateway_type,\
                                             'key':rdata.key,\
                                             'precedence':rdata.precedence
                        })

            except:
                print '[-] Zone Transfer Failed!'
                zone_records.append({'zone_transfer':'failed','ns_server':ns_srv})
        return zone_records


def main():
    resolver = DnsHelper('google.com')
    print resolver.get_mx()
    print resolver.get_ip('www.google.com')
    print resolver.get_ns()
    print resolver.get_soa()
    print resolver.get_txt()
    print resolver.get_spf()
    tresolver = DnsHelper('owasp.org')
    print tresolver.zone_transfer()
if __name__ == "__main__":
    main()
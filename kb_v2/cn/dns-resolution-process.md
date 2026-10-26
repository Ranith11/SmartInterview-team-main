---
topic: DNS Resolution Process
domain: cn
subtopics: ["recursive", "iterative", "record types: A", "AAAA", "CNAME", "MX", "TXT", "NS", "SOA"]
sources:
  - title: "Wikipedia: Domain Name System"
    url: https://en.wikipedia.org/wiki/Domain_Name_System
    license: CC BY-SA 4.0
status: AUTO_VERIFIED
open_issues: 0
generator: openai/gpt-oss-120b
critic: openai/gpt-oss-20b
last_verified: 2026-10-02
human_reviewed: false
---
## Definition  

The Domain Name System (DNS) is a hierarchical, distributed database that maps human‑readable domain names to the data needed for network communication.  At its core, DNS stores **resource records (RRs)**—each record type conveys a specific piece of information, such as an IP address (A/AAAA), an alias (CNAME), mail routing (MX), or zone authority (SOA, NS, TXT).  Clients (resolvers) query DNS to translate a name like `www.example.com` into the IP address of the server that will actually handle the request.

---

## How It Works  

### Recursive resolution  

**Mechanism** – In a recursive query the client asks a DNS resolver to return the final answer. The resolver bears the full burden of contacting the root, TLD, and authoritative name servers until it can supply an answer or an error.  

**Worked example** – A user types `www.example.com` in a browser.  
1. The local resolver (often provided by the ISP) receives a recursive query.  
2. It contacts a root server → receives a referral to the `.com` TLD servers.  
3. It queries a `.com` server → receives a referral to `example.com` authoritative servers.  
4. It queries an `example.com` authoritative server → receives an **A** record `93.184.216.34`.  
5. The resolver returns this IP to the client, which can now open a TCP connection.

### Iterative resolution  

**Mechanism** – In an iterative query the resolver asks each server for the *best* information it has; the server never performs the full lookup on behalf of the client. The client must follow referrals itself.  

**Worked example** – A stub resolver on a workstation sends an iterative query to a root server.  
1. Root replies with the list of `.com` name servers.  
2. The workstation (or its local resolver) sends an iterative query to a `.com` server, which replies with the `example.com` NS records.  
3. The workstation queries one of those NS servers and finally receives the **A** record.  
The client does the “hopping” that a recursive resolver would otherwise hide.

### Record type: **A**  

**Mechanism** – Stores an IPv4 address (32‑bit) for a host name.  

**Worked example** – Query `dig A www.example.com` → response: `www.example.com. 3600 IN A 93.184.216.34`. The TTL of 3600 seconds tells caches how long to keep the record.

### Record type: **AAAA**  

**Mechanism** – Stores an IPv6 address (128‑bit) for a host name.  

**Worked example** – `dig AAAA www.example.com` → `www.example.com. 3600 IN AAAA 2606:2800:220:1:248:1893:25c8:1946`. IPv6‑only clients will use this address.

### Record type: **CNAME**  

**Mechanism** – Canonical name alias; points one name to another name’s records. The alias itself never holds other data types.  

**Worked example** – `mail.example.com CNAME www.example.com`. A query for `mail.example.com A` triggers the resolver to fetch the **A** record of `www.example.com` (93.184.216.34) and return it as the answer for the alias.

### Record type: **MX**  

**Mechanism** – Specifies mail exchange servers for a domain, with a priority value.  

**Worked example** – `example.com MX 10 mail1.example.com.` and `example.com MX 20 mail2.example.com.`. An email sender queries the MX records, picks the lowest‑priority (10) server, then resolves `mail1.example.com` to an **A**/`AAAA` address to deliver mail.

### Record type: **TXT**  

**Mechanism** – Holds arbitrary text strings; widely used for SPF, DKIM, domain verification, etc.  

**Worked example** – `example.com TXT "v=spf1 include:_spf.google.com ~all"`. A mail server retrieving the TXT record can evaluate the SPF policy to decide whether to accept a message.

### Record type: **NS**  

**Mechanism** – Lists authoritative name servers for a zone.  

**Worked example** – `example.com NS ns1.provider.net.` and `example.com NS ns2.provider.net.`. When a resolver reaches the delegation point, it uses these NS records to know where to query for the zone’s authoritative data.

### Record type: **SOA**  

**Mechanism** – Start of Authority record marks the beginning of a zone and contains administrative data: primary master server, responsible party email, serial number, refresh, retry, expire, and minimum TTL values.  

**Worked example** –  

```
example.com. 3600 IN SOA ns1.provider.net. hostmaster.example.com. (
        2023101501 ; serial
        7200       ; refresh (2h)
        1800       ; retry (30m)
        1209600    ; expire (2w)
        3600 )     ; minimum TTL
```

Secondary name servers use the serial number to detect zone changes and request an AXFR (full zone transfer) from the primary.

---

## Key Properties  

| Property | Description |
|----------|-------------|
| **Hierarchical** | Tree‑structured namespace from the root (.) down through TLDs to individual hosts. |
| **Distributed** | Authority is delegated via NS records; no single server holds the entire database. |
| **Caching** | Resolvers store answers for the TTL duration, reducing latency and load on upstream servers. |
| **Stateless queries** | Each DNS request is independent; UDP is the default transport, TCP used for large responses or zone transfers. |
| **Extensible** | New RR types can be added without breaking existing infrastructure. |

---

## Real‑World Use  

* **Web browsing** – Browsers rely on A/AAAA records to locate web servers.  
* **Email delivery** – MX records guide SMTP servers to the correct mail exchangers; SPF/DKIM policies are stored in TXT records.  
* **CDNs & load balancing** – Multiple A/AAAA records (or CNAME chains) enable geographic routing and failover.  
* **Domain verification** – Services like Google Search Console ask owners to publish a specific TXT record to prove control.  
* **Service discovery** – Internal corporate networks use SRV or custom TXT records to locate services without hard‑coding IPs.

---

## Comparison  

| Aspect | Recursive resolver | Iterative resolver (stub) |
|--------|-------------------|---------------------------|
| **Who does the work** | Resolver contacts all servers on behalf of the client. | Client follows each referral itself. |
| **Network traffic** | Fewer round‑trips for the client, but more traffic from resolver to upstream servers. | More round‑trips visible to the client; useful for debugging. |
| **Typical deployment** | ISP or corporate DNS servers. | OS‑level stub resolvers (e.g., `glibc` resolver). |
| **Security** | Can enforce DNSSEC validation centrally. | Validation must be performed by the client if desired. |

---

## Tradeoffs / When NOT to Use  

* **Recursive queries from untrusted networks** – Exposing a recursive resolver to the open Internet invites amplification attacks; use it only within a trusted perimeter.  
* **Iterative queries from constrained devices** – Mobile or IoT devices with limited CPU may prefer a recursive service to avoid multiple hops.  
* **CNAME at the apex** – DNS standards prohibit a CNAME at a zone’s apex because the apex must also hold NS and SOA records; use ALIAS or ANAME pseudo‑records instead.  
* **Large TXT records** – Overly long TXT strings can exceed UDP size limits, forcing TCP fallback and increasing latency; keep them concise.  

---

## Interview Q&A  

1. **Q:** *What is the difference between a recursive and an iterative DNS query?*  
   **A:** In a recursive query the resolver is asked to return the final answer; it will contact root, TLD, and authoritative servers as needed. In an iterative query the resolver returns the best information it has (often a referral), and the client must continue the lookup.  
   **Follow‑up:** *Why do most end‑user devices use recursive resolvers?*  

2. **Q:** *Explain how a CNAME record works and a common pitfall when using it.*  
   **A:** A CNAME creates an alias; the DNS server returns the canonical name, and the resolver then looks up the target’s records (A/AAAA, etc.). A pitfall is placing a CNAME at the zone apex, which conflicts with required NS and SOA records.  
   **Follow‑up:** *How do modern DNS providers allow “apex aliasing”?*  

3. **Q:** *Describe the role of the SOA record in zone transfers.*  
   **A:** The SOA contains a serial number that secondary servers compare against the primary’s serial. If the primary’s serial is higher, the secondary initiates an AXFR (full zone transfer) or IXFR (incremental).  
   **Follow‑up:** *What happens if the serial number is not incremented after a change?*  

4. **Q:** *What is DNS caching and how does TTL affect it?*  
   **A:** Caching stores DNS responses for the duration specified by the TTL field. A short TTL forces frequent refreshes (useful for load‑balanced services), while a long TTL reduces query load but may delay propagation of updates.  
   **Follow‑up:** *How can a client force a refresh before TTL expiry?*  

5. **Q:** *How does an MX record influence email delivery, and what does the priority value mean?*  
   **A:** MX records list mail servers for a domain; the priority (lower number = higher priority) tells the sending MTA which server to try first. If the primary server is unreachable, the MTA proceeds to the next higher‑priority MX.  
   **Follow‑up:** *Can an MX record point to a CNAME? Why or why not?*  

---

## Common Misconceptions  

| Misconception | Reality |
|---------------|---------|
| “DNS is a single database.” | DNS is a **distributed** hierarchy; each zone is served by its own authoritative servers. |
| “A CNAME can coexist with other records for the same name.” | RFC 1034 forbids any other record types (including NS, SOA) alongside a CNAME at the same owner name. |
| “Recursive resolvers always return the fastest IP.” | They return the first answer they receive; load‑balancing is achieved by the authoritative server returning multiple A/AAAA records or using geo‑based responses. |
| “TXT records are only for human‑readable notes.” | TXT records are heavily used for machine‑readable policies (SPF, DKIM, domain verification). |
| “If a resolver has a cached answer, it never contacts upstream servers.” | Cached data is used only while its TTL is valid; once expired, the resolver must re‑query upstream. |

<!-- END -->

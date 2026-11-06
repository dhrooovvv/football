# An integrated dataset of spatiotemporal and event data in elite soccer

Authors: Bassek, Rein, Weber, Memmert. Year: 2025.
Source: https://github.com/spoho-datascience/idsse-data

Official repository confirms seven matches, tracking/events, and CC-BY attribution. Label adapter still unexecuted.

Evidence scope: documentation/abstract or earlier audit record, not reproduced experimental results.

2026-11-06 adapter evidence: official floodlight DFL parser at https://raw.githubusercontent.com/floodlight-sports/floodlight/master/floodlight/io/dfl.py defines possession {1:Home,2:Away}, ballstatus {0:Dead,1:Alive}; raw frame N is source identity, T supports 25Hz verification, pitch coordinates centered. Metadata HomeTeamId and GuestTeamId provide explicit mapping. Figshare API article 28196177 provides file sizes and MD5 checksums. Only five development matches downloaded under protocol 6b71d10; sealed assets excluded. Attribution: Deutsche Fußball Liga (DFL), Bassek et al. Scientific Data 12,195 (2025), CC-BY4.0.

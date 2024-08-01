# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

### Changed

==========
Changelog
==========

+++++++++
v0.3.0 (01/08/2024)
+++++++++

**Fixed**

- Use new proposal-specific endpoint for dewar registry metadata

+++++++++
v0.2.0 (06/06/2024)
+++++++++

**Added**

- Pre session information endpoints

+++++++++
v0.1.0 (19/04/2024)
+++++++++

**Added**

- Samples endpoint now returns type as well
- Invalid characters are not allowed in item names
- Allow user to make multiple copies of sample
- All sample names will get prefixed with the macromolecule name
- Shipments are now session specific

**Fixed**

- Duplicate container names inside shipment are not allowed

+++++++++
v0.0.1 (27/03/2024)
+++++++++

**Added**

- Items exported to ISPyB now prepend the `comments` field with `Created by eBIC-SH`

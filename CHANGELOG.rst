==========
Changelog
==========

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

+++++++++
v0.9.1 (26/02/2025)
+++++++++

**Fixed**

- Use app JWT for authenticating against Expeye

+++++++++
v0.9.0 (25/02/2025)
+++++++++

**Added**

- Allow users to automatically generate dewar codes

**Fixed**

- Fix assertion when both barcodes and names are missing in container

+++++++++
v0.8.0 (28/01/2025)
+++++++++

**Added**

- PDF generation (:code:`/shipments/{shipmentId}/pdf-report)
- Endpoint for assigning cassette positions to data collection groups (:code:`/shipments/{shipmentId}/assign-data-collection-groups` and :code:`/proposals/{proposalReference}/sessions/{visitNumber}/assign-data-collection-groups)

**Changed**

- Rename "shipment" in shipping label to "sample collection"

+++++++++
v0.7.0 (10/01/2025)
+++++++++

**Added**

- Query parameter to ignore samples in internal containers
- Sample collection name is now returned alongside sample list

**Changed**

- Sample name is now checked against macromolecule to prevent duplicate prefixes

+++++++++
v0.6.2 (10/12/2024)
+++++++++

**Changed**

- Rename application to Scaup

+++++++++
v0.6.1 (27/11/2024)
+++++++++

**Changed**

- Include barcode data when pushing to ISPyB, to ensure compatibility with the dewar logistics service

+++++++++
v0.6.0 (22/10/2024)
+++++++++

**Added**

- Generate bar codes for dewars

**Changed**

- Include dewar in line items
- Do not include walk-ins in shipment requests
- Prevent overlapping children on patches/posts

+++++++++
v0.5.0 (24/09/2024)
+++++++++

**Added**

- Callback handler, passes callback URL to shipping service
- Add ISPyB data to samples endpoint

**Fixed**

- Allow orphan containers in authorisation
- Fixed dummy authentication

**Removed**

- Unused top level container fields

+++++++++
v0.4.0 (28/08/2024)
+++++++++

**Added**

- :code:`subType` column in :code:`Container`
- :code:`isInternal` column in :code:`Container`
- :code:`isCurrent` column in :code:`Container`
- :code:`subLocation` column in :code:`Sample`
- Inventory endpoints (:code:`topLevelContainer` as parent)
- New filters for samples/containers listing endpoints

+++++++++
v0.3.1 (01/08/2024)
+++++++++

**Fixed**

- Use new proposal-specific endpoints for dewar registry data

+++++++++
v0.3.0 (16/07/2024)
+++++++++

**Added**

- Allow new generic TLC types

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

==========
Changelog
==========

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

+++++++++
v0.14.2 (05/09/2025)
+++++++++

**Changed**

- Update dependencies

+++++++++
v0.14.1 (01/08/2025)
+++++++++

**Changed**

- Sort samples by cassette slot in report page

+++++++++
v0.14.0 (25/07/2025)
+++++++++

**Added**

- Populate firstExperimentId and dewarRegistryId in dewars

**Changed**

- Generate barcodes using old ISPyB standard

**Fixed**

- Display tracking labels even if lab contact is missing

+++++++++
v0.13.0 (10/07/2025)
+++++++++

**Added**

- Lock sessions 24 hours before they start (for users)

**Changed**

- Users can access proposal resources if they're in the session (not just the proposal)

+++++++++
v0.12.0 (08/07/2025)
+++++++++

**Added**

- Render temporary barcodes for dewars

**Changed**

- Always update shipment statuses, even when getting a whole shipment tree

+++++++++
v0.11.1 (01/07/2025)
+++++++++

**Fixed**

- Fixed dewar prefix generation behaviour

+++++++++
v0.11.0 (13/06/2025)
+++++++++

**Added**

- Include dewar history when getting top level containers
- Update shipment status automatically when getting shipments

+++++++++
v0.10.2 (16/05/2025)
+++++++++

**Added**

- Allow user to set separate backend and frontend URLs for sample shipping

+++++++++
v0.10.1 (08/05/2025)
+++++++++

**Changed**

- Only display instructions once per set of tracking labels
- Only display first two lab contacts in tracking labels

+++++++++
v0.10.0 (25/04/2025)
+++++++++

**Added**

- GET requests for samples now return a list of parents/children
- POST requests for samples now allow users to set sample parents when creating samples

+++++++++
v0.9.2 (11/04/2025)
+++++++++

**Changed**

- Allow users to push unassigned samples
- Improve logic for ordinal suffixes on samples
- Display more information in tracking labels

**Fixed**

- More accurately pair up samples from Expeye with samples in SCAUP database

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

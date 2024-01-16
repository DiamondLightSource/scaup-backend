--
-- PostgreSQL database dump
--

\connect sample_handling
\set VERBOSITY verbose

-- Dumped from database version 13.13 (Debian 13.13-1.pgdg120+1)
-- Dumped by pg_dump version 15.4
SET statement_timeout = 0;
SET lock_timeout = 0;
SET idle_in_transaction_session_timeout = 0;
SET client_encoding = 'UTF8';
SET standard_conforming_strings = on;
SELECT pg_catalog.set_config('search_path', '', false);
SET check_function_bodies = false;
SET xmloption = content;
SET client_min_messages = warning;
SET row_security = off;

--
-- Name: public; Type: SCHEMA; Schema: -; Owner: sample_handling
--

-- *not* creating schema, since initdb creates it


ALTER SCHEMA public OWNER TO sample_handling;

SET default_tablespace = '';

SET default_table_access_method = heap;

--
-- Name: Container; Type: TABLE; Schema: public; Owner: sample_handling
--

CREATE TABLE public."Container" (
    "containerId" integer NOT NULL,
    "shipmentId" integer NOT NULL,
    "topLevelContainerId" integer,
    "parentId" integer,
    type character varying(40) DEFAULT 'genericContainer'::character varying NOT NULL,
    capacity smallint,
    location smallint,
    details json,
    "requestedReturn" boolean NOT NULL,
    "registeredContainer" integer,
    name character varying(40) NOT NULL,
    "externalId" integer,
    comments character varying(255)
);


ALTER TABLE public."Container" OWNER TO sample_handling;

--
-- Name: COLUMN "Container".details; Type: COMMENT; Schema: public; Owner: sample_handling
--

COMMENT ON COLUMN public."Container".details IS 'Generic additional details';


--
-- Name: Container_containerId_seq; Type: SEQUENCE; Schema: public; Owner: sample_handling
--

CREATE SEQUENCE public."Container_containerId_seq"
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE public."Container_containerId_seq" OWNER TO sample_handling;

--
-- Name: Container_containerId_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: sample_handling
--

ALTER SEQUENCE public."Container_containerId_seq" OWNED BY public."Container"."containerId";


--
-- Name: Sample; Type: TABLE; Schema: public; Owner: sample_handling
--

CREATE TABLE public."Sample" (
    "sampleId" integer NOT NULL,
    "shipmentId" integer NOT NULL,
    "proteinId" integer NOT NULL,
    type character varying(40) DEFAULT 'sample'::character varying NOT NULL,
    location smallint,
    details json,
    "containerId" integer,
    name character varying(40) NOT NULL,
    "externalId" integer,
    comments character varying(255)
);


ALTER TABLE public."Sample" OWNER TO sample_handling;

--
-- Name: COLUMN "Sample".details; Type: COMMENT; Schema: public; Owner: sample_handling
--

COMMENT ON COLUMN public."Sample".details IS 'Generic additional details';


--
-- Name: Sample_sampleId_seq; Type: SEQUENCE; Schema: public; Owner: sample_handling
--

CREATE SEQUENCE public."Sample_sampleId_seq"
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE public."Sample_sampleId_seq" OWNER TO sample_handling;

--
-- Name: Sample_sampleId_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: sample_handling
--

ALTER SEQUENCE public."Sample_sampleId_seq" OWNED BY public."Sample"."sampleId";


--
-- Name: Shipment; Type: TABLE; Schema: public; Owner: sample_handling
--

CREATE TABLE public."Shipment" (
    "shipmentId" integer NOT NULL,
    "proposalReference" character varying(10) NOT NULL,
    "creationDate" timestamp with time zone DEFAULT now() NOT NULL,
    "shipmentRequest" integer,
    status character varying(25),
    name character varying(40) NOT NULL,
    "externalId" integer,
    comments character varying(255)
);


ALTER TABLE public."Shipment" OWNER TO sample_handling;

--
-- Name: Shipment_shipmentId_seq; Type: SEQUENCE; Schema: public; Owner: sample_handling
--

CREATE SEQUENCE public."Shipment_shipmentId_seq"
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE public."Shipment_shipmentId_seq" OWNER TO sample_handling;

--
-- Name: Shipment_shipmentId_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: sample_handling
--

ALTER SEQUENCE public."Shipment_shipmentId_seq" OWNED BY public."Shipment"."shipmentId";


--
-- Name: TopLevelContainer; Type: TABLE; Schema: public; Owner: sample_handling
--

CREATE TABLE public."TopLevelContainer" (
    "topLevelContainerId" integer NOT NULL,
    "shipmentId" integer NOT NULL,
    details json,
    code character varying(20) NOT NULL,
    "barCode" character varying(20),
    type character varying(40) DEFAULT 'dewar'::character varying NOT NULL,
    name character varying(40) NOT NULL,
    "externalId" integer,
    comments character varying(255)
);


ALTER TABLE public."TopLevelContainer" OWNER TO sample_handling;

--
-- Name: TopLevelContainer_topLevelContainerId_seq; Type: SEQUENCE; Schema: public; Owner: sample_handling
--

CREATE SEQUENCE public."TopLevelContainer_topLevelContainerId_seq"
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE public."TopLevelContainer_topLevelContainerId_seq" OWNER TO sample_handling;

--
-- Name: TopLevelContainer_topLevelContainerId_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: sample_handling
--

ALTER SEQUENCE public."TopLevelContainer_topLevelContainerId_seq" OWNED BY public."TopLevelContainer"."topLevelContainerId";


--
-- Name: Container containerId; Type: DEFAULT; Schema: public; Owner: sample_handling
--

ALTER TABLE ONLY public."Container" ALTER COLUMN "containerId" SET DEFAULT nextval('public."Container_containerId_seq"'::regclass);


--
-- Name: Sample sampleId; Type: DEFAULT; Schema: public; Owner: sample_handling
--

ALTER TABLE ONLY public."Sample" ALTER COLUMN "sampleId" SET DEFAULT nextval('public."Sample_sampleId_seq"'::regclass);


--
-- Name: Shipment shipmentId; Type: DEFAULT; Schema: public; Owner: sample_handling
--

ALTER TABLE ONLY public."Shipment" ALTER COLUMN "shipmentId" SET DEFAULT nextval('public."Shipment_shipmentId_seq"'::regclass);


--
-- Name: TopLevelContainer topLevelContainerId; Type: DEFAULT; Schema: public; Owner: sample_handling
--

ALTER TABLE ONLY public."TopLevelContainer" ALTER COLUMN "topLevelContainerId" SET DEFAULT nextval('public."TopLevelContainer_topLevelContainerId_seq"'::regclass);


--
-- Data for Name: Container; Type: TABLE DATA; Schema: public; Owner: sample_handling
--

COPY public."Container" ("containerId", "shipmentId", "topLevelContainerId", "parentId", type, capacity, location, details, "requestedReturn", "registeredContainer", name, "externalId", comments) FROM stdin;
1	1	1	\N	puck	\N	\N	\N	f	\N	Container 01	\N	\N
3	1	\N	\N	falconTube	\N	\N	\N	f	\N	Container 02	\N	\N
4	1	\N	\N	gridBox	\N	\N	\N	f	\N	Grid Box 02	\N	
5	1	\N	\N	gridBox	\N	\N	\N	f	\N	Grid Box 03	\N	
341	89	\N	\N	puck	\N	\N	\N	f	\N	Container 03	10	\N
2	1	\N	1	gridBox	\N	1	\N	f	\N	Grid Box 01	\N	Test Comment!
\.


--
-- Data for Name: Sample; Type: TABLE DATA; Schema: public; Owner: sample_handling
--

COPY public."Sample" ("sampleId", "shipmentId", "proteinId", type, location, details, "containerId", name, "externalId", comments) FROM stdin;
3	1	4407	sample	1	{"details": null, "shipmentId": 1, "foil": "Quantifoil copper", "film": "Holey carbon", "mesh": "200", "hole": "R 0.6/1", "vitrification": "GP2"}	4	Sample 02	\N	\N
1	1	4407	sample	1	{"details": null, "shipmentId": 1, "foil": "Quantifoil copper", "film": "Holey carbon", "mesh": "200", "hole": "R 0.6/1", "vitrification": "GP2"}	2	Sample 01	\N	\N
2	1	4407	sample	\N	{"details": null, "shipmentId": 1, "foil": "Quantifoil copper", "film": "Holey carbon", "mesh": "200", "hole": "R 0.6/1", "vitrification": "GP2"}	\N	Sample 02	\N	\N
336	89	4407	sample	\N	{"details": null, "shipmentId": 1, "foil": "Quantifoil copper", "film": "Holey carbon", "mesh": "200", "hole": "R 0.6/1", "vitrification": "GP2"}	\N	Sample 04	10	\N
\.


--
-- Data for Name: Shipment; Type: TABLE DATA; Schema: public; Owner: sample_handling
--

COPY public."Shipment" ("shipmentId", "proposalReference", "creationDate", "shipmentRequest", status, name, "externalId", comments) FROM stdin;
1	cm00001	2024-01-15 11:14:58.56198+00	\N	\N	Shipment 01	\N	\N
2	cm00002	2024-01-15 11:14:58.56198+00	\N	\N	Shipment 02	123	\N
89	cm00003	2024-01-15 11:14:58.56198+00	\N	Booked	Shipment 03	256	\N
\.


--
-- Data for Name: TopLevelContainer; Type: TABLE DATA; Schema: public; Owner: sample_handling
--

COPY public."TopLevelContainer" ("topLevelContainerId", "shipmentId", details, code, "barCode", type, name, "externalId", comments) FROM stdin;
1	1	\N	DLS-1	DLS-1	dewar	Dewar 01	\N	\N
2	2	\N	DLS-2	DLS-2	dewar	Dewar 02	\N	\N
3	2	\N	DLS-3	DLS-3	dewar	Dewar 03	\N	\N
61	89	\N	DLS-4	DLS-4	dewar	Dewar 04	10	\N
\.


--
-- Name: Container_containerId_seq; Type: SEQUENCE SET; Schema: public; Owner: sample_handling
--

SELECT pg_catalog.setval('public."Container_containerId_seq"', 40, true);


--
-- Name: Sample_sampleId_seq; Type: SEQUENCE SET; Schema: public; Owner: sample_handling
--

SELECT pg_catalog.setval('public."Sample_sampleId_seq"', 25, true);


--
-- Name: Shipment_shipmentId_seq; Type: SEQUENCE SET; Schema: public; Owner: sample_handling
--

SELECT pg_catalog.setval('public."Shipment_shipmentId_seq"', 6, true);


--
-- Name: TopLevelContainer_topLevelContainerId_seq; Type: SEQUENCE SET; Schema: public; Owner: sample_handling
--

SELECT pg_catalog.setval('public."TopLevelContainer_topLevelContainerId_seq"', 12, true);


--
-- Name: Container Container_externalId_key; Type: CONSTRAINT; Schema: public; Owner: sample_handling
--

ALTER TABLE ONLY public."Container"
    ADD CONSTRAINT "Container_externalId_key" UNIQUE ("externalId");


--
-- Name: Container Container_pkey; Type: CONSTRAINT; Schema: public; Owner: sample_handling
--

ALTER TABLE ONLY public."Container"
    ADD CONSTRAINT "Container_pkey" PRIMARY KEY ("containerId");


--
-- Name: Sample Sample_externalId_key; Type: CONSTRAINT; Schema: public; Owner: sample_handling
--

ALTER TABLE ONLY public."Sample"
    ADD CONSTRAINT "Sample_externalId_key" UNIQUE ("externalId");


--
-- Name: Sample Sample_pkey; Type: CONSTRAINT; Schema: public; Owner: sample_handling
--

ALTER TABLE ONLY public."Sample"
    ADD CONSTRAINT "Sample_pkey" PRIMARY KEY ("sampleId");


--
-- Name: Shipment Shipment_externalId_key; Type: CONSTRAINT; Schema: public; Owner: sample_handling
--

ALTER TABLE ONLY public."Shipment"
    ADD CONSTRAINT "Shipment_externalId_key" UNIQUE ("externalId");


--
-- Name: Shipment Shipment_pkey; Type: CONSTRAINT; Schema: public; Owner: sample_handling
--

ALTER TABLE ONLY public."Shipment"
    ADD CONSTRAINT "Shipment_pkey" PRIMARY KEY ("shipmentId");


--
-- Name: TopLevelContainer TopLevelContainer_externalId_key; Type: CONSTRAINT; Schema: public; Owner: sample_handling
--

ALTER TABLE ONLY public."TopLevelContainer"
    ADD CONSTRAINT "TopLevelContainer_externalId_key" UNIQUE ("externalId");


--
-- Name: TopLevelContainer TopLevelContainer_pkey; Type: CONSTRAINT; Schema: public; Owner: sample_handling
--

ALTER TABLE ONLY public."TopLevelContainer"
    ADD CONSTRAINT "TopLevelContainer_pkey" PRIMARY KEY ("topLevelContainerId");


--
-- Name: ix_Container_containerId; Type: INDEX; Schema: public; Owner: sample_handling
--

CREATE INDEX "ix_Container_containerId" ON public."Container" USING btree ("containerId");


--
-- Name: ix_Container_shipmentId; Type: INDEX; Schema: public; Owner: sample_handling
--

CREATE INDEX "ix_Container_shipmentId" ON public."Container" USING btree ("shipmentId");


--
-- Name: ix_Container_topLevelContainerId; Type: INDEX; Schema: public; Owner: sample_handling
--

CREATE INDEX "ix_Container_topLevelContainerId" ON public."Container" USING btree ("topLevelContainerId");


--
-- Name: ix_Sample_containerId; Type: INDEX; Schema: public; Owner: sample_handling
--

CREATE INDEX "ix_Sample_containerId" ON public."Sample" USING btree ("containerId");


--
-- Name: ix_Sample_sampleId; Type: INDEX; Schema: public; Owner: sample_handling
--

CREATE INDEX "ix_Sample_sampleId" ON public."Sample" USING btree ("sampleId");


--
-- Name: ix_Sample_shipmentId; Type: INDEX; Schema: public; Owner: sample_handling
--

CREATE INDEX "ix_Sample_shipmentId" ON public."Sample" USING btree ("shipmentId");


--
-- Name: ix_Shipment_proposalReference; Type: INDEX; Schema: public; Owner: sample_handling
--

CREATE INDEX "ix_Shipment_proposalReference" ON public."Shipment" USING btree ("proposalReference");


--
-- Name: ix_Shipment_shipmentId; Type: INDEX; Schema: public; Owner: sample_handling
--

CREATE INDEX "ix_Shipment_shipmentId" ON public."Shipment" USING btree ("shipmentId");


--
-- Name: ix_TopLevelContainer_shipmentId; Type: INDEX; Schema: public; Owner: sample_handling
--

CREATE INDEX "ix_TopLevelContainer_shipmentId" ON public."TopLevelContainer" USING btree ("shipmentId");


--
-- Name: ix_TopLevelContainer_topLevelContainerId; Type: INDEX; Schema: public; Owner: sample_handling
--

CREATE INDEX "ix_TopLevelContainer_topLevelContainerId" ON public."TopLevelContainer" USING btree ("topLevelContainerId");


--
-- Name: Container Container_parentId_fkey; Type: FK CONSTRAINT; Schema: public; Owner: sample_handling
--

ALTER TABLE ONLY public."Container"
    ADD CONSTRAINT "Container_parentId_fkey" FOREIGN KEY ("parentId") REFERENCES public."Container"("containerId") ON DELETE SET NULL;


--
-- Name: Container Container_shipmentId_fkey; Type: FK CONSTRAINT; Schema: public; Owner: sample_handling
--

ALTER TABLE ONLY public."Container"
    ADD CONSTRAINT "Container_shipmentId_fkey" FOREIGN KEY ("shipmentId") REFERENCES public."Shipment"("shipmentId");


--
-- Name: Container Container_topLevelContainerId_fkey; Type: FK CONSTRAINT; Schema: public; Owner: sample_handling
--

ALTER TABLE ONLY public."Container"
    ADD CONSTRAINT "Container_topLevelContainerId_fkey" FOREIGN KEY ("topLevelContainerId") REFERENCES public."TopLevelContainer"("topLevelContainerId") ON DELETE SET NULL;


--
-- Name: Sample Sample_containerId_fkey; Type: FK CONSTRAINT; Schema: public; Owner: sample_handling
--

ALTER TABLE ONLY public."Sample"
    ADD CONSTRAINT "Sample_containerId_fkey" FOREIGN KEY ("containerId") REFERENCES public."Container"("containerId") ON DELETE SET NULL;


--
-- Name: Sample Sample_shipmentId_fkey; Type: FK CONSTRAINT; Schema: public; Owner: sample_handling
--

ALTER TABLE ONLY public."Sample"
    ADD CONSTRAINT "Sample_shipmentId_fkey" FOREIGN KEY ("shipmentId") REFERENCES public."Shipment"("shipmentId");


--
-- Name: TopLevelContainer TopLevelContainer_shipmentId_fkey; Type: FK CONSTRAINT; Schema: public; Owner: sample_handling
--

ALTER TABLE ONLY public."TopLevelContainer"
    ADD CONSTRAINT "TopLevelContainer_shipmentId_fkey" FOREIGN KEY ("shipmentId") REFERENCES public."Shipment"("shipmentId");


--
-- Name: SCHEMA public; Type: ACL; Schema: -; Owner: sample_handling
--

REVOKE USAGE ON SCHEMA public FROM PUBLIC;
GRANT ALL ON SCHEMA public TO PUBLIC;


--
-- PostgreSQL database dump complete
--


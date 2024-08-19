--
-- PostgreSQL database dump
--

-- Dumped from database version 16.2
-- Dumped by pg_dump version 16.1

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
    "shipmentId" integer,
    "topLevelContainerId" integer,
    "parentId" integer,
    type character varying(40) DEFAULT 'genericContainer'::character varying NOT NULL,
    capacity smallint,
    location smallint,
    details json,
    "requestedReturn" boolean NOT NULL,
    "registeredContainer" character varying,
    name character varying(40) NOT NULL,
    "externalId" integer,
    comments character varying(255),
    "isInternal" boolean NOT NULL,
    "isCurrent" boolean NOT NULL
);


ALTER TABLE public."Container" OWNER TO sample_handling;

--
-- Name: COLUMN "Container".details; Type: COMMENT; Schema: public; Owner: sample_handling
--

COMMENT ON COLUMN public."Container".details IS 'Generic additional details';


--
-- Name: COLUMN "Container"."externalId"; Type: COMMENT; Schema: public; Owner: sample_handling
--

COMMENT ON COLUMN public."Container"."externalId" IS 'Item ID in ISPyB';


--
-- Name: COLUMN "Container"."isInternal"; Type: COMMENT; Schema: public; Owner: sample_handling
--

COMMENT ON COLUMN public."Container"."isInternal" IS 'Whether this container is for internal facility storage use only';


--
-- Name: COLUMN "Container"."isCurrent"; Type: COMMENT; Schema: public; Owner: sample_handling
--

COMMENT ON COLUMN public."Container"."isCurrent" IS 'Whether container position is current';


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


ALTER SEQUENCE public."Container_containerId_seq" OWNER TO sample_handling;

--
-- Name: Container_containerId_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: sample_handling
--

ALTER SEQUENCE public."Container_containerId_seq" OWNED BY public."Container"."containerId";


--
-- Name: PreSession; Type: TABLE; Schema: public; Owner: sample_handling
--

CREATE TABLE public."PreSession" (
    "preSessionId" integer NOT NULL,
    "shipmentId" integer NOT NULL,
    details json
);


ALTER TABLE public."PreSession" OWNER TO sample_handling;

--
-- Name: COLUMN "PreSession".details; Type: COMMENT; Schema: public; Owner: sample_handling
--

COMMENT ON COLUMN public."PreSession".details IS 'Generic additional details';


--
-- Name: PreSession_preSessionId_seq; Type: SEQUENCE; Schema: public; Owner: sample_handling
--

CREATE SEQUENCE public."PreSession_preSessionId_seq"
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public."PreSession_preSessionId_seq" OWNER TO sample_handling;

--
-- Name: PreSession_preSessionId_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: sample_handling
--

ALTER SEQUENCE public."PreSession_preSessionId_seq" OWNED BY public."PreSession"."preSessionId";


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
-- Name: COLUMN "Sample"."externalId"; Type: COMMENT; Schema: public; Owner: sample_handling
--

COMMENT ON COLUMN public."Sample"."externalId" IS 'Item ID in ISPyB';


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


ALTER SEQUENCE public."Sample_sampleId_seq" OWNER TO sample_handling;

--
-- Name: Sample_sampleId_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: sample_handling
--

ALTER SEQUENCE public."Sample_sampleId_seq" OWNED BY public."Sample"."sampleId";


--
-- Name: Shipment; Type: TABLE; Schema: public; Owner: sample_handling
--

CREATE TABLE public."Shipment" (
    "shipmentId" integer NOT NULL,
    "creationDate" timestamp with time zone DEFAULT now() NOT NULL,
    "shipmentRequest" integer,
    status character varying(25),
    name character varying(40) NOT NULL,
    "externalId" integer,
    comments character varying(255),
    "proposalCode" character varying(2) NOT NULL,
    "proposalNumber" integer NOT NULL,
    "visitNumber" integer NOT NULL
);


ALTER TABLE public."Shipment" OWNER TO sample_handling;

--
-- Name: COLUMN "Shipment"."externalId"; Type: COMMENT; Schema: public; Owner: sample_handling
--

COMMENT ON COLUMN public."Shipment"."externalId" IS 'Item ID in ISPyB';


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


ALTER SEQUENCE public."Shipment_shipmentId_seq" OWNER TO sample_handling;

--
-- Name: Shipment_shipmentId_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: sample_handling
--

ALTER SEQUENCE public."Shipment_shipmentId_seq" OWNED BY public."Shipment"."shipmentId";


--
-- Name: TopLevelContainer; Type: TABLE; Schema: public; Owner: sample_handling
--

CREATE TABLE public."TopLevelContainer" (
    "topLevelContainerId" integer NOT NULL,
    "shipmentId" integer,
    details json,
    code character varying(20) NOT NULL,
    "barCode" character varying(20),
    type character varying(40) DEFAULT 'dewar'::character varying NOT NULL,
    name character varying(40) NOT NULL,
    "externalId" integer,
    comments character varying(255),
    "isInternal" boolean NOT NULL
);


ALTER TABLE public."TopLevelContainer" OWNER TO sample_handling;

--
-- Name: COLUMN "TopLevelContainer"."externalId"; Type: COMMENT; Schema: public; Owner: sample_handling
--

COMMENT ON COLUMN public."TopLevelContainer"."externalId" IS 'Item ID in ISPyB';


--
-- Name: COLUMN "TopLevelContainer"."isInternal"; Type: COMMENT; Schema: public; Owner: sample_handling
--

COMMENT ON COLUMN public."TopLevelContainer"."isInternal" IS 'Whether this container is for internal facility storage use only';


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


ALTER SEQUENCE public."TopLevelContainer_topLevelContainerId_seq" OWNER TO sample_handling;

--
-- Name: TopLevelContainer_topLevelContainerId_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: sample_handling
--

ALTER SEQUENCE public."TopLevelContainer_topLevelContainerId_seq" OWNED BY public."TopLevelContainer"."topLevelContainerId";


--
-- Name: alembic_version; Type: TABLE; Schema: public; Owner: sample_handling
--

CREATE TABLE public.alembic_version (
    version_num character varying(32) NOT NULL
);


ALTER TABLE public.alembic_version OWNER TO sample_handling;

--
-- Name: Container containerId; Type: DEFAULT; Schema: public; Owner: sample_handling
--

ALTER TABLE ONLY public."Container" ALTER COLUMN "containerId" SET DEFAULT nextval('public."Container_containerId_seq"'::regclass);


--
-- Name: PreSession preSessionId; Type: DEFAULT; Schema: public; Owner: sample_handling
--

ALTER TABLE ONLY public."PreSession" ALTER COLUMN "preSessionId" SET DEFAULT nextval('public."PreSession_preSessionId_seq"'::regclass);


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

COPY public."Container" ("containerId", "shipmentId", "topLevelContainerId", "parentId", type, capacity, location, details, "requestedReturn", "registeredContainer", name, "externalId", comments, "isInternal", "isCurrent") FROM stdin;
1	1	1	\N	puck	\N	\N	\N	f	\N	Container_01	\N	\N	f	f
3	1	\N	\N	falconTube	\N	\N	\N	f	\N	Container_02	\N	\N	f	f
341	89	\N	\N	puck	\N	\N	\N	f	\N	Container_03	10	\N	f	f
4	1	\N	\N	gridBox	4	\N	\N	f	\N	Grid_Box_02	\N	\N	f	f
5	1	\N	\N	gridBox	4	\N	\N	f	\N	Grid_Box_03	\N	\N	f	f
2	1	\N	1	gridBox	4	\N	\N	f	\N	Grid_Box_01	\N	Test Comment!	f	f
712	97	171	\N	puck	16	\N	\N	f	\N	Container_03	20	\N	f	f
648	97	\N	646	gridBox	4	\N	\N	f	\N	Grid_Box_02	\N	\N	f	f
777	117	199	\N	puck	16	\N	{}	f	\N	Puck_2	303612		f	f
776	117	\N	777	gridBox	4	1	{"lid": "Screw", "fibSession": false, "store": false}	f	\N	Grid_Box_1	303613		f	f
646	97	152	\N	puck	\N	\N	\N	f	\N	Container_01	\N	\N	f	f
788	117	\N	784	gridBox	4	1	{"lid": "Screw", "fibSession": false, "store": false}	f	\N	Grid_Box_2	\N		f	f
784	\N	\N	825	puck	12	\N	\N	f	\N	Internal_puck	\N	\N	t	f
825	\N	221	\N	cane	10	\N	\N	f	\N	Internal_cane	\N	\N	t	f
1162	\N	\N	\N	cane	10	\N	\N	f	\N	Orphan_cane	\N	\N	t	f
\.


--
-- Data for Name: PreSession; Type: TABLE DATA; Schema: public; Owner: sample_handling
--

COPY public."PreSession" ("preSessionId", "shipmentId", details) FROM stdin;
15	2	{"name": "previous"}
54	117	{"clipped": false, "gridCrossGrating": "No", "pixelSize": "", "totalDose": "", "dosePerFrame": "", "tiltSpan": "", "tiltStep": "", "startAngle": "", "tiltScheme": "", "useTomoEpu": "Tomo", "experimentType": "3D-ED", "comments": ""}
\.


--
-- Data for Name: Sample; Type: TABLE DATA; Schema: public; Owner: sample_handling
--

COPY public."Sample" ("sampleId", "shipmentId", "proteinId", type, location, details, "containerId", name, "externalId", comments) FROM stdin;
2	1	4407	sample	\N	{"foil": "Quantifoil copper", "film": "Holey carbon", "mesh": "200", "hole": "R 0.6/1", "vitrification": "GP2", "buffer": "3", "concentration": "5", "vitrificationConditions": "", "clipped": false}	\N	Sample_02	\N	\N
3	1	4407	sample	1	{"details": null, "shipmentId": 1, "foil": "Quantifoil copper", "film": "Holey carbon", "mesh": "200", "hole": "R 0.6/1", "vitrification": "GP2"}	4	Sample_02	\N	\N
1	1	4407	sample	1	{"details": null, "shipmentId": 1, "foil": "Quantifoil copper", "film": "Holey carbon", "mesh": "200", "hole": "R 0.6/1", "vitrification": "GP2"}	2	Sample_01	\N	\N
336	89	4407	sample	\N	{"details": null, "shipmentId": 1, "foil": "Quantifoil copper", "film": "Holey carbon", "mesh": "200", "hole": "R 0.6/1", "vitrification": "GP2"}	\N	Sample_04	10	\N
561	117	338108	grid	1	{"buffer": "", "concentration": "", "foil": "Quantifoil copper", "film": "Holey carbon", "mesh": "200", "hole": "R 0.6/1", "vitrification": "GP2", "vitrificationConditions": ""}	776	3P_1	5664919	\N
434	97	4407	sample	\N	{"details": null, "shipmentId": 1, "foil": "Quantifoil copper", "film": "Holey carbon", "mesh": "200", "hole": "R 0.6/1", "vitrification": "GP2"}	648	Sample_04	\N	\N
562	118	338108	grid	\N	{"buffer": "", "concentration": "", "foil": "Quantifoil copper", "film": "Holey carbon", "mesh": "200", "hole": "R 0.6/1", "vitrification": "GP2", "vitrificationConditions": ""}	\N	3P_1	\N	\N
612	117	338108	grid	\N	{"buffer": "", "concentration": "", "foil": "Quantifoil copper", "film": "Holey carbon", "mesh": "200", "hole": "R 0.6/1", "vitrification": "GP2", "vitrificationConditions": ""}	788	3P_1	\N	\N
\.


--
-- Data for Name: Shipment; Type: TABLE DATA; Schema: public; Owner: sample_handling
--

COPY public."Shipment" ("shipmentId", "creationDate", "shipmentRequest", status, name, "externalId", comments, "proposalCode", "proposalNumber", "visitNumber") FROM stdin;
1	2024-05-02 13:12:36.528788+00	\N	\N	Shipment_01	\N	\N	cm	1	1
2	2024-05-02 13:12:36.528788+00	\N	\N	Shipment_02	123	\N	cm	2	1
89	2024-05-02 13:12:36.528788+00	\N	Booked	Shipment_03	256	\N	cm	2	1
97	2024-06-26 12:55:39.211687+00	\N	\N	Shipment_04	\N	\N	cm	3	1
106	2024-06-26 12:55:39.211687+00	\N	\N	Shipment_05	789	\N	cm	3	1
117	2024-06-26 13:36:53.632782+00	1	Booked	1	63975	\N	bi	23047	100
118	2024-06-26 13:40:32.191664+00	\N	\N	2	\N	\N	bi	23047	100
126	2024-07-15 15:35:32.472987+00	\N	\N	1	\N	\N	bi	23047	99
\.


--
-- Data for Name: TopLevelContainer; Type: TABLE DATA; Schema: public; Owner: sample_handling
--

COPY public."TopLevelContainer" ("topLevelContainerId", "shipmentId", details, code, "barCode", type, name, "externalId", comments, "isInternal") FROM stdin;
3	2	\N	DLS-3	DLS-3	dewar	Dewar_03	\N	\N	f
61	89	\N	DLS-4	DLS-4	dewar	Dewar_04	10	\N	f
2	2	\N	DLS-2	DLS-2	dewar	Dewar_02	\N	\N	f
1	1	\N	DLS-1	DLS-1	dewar	DLS-EM-0000	\N	\N	f
152	97	\N	DLS-4	DLS-4	dewar	Dewar_05	\N	\N	f
171	106	\N	DLS-4	DLS-4	dewar	Dewar_06	20	\N	f
199	117	{}	DLS-BI-0020	\N	dewar	DLS-BI-0020	72181		f
221	\N	{}	DLS-BI-0020	\N	dewar	DLS-BI-0020	\N		t
\.


--
-- Data for Name: alembic_version; Type: TABLE DATA; Schema: public; Owner: sample_handling
--

COPY public.alembic_version (version_num) FROM stdin;
2437fc6c6661
\.


--
-- Name: Container_containerId_seq; Type: SEQUENCE SET; Schema: public; Owner: sample_handling
--

SELECT pg_catalog.setval('public."Container_containerId_seq"', 1186, true);


--
-- Name: PreSession_preSessionId_seq; Type: SEQUENCE SET; Schema: public; Owner: sample_handling
--

SELECT pg_catalog.setval('public."PreSession_preSessionId_seq"', 188, true);


--
-- Name: Sample_sampleId_seq; Type: SEQUENCE SET; Schema: public; Owner: sample_handling
--

SELECT pg_catalog.setval('public."Sample_sampleId_seq"', 1032, true);


--
-- Name: Shipment_shipmentId_seq; Type: SEQUENCE SET; Schema: public; Owner: sample_handling
--

SELECT pg_catalog.setval('public."Shipment_shipmentId_seq"', 186, true);


--
-- Name: TopLevelContainer_topLevelContainerId_seq; Type: SEQUENCE SET; Schema: public; Owner: sample_handling
--

SELECT pg_catalog.setval('public."TopLevelContainer_topLevelContainerId_seq"', 399, true);


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
-- Name: PreSession PreSession_pkey; Type: CONSTRAINT; Schema: public; Owner: sample_handling
--

ALTER TABLE ONLY public."PreSession"
    ADD CONSTRAINT "PreSession_pkey" PRIMARY KEY ("preSessionId");


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
-- Name: TopLevelContainer TopLevelContainer_name_shipmentId_key; Type: CONSTRAINT; Schema: public; Owner: sample_handling
--

ALTER TABLE ONLY public."TopLevelContainer"
    ADD CONSTRAINT "TopLevelContainer_name_shipmentId_key" UNIQUE (name, "shipmentId");


--
-- Name: TopLevelContainer TopLevelContainer_pkey; Type: CONSTRAINT; Schema: public; Owner: sample_handling
--

ALTER TABLE ONLY public."TopLevelContainer"
    ADD CONSTRAINT "TopLevelContainer_pkey" PRIMARY KEY ("topLevelContainerId");


--
-- Name: alembic_version alembic_version_pkc; Type: CONSTRAINT; Schema: public; Owner: sample_handling
--

ALTER TABLE ONLY public.alembic_version
    ADD CONSTRAINT alembic_version_pkc PRIMARY KEY (version_num);


--
-- Name: Container uq_name_shipment; Type: CONSTRAINT; Schema: public; Owner: sample_handling
--

ALTER TABLE ONLY public."Container"
    ADD CONSTRAINT uq_name_shipment UNIQUE (name, "shipmentId");


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
-- Name: ix_PreSession_preSessionId; Type: INDEX; Schema: public; Owner: sample_handling
--

CREATE INDEX "ix_PreSession_preSessionId" ON public."PreSession" USING btree ("preSessionId");


--
-- Name: ix_PreSession_shipmentId; Type: INDEX; Schema: public; Owner: sample_handling
--

CREATE UNIQUE INDEX "ix_PreSession_shipmentId" ON public."PreSession" USING btree ("shipmentId");


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
-- Name: ix_Shipment_proposalCode; Type: INDEX; Schema: public; Owner: sample_handling
--

CREATE INDEX "ix_Shipment_proposalCode" ON public."Shipment" USING btree ("proposalCode");


--
-- Name: ix_Shipment_proposalNumber; Type: INDEX; Schema: public; Owner: sample_handling
--

CREATE INDEX "ix_Shipment_proposalNumber" ON public."Shipment" USING btree ("proposalNumber");


--
-- Name: ix_Shipment_shipmentId; Type: INDEX; Schema: public; Owner: sample_handling
--

CREATE INDEX "ix_Shipment_shipmentId" ON public."Shipment" USING btree ("shipmentId");


--
-- Name: ix_Shipment_visitNumber; Type: INDEX; Schema: public; Owner: sample_handling
--

CREATE INDEX "ix_Shipment_visitNumber" ON public."Shipment" USING btree ("visitNumber");


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
-- Name: PreSession PreSession_shipmentId_fkey; Type: FK CONSTRAINT; Schema: public; Owner: sample_handling
--

ALTER TABLE ONLY public."PreSession"
    ADD CONSTRAINT "PreSession_shipmentId_fkey" FOREIGN KEY ("shipmentId") REFERENCES public."Shipment"("shipmentId");


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


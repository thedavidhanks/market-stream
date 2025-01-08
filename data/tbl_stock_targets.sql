--
-- PostgreSQL database dump
--

-- Dumped from database version 16.4
-- Dumped by pg_dump version 16.4

-- Started on 2025-01-01 15:20:17

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

SET default_tablespace = '';

SET default_table_access_method = heap;

--
-- TOC entry 298 (class 1259 OID 32898)
-- Name: stock_targets; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.stock_targets (
    id integer NOT NULL,
    symbol text NOT NULL,
    weight real,
    last_modified timestamp with time zone,
    portfolio_id integer,
    type text
);


ALTER TABLE public.stock_targets OWNER TO postgres;

--
-- TOC entry 299 (class 1259 OID 32903)
-- Name: stock targets_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE public."stock targets_id_seq"
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public."stock targets_id_seq" OWNER TO postgres;

--
-- TOC entry 5353 (class 0 OID 0)
-- Dependencies: 299
-- Name: stock targets_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE public."stock targets_id_seq" OWNED BY public.stock_targets.id;


--
-- TOC entry 5180 (class 2604 OID 32913)
-- Name: stock_targets id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.stock_targets ALTER COLUMN id SET DEFAULT nextval('public."stock targets_id_seq"'::regclass);


--
-- TOC entry 5182 (class 2606 OID 32917)
-- Name: stock_targets stock targets_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.stock_targets
    ADD CONSTRAINT "stock targets_pkey" PRIMARY KEY (id);


--
-- TOC entry 5184 (class 2620 OID 32954)
-- Name: stock_targets sync_lastmod; Type: TRIGGER; Schema: public; Owner: postgres
--

CREATE TRIGGER sync_lastmod BEFORE UPDATE ON public.stock_targets FOR EACH ROW EXECUTE FUNCTION public.sync_lastmod();


--
-- TOC entry 5183 (class 2606 OID 32959)
-- Name: stock_targets portfolio_id_fk; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.stock_targets
    ADD CONSTRAINT portfolio_id_fk FOREIGN KEY (portfolio_id) REFERENCES public.portfolio_configs(id) NOT VALID;


-- Completed on 2025-01-01 15:20:17

--
-- PostgreSQL database dump complete
--


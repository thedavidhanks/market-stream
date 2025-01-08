--
-- PostgreSQL database dump
--

-- Dumped from database version 16.4
-- Dumped by pg_dump version 16.4

-- Started on 2025-01-01 13:18:42

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
-- TOC entry 7 (class 2615 OID 2200)
-- Name: public; Type: SCHEMA; Schema: -; Owner: pg_database_owner
--

CREATE SCHEMA public;


ALTER SCHEMA public OWNER TO pg_database_owner;

--
-- TOC entry 5384 (class 0 OID 0)
-- Dependencies: 7
-- Name: SCHEMA public; Type: COMMENT; Schema: -; Owner: pg_database_owner
--

COMMENT ON SCHEMA public IS 'standard public schema';


--
-- TOC entry 611 (class 1255 OID 32796)
-- Name: sync_lastmod(); Type: FUNCTION; Schema: public; Owner: postgres
--

CREATE FUNCTION public.sync_lastmod() RETURNS trigger
    LANGUAGE plpgsql
    AS $$
BEGIN
  NEW.last_modified := NOW();

  RETURN NEW;
END;
$$;


ALTER FUNCTION public.sync_lastmod() OWNER TO postgres;

SET default_tablespace = '';

SET default_table_access_method = heap;

--
-- TOC entry 278 (class 1259 OID 32797)
-- Name: stock_bars; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.stock_bars (
    "time" timestamp with time zone NOT NULL,
    symbol text NOT NULL,
    open double precision,
    high double precision,
    low double precision,
    close double precision,
    volume integer,
    trade_count integer,
    vwap double precision,
    adj_close double precision,
    "interval" integer
);


ALTER TABLE public.stock_bars OWNER TO postgres;

--
-- TOC entry 280 (class 1259 OID 32806)
-- Name: stock_trades_real_time; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.stock_trades_real_time (
    "time" timestamp with time zone NOT NULL,
    symbol text NOT NULL,
    price double precision,
    size integer,
    exchange text,
    trade_id text,
    conditions text
);


ALTER TABLE public.stock_trades_real_time OWNER TO postgres;

--
-- TOC entry 295 (class 1259 OID 32887)
-- Name: company; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.company (
    symbol text NOT NULL,
    name text NOT NULL
);


ALTER TABLE public.company OWNER TO postgres;

--
-- TOC entry 307 (class 1259 OID 41242)
-- Name: deposits; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.deposits (
    id integer NOT NULL,
    amount numeric(10,2) NOT NULL,
    portfolio_id integer NOT NULL,
    created_on timestamp with time zone DEFAULT CURRENT_TIMESTAMP NOT NULL
);


ALTER TABLE public.deposits OWNER TO postgres;

--
-- TOC entry 306 (class 1259 OID 41241)
-- Name: deposits_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE public.deposits_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.deposits_id_seq OWNER TO postgres;

--
-- TOC entry 5385 (class 0 OID 0)
-- Dependencies: 306
-- Name: deposits_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE public.deposits_id_seq OWNED BY public.deposits.id;


--
-- TOC entry 303 (class 1259 OID 41199)
-- Name: orders; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.orders (
    id uuid NOT NULL,
    client_order_id text,
    created_at timestamp with time zone,
    updated_at timestamp with time zone,
    filled_at timestamp with time zone,
    expired_at timestamp with time zone,
    failed_at timestamp with time zone,
    replaced_at timestamp with time zone,
    replaced_by uuid,
    replaces uuid,
    asset_id uuid,
    symbol text,
    asset_class text,
    notional text,
    qty text,
    filled_qty text,
    filled_avg_price text,
    order_class text,
    type text,
    side text,
    time_in_force text,
    limit_price text,
    stop_price text,
    status text,
    extended_hours boolean,
    trail_percent text,
    trail_price text,
    hwm text,
    portfolio_id integer,
    submitted_at time with time zone,
    order_type text,
    expected_price text
);


ALTER TABLE public.orders OWNER TO postgres;

--
-- TOC entry 5386 (class 0 OID 0)
-- Dependencies: 303
-- Name: TABLE orders; Type: COMMENT; Schema: public; Owner: postgres
--

COMMENT ON TABLE public.orders IS 'Represents a request for the sale or purchase of an asset.
Information about the columns can be found on Alpaca
https://alpaca.markets/sdks/python/api_reference/trading/models.html#alpaca.trading.models.Order';


--
-- TOC entry 5387 (class 0 OID 0)
-- Dependencies: 303
-- Name: COLUMN orders.expected_price; Type: COMMENT; Schema: public; Owner: postgres
--

COMMENT ON COLUMN public.orders.expected_price IS 'The price that was last seen before placing the order. Not an alpaca order field.';


--
-- TOC entry 296 (class 1259 OID 32892)
-- Name: portfolio_configs; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.portfolio_configs (
    id integer NOT NULL,
    name text NOT NULL,
    owner_id text,
    created_date timestamp with time zone,
    active boolean,
    model_name text,
    last_modified timestamp with time zone
);


ALTER TABLE public.portfolio_configs OWNER TO postgres;

--
-- TOC entry 297 (class 1259 OID 32897)
-- Name: portfolio configurations_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE public."portfolio configurations_id_seq"
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public."portfolio configurations_id_seq" OWNER TO postgres;

--
-- TOC entry 5388 (class 0 OID 0)
-- Dependencies: 297
-- Name: portfolio configurations_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE public."portfolio configurations_id_seq" OWNED BY public.portfolio_configs.id;


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
-- TOC entry 5389 (class 0 OID 0)
-- Dependencies: 299
-- Name: stock targets_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE public."stock targets_id_seq" OWNED BY public.stock_targets.id;


--
-- TOC entry 300 (class 1259 OID 32904)
-- Name: stock_bars_5min; Type: VIEW; Schema: public; Owner: postgres
--

CREATE VIEW public.stock_bars_5min AS
 SELECT bucket,
    symbol,
    open,
    high,
    low,
    close,
    volume
   FROM _timescaledb_internal._materialized_hypertable_3;


ALTER VIEW public.stock_bars_5min OWNER TO postgres;

--
-- TOC entry 301 (class 1259 OID 32908)
-- Name: stock_bars_5min_rt; Type: VIEW; Schema: public; Owner: postgres
--

CREATE VIEW public.stock_bars_5min_rt AS
 SELECT bucket,
    symbol,
    open,
    high,
    low,
    close,
    volume
   FROM _timescaledb_internal._materialized_hypertable_6;


ALTER VIEW public.stock_bars_5min_rt OWNER TO postgres;

--
-- TOC entry 5192 (class 2604 OID 41245)
-- Name: deposits id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.deposits ALTER COLUMN id SET DEFAULT nextval('public.deposits_id_seq'::regclass);


--
-- TOC entry 5190 (class 2604 OID 32912)
-- Name: portfolio_configs id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.portfolio_configs ALTER COLUMN id SET DEFAULT nextval('public."portfolio configurations_id_seq"'::regclass);


--
-- TOC entry 5191 (class 2604 OID 32913)
-- Name: stock_targets id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.stock_targets ALTER COLUMN id SET DEFAULT nextval('public."stock targets_id_seq"'::regclass);


--
-- TOC entry 5206 (class 2606 OID 41248)
-- Name: deposits deposits_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.deposits
    ADD CONSTRAINT deposits_pkey PRIMARY KEY (id);


--
-- TOC entry 5204 (class 2606 OID 41205)
-- Name: orders orders_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.orders
    ADD CONSTRAINT orders_pkey PRIMARY KEY (id);


--
-- TOC entry 5199 (class 2606 OID 32915)
-- Name: portfolio_configs portfolio configurations_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.portfolio_configs
    ADD CONSTRAINT "portfolio configurations_pkey" PRIMARY KEY (id);


--
-- TOC entry 5201 (class 2606 OID 32917)
-- Name: stock_targets stock targets_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.stock_targets
    ADD CONSTRAINT "stock targets_pkey" PRIMARY KEY (id);


--
-- TOC entry 5202 (class 1259 OID 41211)
-- Name: fki_portfolio_id_fk; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX fki_portfolio_id_fk ON public.orders USING btree (portfolio_id);


--
-- TOC entry 5194 (class 1259 OID 32940)
-- Name: ix_symbol_time; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX ix_symbol_time ON public.stock_bars USING btree (symbol, "time" DESC);


--
-- TOC entry 5196 (class 1259 OID 32941)
-- Name: ix_symbol_time_2; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX ix_symbol_time_2 ON public.stock_trades_real_time USING btree (symbol, "time" DESC);


--
-- TOC entry 5195 (class 1259 OID 32942)
-- Name: stock_bars_time_idx; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX stock_bars_time_idx ON public.stock_bars USING btree ("time" DESC);


--
-- TOC entry 5197 (class 1259 OID 32943)
-- Name: stocks_real_time_time_idx; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX stocks_real_time_time_idx ON public.stock_trades_real_time USING btree ("time" DESC);


--
-- TOC entry 5214 (class 2620 OID 32953)
-- Name: portfolio_configs sync_lastmod; Type: TRIGGER; Schema: public; Owner: postgres
--

CREATE TRIGGER sync_lastmod BEFORE UPDATE ON public.portfolio_configs FOR EACH ROW EXECUTE FUNCTION public.sync_lastmod();


--
-- TOC entry 5215 (class 2620 OID 32954)
-- Name: stock_targets sync_lastmod; Type: TRIGGER; Schema: public; Owner: postgres
--

CREATE TRIGGER sync_lastmod BEFORE UPDATE ON public.stock_targets FOR EACH ROW EXECUTE FUNCTION public.sync_lastmod();


--
-- TOC entry 5210 (class 2620 OID 32955)
-- Name: stock_bars ts_cagg_invalidation_trigger; Type: TRIGGER; Schema: public; Owner: postgres
--

CREATE TRIGGER ts_cagg_invalidation_trigger AFTER INSERT OR DELETE OR UPDATE ON public.stock_bars FOR EACH ROW EXECUTE FUNCTION _timescaledb_functions.continuous_agg_invalidation_trigger('1');


--
-- TOC entry 5212 (class 2620 OID 32956)
-- Name: stock_trades_real_time ts_cagg_invalidation_trigger; Type: TRIGGER; Schema: public; Owner: postgres
--

CREATE TRIGGER ts_cagg_invalidation_trigger AFTER INSERT OR DELETE OR UPDATE ON public.stock_trades_real_time FOR EACH ROW EXECUTE FUNCTION _timescaledb_functions.continuous_agg_invalidation_trigger('5');


--
-- TOC entry 5211 (class 2620 OID 32957)
-- Name: stock_bars ts_insert_blocker; Type: TRIGGER; Schema: public; Owner: postgres
--

CREATE TRIGGER ts_insert_blocker BEFORE INSERT ON public.stock_bars FOR EACH ROW EXECUTE FUNCTION _timescaledb_functions.insert_blocker();


--
-- TOC entry 5213 (class 2620 OID 32958)
-- Name: stock_trades_real_time ts_insert_blocker; Type: TRIGGER; Schema: public; Owner: postgres
--

CREATE TRIGGER ts_insert_blocker BEFORE INSERT ON public.stock_trades_real_time FOR EACH ROW EXECUTE FUNCTION _timescaledb_functions.insert_blocker();


--
-- TOC entry 5209 (class 2606 OID 41249)
-- Name: deposits deposits_portfolio_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.deposits
    ADD CONSTRAINT deposits_portfolio_id_fkey FOREIGN KEY (portfolio_id) REFERENCES public.portfolio_configs(id);


--
-- TOC entry 5207 (class 2606 OID 32959)
-- Name: stock_targets portfolio_id_fk; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.stock_targets
    ADD CONSTRAINT portfolio_id_fk FOREIGN KEY (portfolio_id) REFERENCES public.portfolio_configs(id) NOT VALID;


--
-- TOC entry 5208 (class 2606 OID 41206)
-- Name: orders portfolio_id_fk; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.orders
    ADD CONSTRAINT portfolio_id_fk FOREIGN KEY (portfolio_id) REFERENCES public.portfolio_configs(id) ON DELETE RESTRICT NOT VALID;


-- Completed on 2025-01-01 13:18:43

--
-- PostgreSQL database dump complete
--


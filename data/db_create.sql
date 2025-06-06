--
-- Create database and tables for ML Market Data
--


--
-- TOC entry 278 (class 1259 OID 32797)
-- Name: stock_bars; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE IF NOT EXISTS public.stock_bars (
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

-- Create a hypertable for stock_bars
SELECT create_hypertable('stock_bars', 'time', if_not_exists => TRUE);
CREATE TRIGGER ts_cagg_invalidation_trigger AFTER INSERT OR DELETE OR UPDATE ON public.stock_bars FOR EACH ROW EXECUTE FUNCTION _timescaledb_functions.continuous_agg_invalidation_trigger('1');
DROP TRIGGER IF EXISTS ts_insert_blocker ON public.stock_bars;
CREATE TRIGGER ts_insert_blocker BEFORE INSERT ON public.stock_bars FOR EACH ROW EXECUTE FUNCTION _timescaledb_functions.insert_blocker();

--
-- TOC entry 280 (class 1259 OID 32806)
-- Name: stock_trades_real_time; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE  IF NOT EXISTS public.stock_trades_real_time (
    "time" timestamp with time zone NOT NULL,
    symbol text NOT NULL,
    price double precision,
    size integer,
    exchange text,
    trade_id text,
    conditions text
);


-- Make stock_trades_real_time it a hypertable
SELECT create_hypertable('stock_trades_real_time', 'time', if_not_exists => TRUE, chunk_time_interval => INTERVAL '1 day');
CREATE TRIGGER ts_cagg_invalidation_trigger AFTER INSERT OR DELETE OR UPDATE ON public.stock_trades_real_time FOR EACH ROW EXECUTE FUNCTION _timescaledb_functions.continuous_agg_invalidation_trigger('5');
DROP TRIGGER IF EXISTS ts_insert_blocker ON public.stock_trades_real_time;
CREATE TRIGGER ts_insert_blocker BEFORE INSERT ON public.stock_trades_real_time FOR EACH ROW EXECUTE FUNCTION _timescaledb_functions.insert_blocker();

--
-- TOC entry 295 (class 1259 OID 32887)
-- Name: company; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE IF NOT EXISTS  public.company (
    symbol text NOT NULL,
    name text NOT NULL
);

--
-- TOC entry 307 (class 1259 OID 41242)
-- Name: deposits; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE IF NOT EXISTS public.deposits (
    id integer NOT NULL,
    amount numeric(10,2) NOT NULL,
    portfolio_id integer NOT NULL,
    created_on timestamp with time zone DEFAULT CURRENT_TIMESTAMP NOT NULL
);

CREATE SEQUENCE public.deposits_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;
ALTER SEQUENCE public.deposits_id_seq OWNED BY public.deposits.id;

--
-- TOC entry 303 (class 1259 OID 41199)
-- Name: orders; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE IF NOT EXISTS  public.orders (
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
    
COMMENT ON TABLE public.orders IS 'Represents a request for the sale or purchase of an asset.
Information about the columns can be found on Alpaca
https://alpaca.markets/sdks/python/api_reference/trading/models.html#alpaca.trading.models.Order';
COMMENT ON COLUMN public.orders.expected_price IS 'The price that was last seen before placing the order. Not an alpaca order field.';


--
-- TOC entry 296 (class 1259 OID 32892)
-- Name: portfolio_configs; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE IF NOT EXISTS public.portfolio_configs (
    id serial NOT NULL,
    name text NOT NULL,
    owner_id text,
    created_date timestamp with time zone DEFAULT NOW(),
    active boolean,
    model_name text,
    last_modified timestamp with time zone
);

ALTER TABLE ONLY public.portfolio_configs
    ADD CONSTRAINT "portfolio configurations_pkey" PRIMARY KEY (id);
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
ALTER SEQUENCE public."portfolio configurations_id_seq" OWNED BY public.portfolio_configs.id;

--
-- TOC entry 298 (class 1259 OID 32898)
-- Name: stock_targets; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE IF NOT EXISTS public.stock_targets (
    id serial NOT NULL,
    symbol text NOT NULL,
    weight real,
    last_modified timestamp with time zone,
    portfolio_id integer REFERENCES public.portfolio_configs(id),
    type text
);

ALTER TABLE ONLY public.stock_targets
    ADD CONSTRAINT "stock targets_pkey" PRIMARY KEY (id);
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
ALTER SEQUENCE public."stock targets_id_seq" OWNED BY public.stock_targets.id;

-- Create the sync_lastmod trigger function
CREATE OR REPLACE FUNCTION public.sync_lastmod()
RETURNS trigger AS $$
BEGIN
    NEW.last_modified := NOW();
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

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

DROP INDEX IF EXISTS stock_bars_time_idx;
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
DROP TRIGGER IF EXISTS ts_cagg_invalidation_trigger ON public.stock_bars;
CREATE TRIGGER ts_cagg_invalidation_trigger AFTER INSERT OR DELETE OR UPDATE ON public.stock_bars FOR EACH ROW EXECUTE FUNCTION _timescaledb_functions.continuous_agg_invalidation_trigger('1');


--
-- TOC entry 5212 (class 2620 OID 32956)
-- Name: stock_trades_real_time ts_cagg_invalidation_trigger; Type: TRIGGER; Schema: public; Owner: postgres
--
DROP TRIGGER IF EXISTS ts_cagg_invalidation_trigger ON public.stock_trades_real_time; 
CREATE TRIGGER ts_cagg_invalidation_trigger AFTER INSERT OR DELETE OR UPDATE ON public.stock_trades_real_time FOR EACH ROW EXECUTE FUNCTION _timescaledb_functions.continuous_agg_invalidation_trigger('5');


--
-- TOC entry 5211 (class 2620 OID 32957)
-- Name: stock_bars ts_insert_blocker; Type: TRIGGER; Schema: public; Owner: postgres
--
DROP TRIGGER IF EXISTS ts_insert_blocker ON public.stock_bars;
CREATE TRIGGER ts_insert_blocker BEFORE INSERT ON public.stock_bars FOR EACH ROW EXECUTE FUNCTION _timescaledb_functions.insert_blocker();


--
-- TOC entry 5213 (class 2620 OID 32958)
-- Name: stock_trades_real_time ts_insert_blocker; Type: TRIGGER; Schema: public; Owner: postgres
--
DROP TRIGGER IF EXISTS ts_insert_blocker ON public.stock_trades_real_time;
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


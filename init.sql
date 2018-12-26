CREATE DATABASE kostal;

-- Table: public.pvwr

-- DROP TABLE public.pvwr;

CREATE TABLE public.pvwr
(
    id bigint NOT NULL DEFAULT nextval('pvwr_id_seq'::regclass),
    "timestamp" timestamp with time zone NOT NULL DEFAULT CURRENT_TIMESTAMP,
    pv_generator_dc_input_1_voltage numeric NOT NULL,
    pv_generator_dc_input_1_current numeric NOT NULL,
    pv_generator_dc_input_1_power numeric NOT NULL,
    house_home_consumption_covered_by_solar_generator numeric NOT NULL,
    house_home_consumption_covered_by_grid numeric NOT NULL,
    house_phase_selective_home_consumption_phase_1 numeric NOT NULL,
    house_phase_selective_home_consumption_phase_2 numeric NOT NULL,
    house_phase_selective_home_consumption_phase_3 numeric NOT NULL,
    grid_grid_parameters_output_power numeric NOT NULL,
    grid_grid_parameters_grid_frequency numeric NOT NULL,
    grid_grid_parameters_cos numeric NOT NULL,
    grid_phase_1_voltage numeric NOT NULL,
    grid_phase_1_current numeric NOT NULL,
    grid_phase_1_power numeric NOT NULL,
    grid_phase_2_voltage numeric NOT NULL,
    grid_phase_2_current numeric NOT NULL,
    grid_phase_2_power numeric NOT NULL,
    grid_phase_3_voltage numeric NOT NULL,
    grid_phase_3_current numeric NOT NULL,
    grid_phase_3_power numeric NOT NULL,
    stats_total_yield numeric NOT NULL,
    stats_total_operation_time numeric NOT NULL,
    stats_total_total_home_consumption numeric NOT NULL,
    stats_total_self_consumption_kwh numeric NOT NULL,
    stats_total_self_consumption_rate numeric NOT NULL,
    stats_total_degree_of_self_sufficiency numeric NOT NULL,
    stats_day_yield numeric NOT NULL,
    stats_day_total_home_consumption numeric NOT NULL,
    stats_day_self_consumption_kwh numeric NOT NULL,
    stats_day_self_consumption_rate numeric NOT NULL,
    stats_day_degree_of_self_sufficiency numeric NOT NULL,
    CONSTRAINT pvwr_pkey PRIMARY KEY (id)
)
WITH (
    OIDS = FALSE
)
TABLESPACE pg_default;

ALTER TABLE public.pvwr
    OWNER to postgres;

GRANT SELECT ON TABLE public.pvwr TO grafanareader;

GRANT ALL ON TABLE public.pvwr TO postgres;

-- I contain all of the create table statements
-- create database
-- create all tables
-- create user?
CREATE DATABASE IF NOT EXISTS all_ears;

CREATE TABLE IF NOT EXISTS all_ears.elephantcarcasses
(
    un_region         char(25)  not null,
    subregion_name    char(50)  not null,
    subregion_id      char(2)   not null,
    country_name      char(100) not null,
    country_code      char(2)   not null,
    mike_site_id      char(3)   not null,
    mike_site_name    char(100) not null,
    mike_year         int       not null,
    carcasses         int       not null,
    illegal_carcasses int       not null,
    PRIMARY KEY (mike_site_id, mike_year)
);

-- Alter username, host, and password to fit db setup desire
CREATE USER IF NOT EXISTS 'admin'@'localhost' IDENTIFIED BY 'password';

GRANT ALL PRIVILEGES on all_ears.* TO 'admin'@'localhost';
FLUSH PRIVILEGES;


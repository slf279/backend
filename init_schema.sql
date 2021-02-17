-- I contain all of the create table statements
-- create database
-- create all tables
-- create user?
CREATE DATABASE IF NOT EXISTS all_ears;

CREATE TABLE IF NOT EXISTS all_ears.elephantcarcasses(
	un_region char(25),
	subregion_name char(50),
	subregion_id char(2),
	country_name char(100),
	country_code char(2),
	mike_site_id char(3),
	mike_site_name char(100),
	mike_year int,
	total_number_of_carcasses int,
	number_of_illegal_carcasses int,
	PRIMARY KEY(mike_site_id, mike_year)
);

CREATE TABLE IF NOT EXISTS all_ears.countrycarcasses(
	country_code char(2),
	mike_site_id char(3),
	total_carcasses int,
	total_illegal_carcasses int,
	PRIMARY KEY(country_code),
	FOREIGN KEY(mike_site_id) REFERENCES all_ears.elephantcarcasses(mike_site_id)
);

-- Alter username, host, and password to fit db setup desire
CREATE USER IF NOT EXISTS 'admin'@'localhost' IDENTIFIED BY 'password';

GRANT ALL PRIVILEGES on all_ears.* TO 'admin'@'localhost';
FLUSH PRIVILEGES;


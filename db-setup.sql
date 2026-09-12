-- Run as yieldseeker_admin
CREATE DATABASE barbelldb;
CREATE ROLE barbell_admin LOGIN PASSWORD '<choose-a-strong-password>';
GRANT CONNECT ON DATABASE barbelldb TO barbell_admin;
GRANT USAGE, CREATE ON SCHEMA public TO barbell_admin;

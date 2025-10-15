-- db/create_db.sql

-- Ask for a local password at run time (psql meta-command; not stored in Git)
\prompt 'Enter a password for role "admin": ' admin_pass

DO
$$
BEGIN
    IF NOT EXISTS (SELECT FROM pg_roles WHERE rolname = 'admin') THEN
        -- Use the prompted password safely
        EXECUTE format('CREATE ROLE admin WITH LOGIN PASSWORD %L', :'admin_pass');
        ALTER ROLE admin CREATEDB;
        RAISE NOTICE 'Created role "admin".';
    ELSE
        RAISE NOTICE 'Role "admin" already exists.';
    END IF;
END
$$;

DROP DATABASE IF EXISTS hustlehub;
CREATE DATABASE hustlehub WITH OWNER = admin ENCODING 'UTF8' TEMPLATE template0;

\connect hustlehub;

CREATE SCHEMA IF NOT EXISTS public AUTHORIZATION admin;
GRANT ALL ON SCHEMA public TO admin;
GRANT USAGE ON SCHEMA public TO public;
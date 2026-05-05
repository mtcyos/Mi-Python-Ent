-- Compatible con : SQLite, MariaDB, PostgreSQL, MsSQL (Win, Linux, Mac)
-- Tabla : Bdt - Bases de Datos
-- Ord Principal : cSvr
-- Clave Busqueda : cSvr
CREATE TABLE "Bdt" (
    "cSvr"       VARCHAR(9),    -- Servidor
    "cSvrTip"    VARCHAR(10),   -- Tipo de Servidor: SQLite, PostgreSQL, MariaDB, MSSQL, Ach, Dbf
    "cDir"       VARCHAR(100),  -- Ruta, IP o DNS
    "cUsr"       VARCHAR(25),   -- Usuario de acceso
    "cPas"       VARCHAR(25),   -- Contraseña (cifrada o plana)
    "cBdt"       VARCHAR(20),   -- Nombre de la Base de Datos
    "cObs"       VARCHAR(100),  -- Observaciones
    "cObsSis"    VARCHAR(100),  -- Observaciones Sistema
    "cModRegNik" VARCHAR(20),   -- Ultima Modificacion Nick
    "cModRegTim" VARCHAR(20)    -- Ultima Modificacion Timestamp (aaaa-mm-dd hh:mm:ss)
);

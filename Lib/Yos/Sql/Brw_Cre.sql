-- Compatible con : SQLite, MariaDB, PostgreSQL, MsSQL (Win, Linux, Mac)
-- Tabla : Brw - Browses
-- Ord Principal : cTab + cCod + cNum
-- Clave Busqueda : cTab + cCod
CREATE TABLE "Brw" (
    "cTab"          VARCHAR(20),    -- Tabla
    "cCod"          VARCHAR(25),    -- Código (Main, etc.)
    "cNum"          VARCHAR(3),     -- Nº Orden 00n
    "cCab"          VARCHAR(50),    -- Cabecera que verá el usuario
    "cLon"          VARCHAR(4),     -- Longitud (en caracteres o %)
    "cClm"          VARCHAR(20),    -- Columna de la tabla
    "cObs"          VARCHAR(100),   -- Observaciones
    "cObsSis"       VARCHAR(100),   -- Observaciones Sistema
    "cModRegNik"    VARCHAR(20),    -- Ultima Modificacion Nick
    "cModRegTim"    VARCHAR(20))    -- Ultima Modificacion Timestamp (aaaa-mm-dd hh:mm:ss)

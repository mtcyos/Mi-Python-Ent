-- Compatible con : SQLite, MariaDB, PostgreSQL, MsSQL (Win, Linux, Mac)
-- Tabla : Ord - Ordenes de las Tablas
-- Ord Principal : cTab + cNum
-- Clave Busqueda :cTab
CREATE TABLE "Ord" (
    "cTab"          VARCHAR(20),    -- Tabla
    "cNum"          VARCHAR(3),     -- Nº Orden 00n
    "cTxt"          VARCHAR(50),
    "cCmd"          VARCHAR(200),
    "cObs"          VARCHAR(100),  -- Observaciones
    "cObsSis"       VARCHAR(100),   -- Observaciones Sistema
    "cModRegNik"    VARCHAR(20),   -- Ultima Modificacion Nick
    "cModRegTim"    VARCHAR(20))   -- Ultima Modificacion Timestamp (aaaa-mm-dd hh:mm:ss)

-- Compatible con : SQLite, MariaDB, PostgreSQL, MsSQL (Win, Linux, Mac)
-- Tabla : ClmMod - Columnas a Modificar
-- Ord Principal : cTab + cCod + cNum
-- Clave Busqueda : cTab + cCod
CREATE TABLE "ClmMod" (
    "cTab"          VARCHAR(20),    -- Tabla
    "cCod"          VARCHAR(25),    -- Código (Main, etc.)
    "cNum"          VARCHAR(3),     -- Nº Orden 00n
    "cClm"          VARCHAR(20),    -- Columna de la tabla
    "cCab"          VARCHAR(50),    -- Cabecera que verá el usuario
    "cMod"          VARCHAR(3),     -- Permisos (Mod/Cre=Solo se Modifica en Creacion)
    "cNul"          VARCHAR(1),     -- Admite Nulos (/N)
    "cOpc"          VARCHAR(100),   -- Lista de Opciones
    "cObs"          VARCHAR(100),   -- Observaciones
    "cObsSis"       VARCHAR(100),   -- Observaciones Sistema
    "cModRegNik"    VARCHAR(20),    -- Ultima Modificacion Nick
    "cModRegTim"    VARCHAR(20))    -- Ultima Modificacion Timestamp (aaaa-mm-dd hh:mm:ss)

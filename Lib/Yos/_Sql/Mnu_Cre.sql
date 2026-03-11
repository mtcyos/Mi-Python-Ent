-- Compatible con : SQLite, MariaDB, PostgreSQL, MsSQL (Win, Linux, Mac)
-- Tabla : Mnu - Menus
-- Ord Principal : cMnu + cNum
-- Clave Busqueda : cMnu
CREATE TABLE "Mnu" (
    "cMnu"          VARCHAR(25),    -- Nombre del Menu
    "cNum"          VARCHAR(3),     -- Nº Orden 00n
    "cTip"          VARCHAR(3),     -- Tipo (Opc/Cab)
    "cEtn"          VARCHAR(10),    -- Entorno (/Win/Linux/Darwin)
    "cTxt"          VARCHAR(50),    -- Texto de Opción
    "cFnc"          VARCHAR(200),   -- Función/Acción
    "cObs"          VARCHAR(100),   -- Observaciones
    "cModRegNik"    VARCHAR(20),    -- Ultima Modificacion Nick
    "cModRegTim"    VARCHAR(20))    -- Ultima Modificacion Timestamp (aaaa-mm-dd hh:mm:ss)

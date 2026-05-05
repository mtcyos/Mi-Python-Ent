-- Compatible con : SQLite, MariaDB, PostgreSQL, MsSQL (Win, Linux, Mac)
-- Tabla : Mnu - Menus
-- Ord Principal : cMnu + cNum
-- Clave Busqueda : cMnu

CREATE TABLE "Mnu" (
    "cNul"   VARCHAR(1),   -- Opción Nula (/s)
    "cMnu"   VARCHAR(20),  -- Nombre del Menu / Aplicacion
    "cNumOrd"    VARCHAR(4),   -- Nº Orden 000n
    "cNueOrd"    VARCHAR(4),   -- Nº Orden 000n PARA RENUMERAR
    "cMnuCod"    VARCHAR(12),  -- Tipo de linea del Menu (IniPop/MnuIte/EndPop/MnuSub/Sep)
    "cDes"   VARCHAR(100), -- Texto de Opción
    "cFnc"   VARCHAR(253), -- Función/Acción
    "cEtn"   VARCHAR(10),  -- Entorno (/Windows,Linux,Darwin)
    "cObs"   VARCHAR(100), -- Observaciones
    "cObsSis"    VARCHAR(100), -- Observaciones
    "cModRegNik" TEXT(20),     -- Ultima Modificacion Nick
    "cModRegTim" TEXT(20)      -- Ultima Modificacion Timestamp (aaaa-mm-dd hh:mm:ss)
);

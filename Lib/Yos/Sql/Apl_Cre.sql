-- Compatible con : SQLite, MariaDB, PostgreSQL, MsSQL (Win, Linux, Mac)
-- Tabla : Apl - Aplicaciones
-- Ord Principal : cNom
-- Clave Busqueda : cNom (Normalmente es de un solo Registro en YosCfg)
CREATE TABLE "Apl" (
    "cNom"          VARCHAR(60),    -- Nombre de la Aplicación
    "cEtnApl"       VARCHAR(3),     -- Entorno (Txt/Gui)
    "cEtnAplLet"    VARCHAR(25),    -- Letra o Estilo del Entorno
    "cVsn"          VARCHAR(8),     -- Versión aaaa.mm
    "cCpy"          VARCHAR(50),    -- Copyrigh
    "cCpyEml"       VARCHAR(50),    -- Email de soporte/autor
    "cObs"          VARCHAR(100),   -- Observaciones
    "cObsSis"       VARCHAR(100),   -- Observaciones Sistema
    "cModRegNik"    VARCHAR(20),    -- Ultima Modificacion Nick
    "cModRegTim"    VARCHAR(20))    -- Ultima Modificacion Timestamp (aaaa-mm-dd hh:mm:ss)

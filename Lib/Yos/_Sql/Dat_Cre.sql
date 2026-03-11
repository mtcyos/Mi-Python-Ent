-- Compatible con : SQLite, MariaDB, PostgreSQL, MsSQL (Win, Linux, Mac)
-- Tabla : Dat - Datos para la Aplicacion
-- Ord Principal : cNom
-- Clave Busqueda : cNom
CREATE TABLE "Dat" (
    "cNom"          VARCHAR(60),    -- Nombre de la Variable (Eml_Svr, etc.)
    "cDes"          VARCHAR(100),   -- Descripción
    "cTipClm"       VARCHAR(1),     -- Tipo (c=Char, n=Num, d=Fehca, l=Logica)
    "cVal"          VARCHAR(253),   -- Valor de la variable
    "cValPmd"       VARCHAR(100),   -- Valor por defecto
    "cLonClm"       VARCHAR(3),     -- Longitud para justificar a la derecha con espacio
    "cAli"          VARCHAR(1),     -- Alineación (/C/D)
    "cObs"          VARCHAR(100),   -- Observaciones
    "cObsSis"       VARCHAR(100),   -- Observaciones Sistema
    "cModRegNik"    VARCHAR(20),    -- Ultima Modificacion Nick
    "cModRegTim"    VARCHAR(20))    -- Ultima Modificacion Timestamp (aaaa-mm-dd hh:mm:ss)

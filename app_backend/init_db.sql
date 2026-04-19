CREATE DATABASE IF NOT EXISTS partidos_data_base;
USE partidos_data_base;

DROP TABLE IF EXISTS partidos_mundial;

CREATE TABLE IF NOT EXISTS partidos_mundial(
    id INT AUTO_INCREMENT PRIMARY KEY ,
    fecha DATE,
    equipo_local VARCHAR(50),
    equipo_visitante VARCHAR(50),
    fase VARCHAR(30),
    goles_local INT,
    goles_visitante INT
);



DROP TABLE IF EXISTS usuarios;

CREATE TABLE IF NOT EXISTS usuarios (

    id INT AUTO_INCREMENT PRIMARY KEY,
    nombre VARCHAR(100) NOT NULL,
    email VARCHAR(100) NOT NULL UNIQUE

);

CREATE TABLE IF NOT EXISTS predicciones(
    id_prediccion INT AUTO_INCREMENT PRIMARY KEY,
    id_partido INT NOT NULL,
    id_usuario INT NOT NULL,
    goles_local INT NOT NULL,
    goles_visitante INT NOT NULL
);


INSERT INTO partidos_mundial (fecha, equipo_local, equipo_visitante, fase) VALUES
('2026-06-11', 'México', 'Sudáfrica', 'GRUPOS'),
('2026-06-11', 'Corea del Sur', 'República Checa', 'GRUPOS'),
('2026-06-12', 'Canadá', 'Bosnia y Herzegovina', 'GRUPOS'),
('2026-06-12', 'Estados Unidos', 'Paraguay', 'GRUPOS'),
('2026-06-13', 'Catar', 'Suiza', 'GRUPOS'),
('2026-06-13', 'Brasil', 'Marruecos', 'GRUPOS'),
('2026-06-13', 'Haití', 'Escocia', 'GRUPOS'),
('2026-06-14', 'Australia', 'Turquía', 'GRUPOS'),
('2026-06-14', 'Alemania', 'Curazao', 'GRUPOS'),
('2026-06-14', 'Países Bajos', 'Japón', 'GRUPOS'),
('2026-06-14', 'Costa de Marfil', 'Ecuador', 'GRUPOS'),
('2026-06-14', 'Suecia', 'Túnez', 'GRUPOS'),
('2026-06-15', 'España', 'Islas de Cabo Verde', 'GRUPOS'),
('2026-06-15', 'Bélgica', 'Egipto', 'GRUPOS'),
('2026-06-15', 'Arabia Saudí', 'Uruguay', 'GRUPOS'),
('2026-06-15', 'República Islámica de Irán', 'Nueva Zelanda', 'GRUPOS'),
('2026-06-16', 'Francia', 'Senegal', 'GRUPOS'),
('2026-06-16', 'Irak', 'Noruega', 'GRUPOS'),
('2026-06-16', 'Argentina', 'Argelia', 'GRUPOS'),
('2026-06-17', 'Austria', 'Jordania', 'GRUPOS'),
('2026-06-17', 'Portugal', 'República Democrática del Congo', 'GRUPOS'),
('2026-06-17', 'Inglaterra', 'Croacia', 'GRUPOS'),
('2026-06-17', 'Ghana', 'Panamá', 'GRUPOS'),
('2026-06-17', 'Uzbekistán', 'Colombia', 'GRUPOS'),
('2026-06-18', 'República Checa', 'Sudáfrica', 'GRUPOS'),
('2026-06-18', 'Suiza', 'Bosnia y Herzegovina', 'GRUPOS'),
('2026-06-18', 'Canadá', 'Catar', 'GRUPOS'),
('2026-06-18', 'México', 'Corea del Sur', 'GRUPOS'),
('2026-06-19', 'Estados Unidos', 'Australia', 'GRUPOS'),
('2026-06-19', 'Escocia', 'Marruecos', 'GRUPOS'),
('2026-06-19', 'Brasil', 'Haití', 'GRUPOS'),
('2026-06-20', 'Turquía', 'Paraguay', 'GRUPOS'),
('2026-06-20', 'Países Bajos', 'Suecia', 'GRUPOS'),
('2026-06-20', 'Alemania', 'Costa de Marfil', 'GRUPOS'),
('2026-06-20', 'Ecuador', 'Curazao', 'GRUPOS'),
('2026-06-21', 'Túnez', 'Japón', 'GRUPOS'),
('2026-06-21', 'España', 'Arabia Saudí', 'GRUPOS'),
('2026-06-21', 'Bélgica', 'República Islámica de Irán', 'GRUPOS'),
('2026-06-21', 'Uruguay', 'Islas de Cabo Verde', 'GRUPOS'),
('2026-06-21', 'Nueva Zelanda', 'Egipto', 'GRUPOS'),
('2026-06-22', 'Argentina', 'Austria', 'GRUPOS'),
('2026-06-22', 'Francia', 'Irak', 'GRUPOS'),
('2026-06-22', 'Noruega', 'Senegal', 'GRUPOS'),
('2026-06-23', 'Jordania', 'Argelia', 'GRUPOS'),
('2026-06-23', 'Portugal', 'Uzbekistán', 'GRUPOS'),
('2026-06-23', 'Inglaterra', 'Ghana', 'GRUPOS'),
('2026-06-23', 'Panamá', 'Croacia', 'GRUPOS'),
('2026-06-23', 'Colombia', 'República Democrática del Congo', 'GRUPOS'),
('2026-06-24', 'Suiza', 'Canadá', 'GRUPOS'),
('2026-06-24', 'Bosnia y Herzegovina', 'Catar', 'GRUPOS'),
('2026-06-24', 'Escocia', 'Brasil', 'GRUPOS'),
('2026-06-24', 'Marruecos', 'Haití', 'GRUPOS'),
('2026-06-24', 'República Checa', 'México', 'GRUPOS'),
('2026-06-24', 'Sudáfrica', 'Corea del Sur', 'GRUPOS'),
('2026-06-25', 'Curazao', 'Costa de Marfil', 'GRUPOS'),
('2026-06-25', 'Ecuador', 'Alemania', 'GRUPOS'),
('2026-06-25', 'Japón', 'Suecia', 'GRUPOS'),
('2026-06-25', 'Túnez', 'Países Bajos', 'GRUPOS'),
('2026-06-25', 'Turquía', 'Estados Unidos', 'GRUPOS'),
('2026-06-25', 'Paraguay', 'Australia', 'GRUPOS'),
('2026-06-26', 'Noruega', 'Francia', 'GRUPOS'),
('2026-06-26', 'Senegal', 'Irak', 'GRUPOS'),
('2026-06-26', 'Islas de Cabo Verde', 'Arabia Saudí', 'GRUPOS'),
('2026-06-26', 'Uruguay', 'España', 'GRUPOS'),
('2026-06-27', 'Egipto', 'República Islámica de Irán', 'GRUPOS'),
('2026-06-27', 'Nueva Zelanda', 'Bélgica', 'GRUPOS'),
('2026-06-27', 'Panamá', 'Inglaterra', 'GRUPOS'),
('2026-06-27', 'Croacia', 'Ghana', 'GRUPOS'),
('2026-06-27', 'Colombia', 'Portugal', 'GRUPOS'),
('2026-06-27', 'República Democrática del Congo', 'Uzbekistán', 'GRUPOS'),
('2026-06-27', 'Argelia', 'Austria', 'GRUPOS'),
('2026-06-27', 'Jordania', 'Argentina', 'GRUPOS');

-- phpMyAdmin SQL Dump
-- version 5.2.1
-- https://www.phpmyadmin.net/
--
-- Servidor: 127.0.0.1
-- Tiempo de generación: 09-05-2024 a las 15:32:30
-- Versión del servidor: 10.4.32-MariaDB
-- Versión de PHP: 8.2.12

SET SQL_MODE = "NO_AUTO_VALUE_ON_ZERO";
START TRANSACTION;
SET time_zone = "+00:00";


/*!40101 SET @OLD_CHARACTER_SET_CLIENT=@@CHARACTER_SET_CLIENT */;
/*!40101 SET @OLD_CHARACTER_SET_RESULTS=@@CHARACTER_SET_RESULTS */;
/*!40101 SET @OLD_COLLATION_CONNECTION=@@COLLATION_CONNECTION */;
/*!40101 SET NAMES utf8mb4 */;

--
-- Base de datos: `boolings`
--

-- --------------------------------------------------------

--
-- Estructura de tabla para la tabla `bookings`
CREATE DATABASE IF NOT EXISTS boolings;
USE boolings;



CREATE TABLE `bookings` (
  `id` int(11) NOT NULL,
  `id_user` int(11) NOT NULL,
  `id_event` int(11) NOT NULL,
  `name_client` varchar(255) NOT NULL,
  `date` varchar(255) NOT NULL,
  `number_of_reserved_tickets` int(255) NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

--
-- Volcado de datos para la tabla `bookings`
--

INSERT INTO `bookings` (`id`, `id_user`, `id_event`, `name_client`, `date`, `number_of_reserved_tickets`) VALUES
(1, 0, 8, 'Braynel', '2024-12-02', 1),
(2, 5, 5, 'Juana', '2024-01-01', 1),
(3, 5, 5, 'Juana', '2024-01-01', 1),
(4, 5, 5, 'Juana', '2024-01-31', 1),
(5, 5, 5, 'Juana', '2024-01-31', 1),
(6, 5, 5, 'Juana', '2024-01-31', 1),
(7, 5, 5, 'Juana', '2024-01-01', 1),
(8, 8, 8, 'Jose', '2024-12-01', 2),
(9, 26, 26, 'Rijo', '2024-01-31', 2),
(10, 6, 6, 'Ariadna', '2024-01-31', 2),
(11, 40, 40, 'Jose', '2024-12-01', 2),
(12, 13, 13, 'Francisco', '2024-12-01', 4),
(13, 10, 10, 'Carlos', '2022-01-31', 1),
(14, 22, 22, 'Jeremy', '2024-12-02', 1),
(15, 22, 22, 'Jose', '2024-08-31', 2),
(16, 22, 22, 'Jose', '2024-08-31', 2),
(17, 22, 22, 'Jeremy', '2024-12-02', 1),
(18, 22, 22, 'Jeremy', '2024-12-02', 1),
(19, 19, 19, 'Josea', '2024-12-01', 1),
(20, 24, 24, 'Camila Rodriguez', '2024-06-12', 1),
(21, 7, 7, 'Braynel', '2024-07-12', 1),
(22, 1, 1, 'Juan', '2024-05-15', 1),
(23, 1, 1, '1111', '2024-05-15', 1),
(24, 14, 14, 'Braynel', '2024-10-10', 1),
(25, 5, 5, 'Jose', '2024-06-18', 10),
(26, 14, 14, 'bbba', '2024-10-10', 3),
(27, 14, 14, 'bbba', '2024-10-10', 3),
(28, 14, 14, 'bbba', '2024-10-10', 3),
(29, 14, 14, 'Josea', '2024-10-10', 2),
(30, 29, 29, 'Braynel', '2024-07-18', 2),
(31, 25, 25, 'Juana', '2024-06-20', 5),
(32, 25, 25, 'Braynel', '2024-06-20', 1),
(33, 25, 25, 'Brayne', '2024-06-20', 4),
(34, 31, 31, 'Josefina', '2024-08-01', 3),
(35, 14, 14, 'Maura', '2024-10-10', 3),
(36, 14, 14, 'Maura', '2024-10-10', 3),
(37, 28, 28, 'Helian', '2024-07-10', 16),
(38, 28, 28, 'Helian', '2024-07-10', 16),
(39, 2, 2, 'Helian', '2024-05-20', 3),
(40, 3, 3, 'Josea', '2024-06-02', 1),
(41, 22, 22, 'Miguel', '2024-05-28', 10),
(42, 33, 33, 'Braynel', '2024-08-16', 3),
(43, 38, 38, 'Juan Francisco', '2024-09-26', 9),
(44, 38, 38, 'Juan Francisco', '2024-09-26', 6),
(45, 11, 11, 'Jose Rijo', '2024-09-05', 4),
(46, 23, 23, 'Braynel', '2024-06-05', 2),
(47, 25, 25, 'Braynel', '2024-06-20', 1),
(48, 38, 38, 'Helian', '2024-09-26', 2),
(49, 4, 4, 'Jose', '2024-06-10', 2),
(50, 40, 40, 'Braynel', '2024-10-12', 1),
(51, 16, 16, 'William', '2024-11-05', 3),
(52, 27, 27, 'William', '2024-07-03', 3),
(53, 38, 38, 'Braynel', '2024-09-26', 1),
(54, 35, 35, 'Josea', '2024-09-02', 30),
(55, 28, 28, 'Helian', '2024-07-10', 3),
(56, 28, 28, 'Braynel', '2024-07-10', 3),
(57, 28, 28, 'Braynel', '2024-07-10', 3),
(58, 5, 5, 'Jose', '2024-06-18', 3),
(59, 5, 5, 'Jose', '2024-06-18', 3),
(60, 5, 5, 'Jose', '2024-06-18', 3),
(61, 5, 5, 'Jose', '2024-06-18', 3),
(62, 5, 5, 'Jose', '2024-06-18', 3),
(63, 5, 5, 'Jose', '2024-06-18', 3),
(64, 13, 13, 'Alexis', '2024-09-25', 4),
(65, 19, 19, 'Jose', '2024-10-31', 4),
(66, 10, 10, 'MAURA', '2024-08-20', 4),
(67, 11, 11, 'Jose', '2024-09-05', 4),
(68, 11, 11, 'Braynel', '2024-09-05', 15),
(69, 4, 4, 'Josea', '2024-06-10', 39),
(70, 4, 4, 'bbba', '2024-06-10', 2),
(71, 4, 4, 'bbba', '2024-06-10', 2),
(72, 4, 4, 'bbba', '2024-06-10', 2),
(73, 4, 4, 'bbba', '2024-06-10', 2),
(74, 4, 4, 'bbba', '2024-06-10', 2),
(75, 7, 7, 'Braynel', '2024-07-12', 3),
(76, 7, 7, 'Braynel', '2024-07-12', 3),
(77, 7, 7, 'Braynel', '2024-07-12', 4),
(78, 2, 28, 'Braynel', '2024-07-10', 3),
(79, 2, 28, 'Braynel', '2024-07-10', 3),
(80, 2, 28, 'Braynel', '2024-07-10', 3),
(81, 2, 28, 'Braynel', '2024-07-10', 3),
(82, 2, 28, 'Braynel', '2024-07-10', 3),
(83, 2, 28, 'Braynel', '2024-07-10', 3),
(84, 2, 10, 'Celine', '2024-08-20', 4),
(85, 2, 10, 'Celine', '2024-08-20', 4),
(86, 2, 10, 'Braynel', '2024-08-20', 3),
(87, 2, 10, 'Helian', '2024-08-20', 2),
(88, 2, 33, 'Arianny', '2024-08-16', 6),
(89, 2, 4, 'Jose', '2024-06-10', 5),
(90, 2, 1, 'Braynel', '2024-05-15', 15),
(91, 2, 19, 'Braynel', '2024-10-31', 4),
(92, 2, 7, 'Arianny', '2024-07-12', 90),
(93, 2, 26, 'Braynel', '2024-06-26', 5),
(94, 2, 22, 'Braynel', '2024-05-28', 90),
(95, 2, 22, 'Braynel', '2024-05-28', 90),
(96, 2, 2, 'Braynel', '2024-05-20', 4),
(97, 2, 8, 'Jose', '2024-07-20', 10),
(98, 2, 1, 'Braynel', '2024-05-15', 8),
(99, 2, 2, 'Braynel', '2024-05-20', 8),
(100, 2, 3, 'Braynel', '2024-06-02', 3),
(101, 2, 20, 'Braynel', '2024-12-05', 9),
(102, 2, 20, 'Braynel', '2024-12-05', 9),
(103, 2, 20, 'Braynel', '2024-12-05', 9),
(104, 2, 5, 'Miguel', '2024-06-18', 3),
(105, 2, 7, 'Miguel', '2024-07-12', 3),
(106, 2, 6, 'Miguel', '2024-07-05', 5),
(107, 2, 13, 'Miguel', '2024-09-25', 3),
(108, 2, 20, 'Miguel', '2024-12-05', 3),
(109, 2, 8, 'Miguel', '2024-07-20', 9),
(110, 2, 14, 'Jose', '2024-10-10', 7),
(111, 2, 11, 'Jose', '2024-09-05', 4),
(112, 2, 35, 'Braynel', '2024-09-02', 3),
(113, 2, 35, 'Braynel', '2024-09-02', 3),
(114, 2, 12, 'Braynel', '2024-09-15', 7),
(115, 2, 21, 'Braynel', '2024-05-22', 4),
(116, 2, 54, 'Juana', '2024-08-18', 7),
(117, 2, 5, 'Braynel', '2024-06-18', 8),
(118, 2, 40, 'Juana', '2024-10-12', 1),
(119, 2, 5, 'Braynel', '', 4),
(120, 2, 20, 'Braynel', '', 4),
(121, 2, 48, 'Braynel', '', 4),
(122, 2, 12, 'Braynel', '', 3),
(123, 2, 20, 'Braynel', '', 2),
(124, 2, 20, 'Braynel', '', 2),
(125, 2, 1, 'Braynel', '', 2),
(126, 2, 7, 'Braynel', '', 6),
(127, 2, 6, 'Braynel', '', 3),
(128, 2, 39, 'Braynel', '', 3),
(135, 2, 6, 'Braynel', '', 3),
(136, 2, 21, 'Braynel', '', 3),
(137, 2, 7, 'Helian', '', 2),
(138, 2, 7, 'Helian', '', 7),
(139, 2, 7, 'Braynel', '', 4),
(140, 2, 7, 'Braynel', '', 2),
(141, 2, 7, 'Braynel', '', 2),
(142, 2, 3, 'Braynel', '', 3),
(143, 2, 39, 'Braynel', '', 3),
(144, 2, 1, 'Braynel', '', 4),
(145, 2, 7, 'Braynel', '', 3),
(146, 2, 7, 'Braynel', '', 4),
(147, 2, 7, 'Braynel', '', 2),
(148, 2, 14, 'Braynel', '', 2),
(149, 2, 2, 'Rijo', '', 2),
(150, 2, 7, 'Braynel', '', 4),
(151, 2, 7, 'Braynel', '', 4),
(152, 2, 39, 'Braynel', '', 3),
(153, 2, 4, 'Braynel', '', 2),
(154, 2, 4, 'Braynel', '', 2),
(155, 2, 2, 'Braynel', '', 3),
(156, 2, 3, 'Braynel', '', 2),
(157, 2, 7, 'MAURA', '', 4),
(158, 2, 7, 'MAURA', '', 4),
(159, 2, 4, 'Braynel', '', 3),
(160, 2, 4, 'Helian', '', 3),
(161, 2, 30, 'Braynel', '', 3),
(162, 2, 30, 'Braynel', '', 3),
(163, 2, 39, 'Braynel', '2024-10-04', 3),
(164, 2, 3, 'Braynel', '2024-06-02', 3),
(165, 2, 3, 'Braynel', '2024-06-02', 3),
(166, 2, 20, 'MAURA', '2024-12-05', 3),
(167, 2, 39, 'Braynel', '2024-10-04', 4),
(168, 2, 1, 'Braynel', '2024-05-15', 3),
(169, 2, 11, 'Helian', '2024-09-05', 7),
(170, 2, 11, 'Helian', '2024-09-05', 7),
(171, 2, 47, 'Helian', '2024-07-01', 3),
(172, 2, 47, 'Helian', '2024-07-01', 3),
(173, 2, 47, 'Helian', '2024-07-01', 3),
(174, 2, 27, 'Braynel', '2024-07-03', 2),
(175, 2, 27, 'Braynel', '2024-07-03', 2);

-- --------------------------------------------------------

--
-- Estructura de tabla para la tabla `comments`
--

CREATE TABLE `comments` (
  `id` int(11) NOT NULL,
  `id_user` int(11) NOT NULL,
  `id_event` int(11) NOT NULL,
  `comment_text` varchar(255) NOT NULL,
  `qualification` varchar(255) NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

-- --------------------------------------------------------

--
-- Estructura de tabla para la tabla `events`
--

CREATE TABLE `events` (
  `id` int(11) NOT NULL,
  `name` varchar(255) NOT NULL,
  `description` varchar(255) NOT NULL,
  `event_date` varchar(255) NOT NULL,
  `event_hour` varchar(255) NOT NULL,
  `place` varchar(255) NOT NULL,
  `maxumum_quota` varchar(255) NOT NULL,
  `price` int(255) NOT NULL,
  `reservation_status` varchar(255) NOT NULL,
  `category` varchar(200) NOT NULL,
  `image_url` varchar(200) NOT NULL,
  `notificado` varchar(200) NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

--
-- Volcado de datos para la tabla `events`
--

INSERT INTO `events` (`id`, `name`, `description`, `event_date`, `event_hour`, `place`, `maxumum_quota`, `price`, `reservation_status`, `category`, `image_url`, `notificado`) VALUES
(1, 'Concierto en el parque', 'Disfruta de una tarde llena de música en vivo en el parque central.', '2024-05-09', '18:00', 'Parque Central', '100', 10, 'Disponible', 'Música y Conciertos', 'static/uploads\\concierto_parque.jpg', ''),
(2, 'Taller de cocina italiana', 'Aprende a cocinar auténtica comida italiana con un chef experto.', '2024-05-20', '14:00', 'Escuela de Cocina \"La Cucina\"', '20', 25, 'Disponible', 'Educación y Talleres', 'static/uploads\\taller_cocina_italiana.jpg', ''),
(3, 'Presentación de libros', 'Descubre las últimas novedades literarias y conoce a los autores.', '2024-06-02', '19:00', 'Librería \"El Sabio\"', '50', 90, 'Disponible', 'Arte y Cultura', 'static/uploads\\presentacion_libros.jpg', ''),
(4, 'Yoga en la playa', 'Relájate y recarga energías con una sesión de yoga al amanecer.', '2024-06-10', '06:30', 'Playa \"La Tranquilidad\"', '30', 15, 'Disponible', 'Bienestar y Fitness', 'static/uploads/yoga_playa.jpg', ''),
(5, 'Tour gastronómico por la ciudad', 'Descubre los mejores restaurantes y saborea la cocina local.', '2024-06-18', '19:30', 'Varios restaurantes', '15', 50, 'Disponible', 'Gastronomia', 'static/uploads/tour_gastronomico.jpg', ''),
(6, 'Conferencia sobre tecnología', 'Únete a expertos en tecnología para discutir las últimas tendencias.', '2024-07-05', '10:00', 'Centro de Convenciones', '200', 30, 'Disponible', 'Conferencia', 'static/uploads/conferencia_tecnologia.jpg', ''),
(7, 'Recital de poesía', 'Disfruta de una noche de versos y emociones en vivo.', '2024-07-12', '20:00', 'Café Literario \"El Bohemio\"', '40', 5, 'Disponible', 'Arte y Cultura', 'static/uploads/recital_poesia.jpg', ''),
(8, 'Tour de arte urbano', 'Descubre las obras más impresionantes del arte callejero en la ciudad.', '2024-07-20', '11:00', 'Punto de encuentro: Plaza del Arte', '25', 20, 'Disponible', 'Arte y Cultura', 'static/uploads/tour_arte_urbano.jpg', ''),
(9, 'Clase de fotografía', 'Aprende técnicas profesionales de fotografía con un fotógrafo reconocido.', '2024-08-05', '15:00', 'Estudio de Fotografía \"La Imagen Perfecta\"', '10', 40, 'Disponible', 'Educación y Talleres', 'static/uploads/clase_fotografia.jpg', ''),
(10, 'Festival de cine al aire libre', 'Disfruta de proyecciones de películas bajo las estrellas.', '2024-08-20', '20:30', 'Parque \"Cine bajo las Estrellas\"', '150', 0, 'Disponible', 'Eventos Comunitarios y Festivales', 'static/uploads/festival_cine.jpg', ''),
(11, 'Concierto de rock', 'Disfruta de una noche llena de música rock en vivo.', '2024-09-05', '20:00', 'Teatro Metropolitano', '200', 20, 'Disponible', 'Música y Conciertos', 'static/uploads/concierto_rock.jpg', ''),
(12, 'Exposición de arte contemporáneo', 'Explora las obras más recientes de artistas contemporáneos.', '2024-09-15', '11:00', 'Galería de Arte Moderno', '50', 10, 'Disponible', 'Arte y Cultura', 'static/uploads/exposicion_arte.jpg', ''),
(13, 'Curso de primeros auxilios', 'Aprende técnicas de primeros auxilios y cómo actuar en situaciones de emergencia.', '2024-09-25', '09:30', 'Cruz Roja Local', '30', 15, 'Disponible', 'Educación y Talleres', 'static/uploads/curso_primeros_auxilios.jpg', ''),
(14, 'Feria de alimentos orgánicos', 'Descubre una variedad de productos orgánicos frescos y deliciosos.', '2024-10-10', '12:00', 'Mercado Orgánico', '100', 5, 'Disponible', 'Eventos Comunitarios y Festivales', 'static/uploads/feria_organica.jpg', ''),
(15, 'Conferencia de medio ambiente', 'Participa en discusiones sobre el cuidado del medio ambiente y la sostenibilidad.', '2024-10-20', '18:30', 'Centro Cultural', '80', 1000, 'Disponible', 'Conferencia', 'static/uploads\\conferencia_medio_ambiente.jpg', ''),
(16, 'Festival de música electrónica', 'Sumérgete en la escena de la música electrónica con DJ internacionales.', '2024-11-05', '22:00', 'Club Nocturno \"Electro\"', '150', 30, 'Disponible', 'Música y Conciertos', 'static/uploads/festival_electronica.jpg', ''),
(17, 'Torneo de ajedrez', 'Demuestra tus habilidades en el tablero en nuestro torneo de ajedrez.', '2024-11-15', '14:00', 'Centro Comunitario', '50', 50, 'Disponible', 'Deporte', 'static/uploads\\torneo_ajedrez.jpg', ''),
(18, 'Exhibición de autos clásicos', '', '2024-11-25', '10:00', 'Plaza de la Ciudad', '200', 10, 'Disponible', 'Exhibicion', 'static/uploads\\exhibicion_autos.jpg', ''),
(19, 'Fiesta de Halloween', 'Celebra Halloween con música, disfraces y diversión para toda la familia.', '2024-10-31', '19:00', 'Parque de la Ciudad', '300', 0, 'Disponible', 'Eventos Comunitarios y Festivales', 'static/uploads\\fiesta_halloween.jpg', ''),
(20, 'Maratón benéfico', 'Participa en una carrera de 10 km para apoyar a organizaciones benéficas locales.', '2024-12-05', '08:30', 'Parque Metropolitano', '500', 20, 'Disponible', 'Eventos Comunitarios y Festivales', 'static/uploads\\maraton_benefico.jpg', ''),
(21, 'Concierto de Jazz en el Parque', 'Disfruta de una tarde soleada con música jazz en vivo en el hermoso Parque Central. ¡Relájate y déjate llevar por los ritmos contagiosos!', '2024-05-22', '16:00', 'Parque Central', '200', 15, 'Disponible', 'Música y Conciertos', 'static/uploads/concierto_jazz.jpg', ''),
(22, 'Curso de Fotografía de Naturaleza', 'Aprende a capturar la belleza de la naturaleza en nuestro curso especializado de fotografía. Explora paisajes impresionantes y domina las técnicas profesionales.', '2024-05-28', '10:00', 'Reserva Natural', '15', 50, 'Disponible', 'Educación y Talleres', 'static/uploads/curso_fotografia_naturaleza.jpg', ''),
(23, 'Festival de Arte Urbano', 'Sumérgete en el mundo del arte callejero con nuestro festival anual. Disfruta de grafitis coloridos, instalaciones artísticas y performances en vivo.', '2024-06-05', '12:00', 'Barrio Creativo', '100', 100, 'Disponible', 'Eventos Comunitarios y Festivales', 'static/uploads\\festival_arte_urbano.jpg', ''),
(24, 'Clase de Cocina Tailandesa', 'Descubre los sabores exóticos de Tailandia en nuestra clase de cocina. Aprende a preparar platos tradicionales y sorprende a tus amigos y familiares.', '2024-06-12', '18:30', 'Escuela de Cocina \"Thai Taste\"', '20', 30, 'Disponible', 'Educación y Talleres', 'static/uploads/clase_cocina_tailandesa.jpg', ''),
(25, 'Conferencia de Marketing Digital', 'Explora las últimas tendencias en marketing digital y estrategias efectivas para hacer crecer tu negocio en línea. ¡Aprende de los mejores expertos en el campo!', '2024-06-20', '15:00', 'Centro de Convenciones', '150', 20, 'Disponible', 'Conferencia', 'static/uploads\\conferencia_tecnologia.jpg', ''),
(26, 'Noche de Cine al Aire Libre', 'Disfruta de una noche bajo las estrellas con proyecciones de películas clásicas y contemporáneas en nuestro cine al aire libre. ¡Trae tu manta y palomitas!', '2024-06-26', '20:00', 'Parque de la Luna', '300', 5, 'Disponible', 'Aire Libre', 'static/uploads/noche_cine_aire_libre.jpg', ''),
(27, 'Exposición de Esculturas Modernas', 'Explora el arte tridimensional con nuestra exposición de esculturas modernas. Desde abstractas hasta figurativas, ¡encuentra inspiración en cada obra!', '2024-07-03', '11:00', 'Galería de Arte Contemporáneo', '50', 0, 'Disponible', 'Arte y Cultura', 'static/uploads/exposicion_esculturas.jpg', ''),
(28, 'Taller de Cocina Vegana', 'Descubre deliciosas y saludables recetas veganas en nuestro taller culinario. Aprende a cocinar platos creativos y nutritivos que satisfarán a todos los paladares.', '2024-07-10', '17:30', 'Restaurante Verde', '25', 35, 'Disponible', 'Educación y Talleres', 'static/uploads/taller_cocina_vegana.jpg', ''),
(29, 'Fiesta de la Espuma', 'Diviértete bajo una lluvia de espuma en nuestra fiesta de verano. Baila al ritmo de la música electrónica mientras disfrutas de una experiencia única y refrescante.', '2024-05-08', '19:00', 'Club Ocean', '200', 15, 'Disponible', 'Fiesta', 'static/uploads\\fiesta_espuma.jpg', ''),
(30, 'Concierto de Piano Clásico', 'Embárcate en un viaje musical con los sonidos clásicos del piano. Disfruta de una noche de elegancia y virtuosismo en nuestro concierto especial.', '2024-07-25', '20:30', 'Sala de Conciertos Mozart', '100', 25, 'Disponible', 'Música y Conciertos', 'static/uploads/concierto_piano_clasico.jpg', ''),
(31, 'Festival de Arte Contemporáneo', 'Explora las últimas tendencias en el mundo del arte contemporáneo con nuestra selección de obras innovadoras y provocativas. ¡Una experiencia para los amantes del arte!', '2024-08-01', '12:00', 'Centro Cultural Moderno', '150', 0, 'Disponible', 'Arte y Cultura', 'static/uploads\\festival_arte_contemporaneo.jpg', ''),
(32, 'Conferencia de Innovación Empresarial', 'Descubre las estrategias más innovadoras para impulsar tu negocio en nuestra conferencia especializada. Aprende de líderes empresariales visionarios y expande tus horizontes.', '2024-08-08', '14:00', 'Centro de Convenciones Empresariales', '80', 10, 'Disponible', 'Conferencia', 'static/uploads/conferencia_innovacion_empresarial.jpg', ''),
(33, 'Noche de Flamenco', 'Déjate seducir por el arte y la pasión del flamenco en una noche inolvidable llena de baile, música y emoción. ¡Vive la cultura española en su máxima expresión!', '2024-08-16', '21:00', 'Tablao Flamenco \"La Gitana\"', '50', 20, 'Disponible', 'Danza', 'static/uploads/noche_flamenco.jpg', ''),
(34, 'Taller de Escritura Creativa', 'Despierta tu creatividad y libera tu imaginación en nuestro taller de escritura creativa. Explora diferentes géneros y técnicas literarias en un ambiente inspirador.', '2024-08-24', '18:00', 'Café Literario \"La Pluma\"', '30', 15, 'Disponible', 'Educación y Talleres', 'static/uploads/taller_escritura_creativa.jpg', ''),
(35, 'Exhibición de Arte Indígena', 'Descubre la riqueza cultural de las comunidades indígenas a través de nuestra exhibición de arte tradicional. Admira piezas únicas y aprende sobre su significado cultural.', '2024-09-02', '10:00', 'Museo de Arte Indígena', '100', 0, 'Disponible', 'Arte y Cultura', 'static/uploads/exhibicion_arte_indigena.jpg', ''),
(36, 'Concierto de Música Clásica', 'Disfruta de una velada sofisticada con los sonidos refinados de la música clásica. Déjate llevar por la belleza y la emoción de las obras maestras de los grandes compositores.', '2024-09-10', '19:30', 'Teatro de la Ópera', '150', 30, 'Disponible', 'Música y Conciertos', 'static/uploads/concierto_musica_clasica.jpg', ''),
(37, 'Feria del Libro Antiguo', 'Explora una colección única de libros antiguos y raros en nuestra feria anual. Encuentra tesoros literarios y sumérgete en la historia a través de sus páginas.', '2024-09-18', '11:00', 'Plaza de las Antigüedades', '50', 0, 'Disponible', 'Eventos Comunitarios y Festivales', 'static/uploads/feria_libro_antiguo.jpg', ''),
(38, 'Taller de Cocina Fusión', 'Experimenta con sabores del mundo en nuestro taller de cocina fusión. Aprende a combinar ingredientes de diferentes culturas y crea platos innovadores y deliciosos.', '2024-09-26', '16:30', 'Escuela de Gastronomía Internacional', '20', 40, 'Disponible', 'Educación y Talleres', 'static/uploads/taller_cocina_fusion.jpg', ''),
(39, 'Festival de Danzas del Mundo', 'Embárcate en un viaje cultural a través de la danza en nuestro festival de danzas del mundo. Disfruta de actuaciones vibrantes y coloridas que celebran la diversidad cultural.', '2024-10-04', '20:00', 'Teatro Cultural', '200', 10, 'Disponible', 'Eventos Comunitarios y Festivales', 'static/uploads/festival_danzas_mundo.jpg', ''),
(40, 'Curso de Arte en Acuarela', 'Descubre el arte de la acuarela en nuestro curso especializado. Aprende técnicas de pintura y crea obras impresionantes bajo la guía de nuestros expertos artistas.', '2024-10-12', '14:00', 'Academia de Arte \"Aqua\"', '15', 25, 'Disponible', 'Educación y Talleres', 'static/uploads/curso_arte_acuarela.jpg', ''),
(41, 'Concierto Juan Luis Guerra', 'Concierto de Juan Luis Guerra presentando sus mayores éxitos.', '2024-06-15', '20:00', 'Estadio Nacional', '10000', 60, 'Disponible', 'Música y Conciertos', 'static/uploads\\juan-luis-guerra.jpg', ''),
(42, 'Concierto de Karol G', 'Show en vivo de Karol G, disfruta de sus nuevos éxitos y clásicos.', '2024-08-20', '21:00', 'Arena Ciudad de México', '15000', 75, 'Disponible', 'Música y Conciertos', 'static/uploads\\concierto_karolg.jpg', ''),
(43, 'Concierto Sinfónico de Verano', 'Disfruta las mejores obras sinfónicas en un ambiente al aire libre.', '2024-05-30', '19:00', 'Anfiteatro Ciudad', '500', 50, 'Disponible', 'Música y Conciertos', 'static/uploads/concierto_sinfonico.jpg', ''),
(44, 'Festival de Reggae', 'Vibra con los ritmos relajantes del reggae bajo las estrellas.', '2024-06-15', '18:00', 'Playa Costa Azul', '300', 45, 'Disponible', 'Música y Conciertos', 'static/uploads/festival_reggae.jpg', ''),
(45, 'Noche de Ópera al Aire Libre', 'Experimenta las emocionantes arias de famosas óperas en vivo.', '2024-06-20', '20:00', 'Parque Central', '400', 60, 'Disponible', 'Música y Conciertos', 'static/uploads/noche_opera.jpg', ''),
(46, 'Tributo a Queen', 'Revive los éxitos de Queen con una banda tributo espectacular.', '2024-06-25', '21:00', 'Estadio Rock City', '10000', 75, 'Disponible', 'Música y Conciertos', 'static/uploads/tributo_queen.jpg', ''),
(47, 'Jazz en la Terraza', 'Noche de jazz suave con vistas a la ciudad.', '2024-07-01', '20:00', 'Terraza Panorama', '200', 30, 'Disponible', 'Música y Conciertos', 'static/uploads/jazz_terraza.jpg', ''),
(48, 'Festival Electrónico de Verano', 'Baila toda la noche con los top DJs del mundo.', '2024-07-10', '22:00', 'Arena Electrónica', '15000', 90, 'Disponible', 'Música y Conciertos', 'static/uploads/festival_electronico.jpg', ''),
(49, 'Noche de Salsa', 'Calienta la pista con los mejores sonidos de salsa.', '2024-07-18', '19:00', 'Salón Latino', '250', 25, 'Disponible', 'Música y Conciertos', 'static/uploads/noche_salsa.jpg', ''),
(50, 'Concierto de Piano', 'Recital de piano clásico por un renombrado pianista.', '2024-07-24', '19:30', 'Auditorio Clásico', '300', 50, 'Disponible', 'Música y Conciertos', 'static/uploads/concierto_piano.jpg', ''),
(51, 'Festival de Folk Americano', 'Disfruta de la música folk americana en un entorno campestre.', '2024-07-30', '16:00', 'Campo Verde', '2000', 40, 'Disponible', 'Música y Conciertos', 'static/uploads/festival_folk.jpg', ''),
(52, 'Noche de Rock Alternativo', 'Concierto de bandas de rock alternativo emergentes.', '2024-08-05', '21:00', 'Club Rebel', '300', 35, 'Disponible', 'Música y Conciertos', 'static/uploads/noche_rock_alt.jpg', ''),
(53, 'Maratón de Conciertos Pop', 'Disfruta de un día completo de música pop con artistas populares.', '2024-08-12', '12:00', 'Parque Musical', '5000', 80, 'Disponible', 'Música y Conciertos', 'static/uploads/maraton_pop.jpg', ''),
(54, 'Concierto Acústico', 'Intimidad y melodía en una noche acústica especial.', '2024-08-18', '19:00', 'Café Intimo', '100', 20, 'Disponible', 'Música y Conciertos', 'static/uploads/concierto_acustico.jpg', ''),
(55, 'Tributo a The Beatles', 'Noche de nostalgia con los grandes éxitos de The Beatles.', '2024-08-23', '20:00', 'Teatro Vintage', '800', 50, 'Disponible', 'Música y Conciertos', 'static/uploads/tributo_beatles.jpg', ''),
(56, 'Festival de Música Latina', 'Festival celebrando lo mejor de la música latina.', '2024-08-31', '15:00', 'Plaza Fiesta', '1000', 55, 'Disponible', 'Música y Conciertos', 'static/uploads/festival_latina.jpg', ''),
(57, 'Noche de Blues', 'Sumérgete en las profundidades del blues con artistas de renombre.', '2024-09-05', '20:00', 'Casa del Blues', '150', 40, 'Disponible', 'Música y Conciertos', 'static/uploads/noche_blues.jpg', ''),
(58, 'Concierto de Música Clásica', 'Una noche con lo mejor de la música clásica.', '2024-09-11', '19:30', 'Gran Teatro', '700', 70, 'Disponible', 'Música y Conciertos', 'static/uploads/concierto_clasica.jpg', ''),
(59, 'Festival de Rock Pesado', 'El más grande festival de rock pesado del año.', '2024-09-17', '18:00', 'Estadio de Rock', '20000', 100, 'Disponible', 'Música y Conciertos', 'static/uploads/festival_rock_pesado.jpg', ''),
(60, 'Gala de Ópera', 'Una exclusiva noche de gala con las mejores obras de ópera.', '2024-09-23', '18:30', 'Opera Nacional', '500', 120, 'Disponible', 'Música y Conciertos', 'static/uploads/gala_opera.jpg', ''),
(61, 'Concierto de Música Electrónica', 'Vive una experiencia electrónica inolvidable.', '2024-09-29', '23:00', 'Dome Electronic', '3000', 65, 'Disponible', 'Música y Conciertos', 'static/uploads/concierto_electronica.jpg', ''),
(62, 'Noche de Tango', 'Disfruta de una noche apasionada con los mejores del tango.', '2024-10-03', '20:00', 'Salón Tango', '200', 50, 'Disponible', 'Música y Conciertos', 'static/uploads/noche_tango.jpg', '');

-- --------------------------------------------------------

--
-- Estructura de tabla para la tabla `event_categories`
--

CREATE TABLE `event_categories` (
  `category_id` int(11) NOT NULL,
  `category_name` varchar(255) NOT NULL,
  `category_description` varchar(255) NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

-- --------------------------------------------------------

--
-- Estructura de tabla para la tabla `payment`
--

CREATE TABLE `payment` (
  `id` int(11) NOT NULL,
  `evento_id` int(11) NOT NULL,
  `amount_paid` decimal(10,2) NOT NULL,
  `payment_date` date NOT NULL,
  `card_number` varchar(19) NOT NULL,
  `card_holder` varchar(255) NOT NULL,
  `card_expiry_date` date NOT NULL,
  `card_cvv` varchar(4) NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

-- --------------------------------------------------------

--
-- Estructura de tabla para la tabla `roles`
--

CREATE TABLE `roles` (
  `id_rol` int(11) NOT NULL,
  `description` varchar(255) NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

--
-- Volcado de datos para la tabla `roles`
--

INSERT INTO `roles` (`id_rol`, `description`) VALUES
(1, 'admin'),
(2, 'user');

-- --------------------------------------------------------

--
-- Estructura de tabla para la tabla `user`
--

CREATE TABLE `user` (
  `id` int(11) NOT NULL,
  `username` varchar(255) NOT NULL,
  `email` varchar(255) NOT NULL,
  `password` varchar(255) NOT NULL,
  `event_safe` varchar(200) NOT NULL,
  `id_role` int(11) NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

--
-- Volcado de datos para la tabla `user`
--

INSERT INTO `user` (`id`, `username`, `email`, `password`, `event_safe`, `id_role`) VALUES
(1, 'brainel', 'brainelrodriguez005@gmail.com', '123', '', 1),
(2, 'brainel12', 'rodriguezbrainel84@gmail.com', 'brainel01', '', 2),
(4, 'Juan', 'bary@gmail.com', 'cabrera01', '', 2),
(5, 'CARLOS', 'carlos@gmail.com', '123', '', 2),
(6, 'juan pablo', 'cabrera@gmail.com', 'jun0900', '', 2),
(7, 'Daurys', 'dauris@gmail.com', 'hola123456', '', 2),
(8, 'Celine Santos', 'barycabrea@gmail.com', 'celine01', '', 2);

--
-- Índices para tablas volcadas
--

--
-- Indices de la tabla `bookings`
--
ALTER TABLE `bookings`
  ADD PRIMARY KEY (`id`),
  ADD KEY `id_user` (`id_user`,`id_event`);

--
-- Indices de la tabla `comments`
--
ALTER TABLE `comments`
  ADD PRIMARY KEY (`id`),
  ADD KEY `id_user` (`id_user`,`id_event`),
  ADD KEY `id_event` (`id_event`);

--
-- Indices de la tabla `events`
--
ALTER TABLE `events`
  ADD PRIMARY KEY (`id`);

--
-- Indices de la tabla `event_categories`
--
ALTER TABLE `event_categories`
  ADD PRIMARY KEY (`category_id`);

--
-- Indices de la tabla `payment`
--
ALTER TABLE `payment`
  ADD PRIMARY KEY (`id`),
  ADD KEY `evento_id` (`evento_id`);

--
-- Indices de la tabla `roles`
--
ALTER TABLE `roles`
  ADD PRIMARY KEY (`id_rol`);

--
-- Indices de la tabla `user`
--
ALTER TABLE `user`
  ADD PRIMARY KEY (`id`),
  ADD KEY `id_role` (`id_role`);

--
-- AUTO_INCREMENT de las tablas volcadas
--

--
-- AUTO_INCREMENT de la tabla `bookings`
--
ALTER TABLE `bookings`
  MODIFY `id` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=176;

--
-- AUTO_INCREMENT de la tabla `comments`
--
ALTER TABLE `comments`
  MODIFY `id` int(11) NOT NULL AUTO_INCREMENT;

--
-- AUTO_INCREMENT de la tabla `events`
--
ALTER TABLE `events`
  MODIFY `id` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=63;

--
-- AUTO_INCREMENT de la tabla `event_categories`
--
ALTER TABLE `event_categories`
  MODIFY `category_id` int(11) NOT NULL AUTO_INCREMENT;

--
-- AUTO_INCREMENT de la tabla `payment`
--
ALTER TABLE `payment`
  MODIFY `id` int(11) NOT NULL AUTO_INCREMENT;

--
-- AUTO_INCREMENT de la tabla `roles`
--
ALTER TABLE `roles`
  MODIFY `id_rol` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=3;

--
-- AUTO_INCREMENT de la tabla `user`
--
ALTER TABLE `user`
  MODIFY `id` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=9;

--
-- Restricciones para tablas volcadas
--

--
-- Filtros para la tabla `payment`
--
ALTER TABLE `payment`
  ADD CONSTRAINT `payment_ibfk_1` FOREIGN KEY (`evento_id`) REFERENCES `events` (`id`);

--
-- Filtros para la tabla `user`
--
ALTER TABLE `user`
  ADD CONSTRAINT `user_ibfk_1` FOREIGN KEY (`id_role`) REFERENCES `roles` (`id_rol`);
COMMIT;

/*!40101 SET CHARACTER_SET_CLIENT=@OLD_CHARACTER_SET_CLIENT */;
/*!40101 SET CHARACTER_SET_RESULTS=@OLD_CHARACTER_SET_RESULTS */;
/*!40101 SET COLLATION_CONNECTION=@OLD_COLLATION_CONNECTION */;

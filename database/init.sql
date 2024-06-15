CREATE DATABASE IF NOT EXISTS `remote_desktop_app` DEFAULT CHARACTER SET utf8 COLLATE utf8_general_ci;

USE `remote_desktop_app`;

CREATE TABLE IF NOT EXISTS `clients` (
    `id` int NOT NULL AUTO_INCREMENT,
    `username` varchar(255) NOT NULL,
    `password` varchar(255) NOT NULL,
    PRIMARY KEY (`id`)
) ENGINE = InnoDB DEFAULT CHARSET = utf8;

CREATE TABLE IF NOT EXISTS `servers` (
    `mac_address` varchar(255) NOT NULL,
    `id` varchar(10) NOT NULL,
    `password` varchar(9) NOT NULL,
    `port` int NOT NULL,
    `remote_address` varchar(255) DEFAULT NULL,
    PRIMARY KEY (`mac_address`)
) ENGINE = InnoDB DEFAULT CHARSET = utf8;

CREATE TABLE IF NOT EXISTS `vps` (
    `id` int NOT NULL AUTO_INCREMENT,
    `ip_address` varchar(255) NOT NULL,
    `connections` int NOT NULL,
    PRIMARY KEY (`id`)
) ENGINE = InnoDB DEFAULT CHARSET = utf8;

CREATE TABLE IF NOT EXISTS `logs` (
    `id` int NOT NULL AUTO_INCREMENT,
    `client_id` int NOT NULL,
    `server_id` varchar(255) NOT NULL,
    `date` datetime NOT NULL,
    PRIMARY KEY (`id`),
    FOREIGN KEY (`client_id`) REFERENCES `clients` (`id`),
    FOREIGN KEY (`server_id`) REFERENCES `servers` (`mac_address`)
) ENGINE = InnoDB DEFAULT CHARSET = utf8;

INSERT INTO
    `servers` (
        `mac_address`,
        `id`,
        `password`,
        `port`
    )
VALUES
    (
        '00:00:00:00:00:00',
        '1234567890',
        '123456789',
        4444
    );

INSERT INTO
    `servers` (`mac_address`, `id`, `password`, `port`)
VALUES
    (
        'E0-0A-F6-96-8D-C5',
        '1234567891',
        '123456789',
        4444
    );

INSERT INTO
    `vps` (`ip_address`, `connections`)
VALUES
    ('172.207.92.76', 0);

INSERT INTO
    `vps` (`ip_address`, `connections`)
VALUES
    ('172.207.92.77', 0);

INSERT INTO
    `vps` (`ip_address`, `connections`)
VALUES
    ('172.207.92.78', 1);

INSERT INTO
    `clients` (`username`, `password`)
VALUES
    ('admin', 'admin');

INSERT INTO
    `logs` (`client_id`, `server_id`, `date`)
VALUES
    (1, '00:00:00:00:00:00', '2021-01-01 00:00:00');

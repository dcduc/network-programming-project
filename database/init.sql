CREATE DATABASE IF NOT EXISTS `remote_desktop_app` DEFAULT CHARACTER SET utf8 COLLATE utf8_general_ci;

CREATE TABLE IF NOT EXISTS `clients` (
    `id` int NOT NULL AUTO_INCREMENT,
    `name` varchar(255) NOT NULL,
    PRIMARY KEY (`id`)
) ENGINE = InnoDB DEFAULT CHARSET = utf8;

CREATE TABLE IF NOT EXISTS `servers` (
    `mac_address` varchar(255) NOT NULL,
    `remote_address` varchar(255) DEFAULT NULL,
    `id` varchar(255) NOT NULL,
    `password` varchar(255) NOT NULL,
    `port` int NOT NULL,
) ENGINE = InnoDB DEFAULT CHARSET = utf8;

CREATE TABLE IF NOT EXISTS `vps` (
    `id` int NOT NULL AUTO_INCREMENT,
    `ip_address` varchar(255) NOT NULL,
    `connections` int NOT NULL,
)
INSERT INTO
    `vps` (`ip_address`, `connections`)
VALUES
    ('172.207.92.76', 0);

INSERT INTO
    `servers` (
        `mac_address`,
        `id`,
        `password`,
        `port`
    )
VALUES
    ('E0-0A-F6-96-8D-C5', '')

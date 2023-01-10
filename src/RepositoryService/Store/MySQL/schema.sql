CREATE TABLE IF NOT EXISTS `repositories` (
    `id` INT(11) NOT NULL AUTO_INCREMENT,
    `name` VARCHAR(255) NOT NULL UNIQUE,
    `description` MEDIUMTEXT NULL,
    `license` VARCHAR(255) NULL,
    `source_url` VARCHAR(255) NOT NULL,
    `status` INT(1) NOT NULL,
    `last_sync` INT(11) NULL,
    `github_id` INT(11) NULL,
    PRIMARY KEY(`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8;

CREATE TABLE IF NOT EXISTS `topics` (
    `id` INT(11) NOT NULL AUTO_INCREMENT,
    `topic` VARCHAR(255) NOT NULL,
    PRIMARY KEY(`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8;

CREATE TABLE IF NOT EXISTS `languages` (
    `id` INT(11) NOT NULL AUTO_INCREMENT,
    `language` VARCHAR(255) NOT NULL,
    PRIMARY KEY(`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8;

CREATE TABLE IF NOT EXISTS `repositories_topics` (
    `id` INT(11) NOT NULL AUTO_INCREMENT,
    `topic_id` INT(11) NOT NULL,
    `repository_id` INT(11) NOT NULL,
    PRIMARY KEY(`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8;

CREATE TABLE IF NOT EXISTS `repositories_languages` (
    `id` INT(11) NOT NULL AUTO_INCREMENT,
    `language_id` INT(11) NOT NULL,
    `repository_id` INT(11) NOT NULL,
    PRIMARY KEY(`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8;

CREATE TABLE IF NOT EXISTS `authors` (
    `id` INT(11) NOT NULL AUTO_INCREMENT,
    `author` VARCHAR(255) NOT NULL,
    `email` VARCHAR(255) NOT NULL,
    `original_author` VARCHAR(255) NOT NULL,
    `original_email` VARCHAR(255) NOT NULL,
    `subject` VARCHAR(64) NULL,
    PRIMARY KEY(`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8;

CREATE TABLE IF NOT EXISTS `authors_keys` (
    `id` INT(11) NOT NULL AUTO_INCREMENT,
    `author_id` INT(11) NOT NULL,
    `public_key` TEXT NOT NULL,
    PRIMARY KEY(`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8;

CREATE TABLE IF NOT EXISTS `repositories_authors` (
    `id` INT(11) NOT NULL AUTO_INCREMENT,
    `repository_id` INT(11) NOT NULL,
    `author_id` INT(11) NOT NULL,
    `write_access` INT(1) NOT NULL,
    PRIMARY KEY(`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8;


CREATE TABLE IF NOT EXISTS `authors_migration` (
    `id` INT(11) NOT NULL AUTO_INCREMENT,
    `old_email` VARCHAR(255) NOT NULL UNIQUE,
    `old_author` VARCHAR(255) NOT NULL,
    `new_author` VARCHAR(255) NOT NULL UNIQUE,
    `new_email` VARCHAR(255) NOT NULL UNIQUE,
    PRIMARY KEY(`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8;

CREATE TABLE IF NOT EXISTS `repositories` (
    `id` INT(11) NOT NULL AUTO_INCREMENT,
    `repository_url` VARCHAR(255) NOT NULL UNIQUE,
    `status` VARCHAR(32) NOT NULL,
    PRIMARY KEY(`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8;

CREATE TABLE IF NOT EXISTS `authors_to_repositories` (
    `id` INT(11) NOT NULL AUTO_INCREMENT,
    `repository_id` INT(11) NOT NULL,
    `author_id` INT(11) NOT NULL,
    PRIMARY KEY(`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8;

INSERT INTO `repositories`
(name, source_url, status)
VALUES
('docker-ce', 'https://github.com/docker/docker-ce.git', 1),
('compose', 'https://github.com/docker/compose.git', 1),
('flask', 'https://github.com/pallets/flask.git', 1),
('vim', 'https://github.com/vim/vim.git', 1),
('emacs', 'https://github.com/emacs-mirror/emacs.git', 1),
('gunicorn', 'https://github.com/benoitc/gunicorn.git', 1),
('youtube-dl', 'https://github.com/ytdl-org/youtube-dl.git', 1),
('jquery', 'https://github.com/jquery/jquery.git', 1),
('django', 'https://github.com/django/django.git', 1);

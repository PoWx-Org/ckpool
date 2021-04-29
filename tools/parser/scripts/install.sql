CREATE DATABASE IF NOT EXISTS pool_base;
USE pool_base;

CREATE TABLE IF NOT EXISTS `mined_blocks` (
  `id_block` int unsigned NOT NULL AUTO_INCREMENT,
  `hash` varchar(256) NOT NULL,
  `date_mined` datetime NOT NULL,
  `height` int unsigned NOT NULL,
  `reward` decimal(14,9) unsigned NOT NULL,
  PRIMARY KEY (`id_block`),
  UNIQUE KEY `hash_UNIQUE` (`hash`),
  UNIQUE KEY `date_mined_UNIQUE` (`date_mined`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

CREATE TABLE IF NOT EXISTS `miners` (
  `id_miner` int unsigned NOT NULL AUTO_INCREMENT,
  `name` varchar(45) DEFAULT NULL,
  PRIMARY KEY (`id_miner`),
  UNIQUE KEY `id_miner_UNIQUE` (`id_miner`),
  UNIQUE KEY `name_UNIQUE` (`name`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

CREATE TABLE IF NOT EXISTS `blocks_stats` (
  `id_stat` int unsigned NOT NULL AUTO_INCREMENT,
  `id_block` int unsigned NOT NULL,
  `id_miner` int unsigned NOT NULL,
  `shares` int DEFAULT NULL,
  PRIMARY KEY (`id_stat`),
  KEY `id_miner_foreign_idx` (`id_miner`),
  KEY `id_block_foreign_idx` (`id_block`),
  CONSTRAINT `id_block_foreign` FOREIGN KEY (`id_block`) REFERENCES `mined_blocks` (`id_block`) ON DELETE CASCADE ON UPDATE CASCADE,
  CONSTRAINT `id_miner_foreign` FOREIGN KEY (`id_miner`) REFERENCES `miners` (`id_miner`) ON DELETE CASCADE ON UPDATE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

CREATE TABLE IF NOT EXISTS `pool_base`.`transactions` (
  `id_payment` INT UNSIGNED NOT NULL AUTO_INCREMENT,
  `id_block` INT UNSIGNED NOT NULL,
  `hash_txn` VARCHAR(45) NULL,
  `status` VARCHAR(45) NOT NULL,
  PRIMARY KEY (`id_payment`),
  UNIQUE INDEX `id_payment_UNIQUE` (`id_payment` ASC),
  UNIQUE INDEX `id_block_UNIQUE` (`id_block` ASC),
  CONSTRAINT `id_block_foreign_txn`
    FOREIGN KEY (`id_block`)
    REFERENCES `pool_base`.`mined_blocks` (`id_block`)
    ON DELETE CASCADE
    ON UPDATE CASCADE) ENGINE=InnoDB;

CREATE TABLE  IF NOT EXISTS `transactions` (
  `id_payment` int(10) unsigned NOT NULL AUTO_INCREMENT,
  `id_block` int(10) unsigned NOT NULL,
  `hash_txn` varchar(128) DEFAULT NULL,
  `status` varchar(45) NOT NULL,
  `amount` decimal(16,8) unsigned zerofill DEFAULT NULL,
  PRIMARY KEY (`id_payment`),
  UNIQUE KEY `id_payment_UNIQUE` (`id_payment`),
  UNIQUE KEY `id_block_UNIQUE` (`id_block`),
  CONSTRAINT `id_block_foreign_txn` FOREIGN KEY (`id_block`) REFERENCES `mined_blocks` (`id_block`) ON DELETE CASCADE ON UPDATE CASCADE
) ENGINE=InnoDB;

CREATE OR REPLACE VIEW  `pool_base`.`stats_blocks_view` AS
    SELECT 
        `mb`.`id_block` AS `id_block`,
        `mb`.`hash` AS `hash`,
        `mb`.`height` AS `height`,
        `u`.`name` AS `user`,
        `bs`.`shares` AS `shares`,
        `mb`.`date_mined` AS `date_mined`
    FROM
        ((`pool_base`.`blocks_stats` `bs`
        LEFT JOIN `pool_base`.`miners` `u` ON ((`bs`.`id_miner` = `u`.`id_miner`)))
        LEFT JOIN `pool_base`.`mined_blocks` `mb` ON ((`bs`.`id_block` = `mb`.`id_block`)));

DROP procedure IF EXISTS `get_mature_blocks`;
CREATE DATABASE IF NOT EXISTS pool_base;
USE pool_base;

CREATE TABLE IF NOT EXISTS `mined_blocks` (
  `id_block` int unsigned NOT NULL AUTO_INCREMENT,
  `hash` varchar(256) NOT NULL,
  `date_mined` datetime NOT NULL,
  `height` int unsigned NOT NULL,
  `reward` decimal(14,9) unsigned NOT NULL,
  PRIMARY KEY (`id_block`),
  UNIQUE KEY `block_id_UNIQUE` (`id_block`),
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
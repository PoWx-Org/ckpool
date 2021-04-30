/*!40101 SET @OLD_CHARACTER_SET_CLIENT=@@CHARACTER_SET_CLIENT */;
/*!40101 SET @OLD_CHARACTER_SET_RESULTS=@@CHARACTER_SET_RESULTS */;
/*!40101 SET @OLD_COLLATION_CONNECTION=@@COLLATION_CONNECTION */;
/*!40101 SET NAMES utf8 */;
/*!40014 SET @OLD_FOREIGN_KEY_CHECKS=@@FOREIGN_KEY_CHECKS, FOREIGN_KEY_CHECKS=0 */;
/*!40101 SET @OLD_SQL_MODE=@@SQL_MODE, SQL_MODE='NO_AUTO_VALUE_ON_ZERO' */;
/*!40111 SET @OLD_SQL_NOTES=@@SQL_NOTES, SQL_NOTES=0 */;

CREATE DATABASE /*!32312 IF NOT EXISTS*/ pool_base /*!40100 DEFAULT CHARACTER SET utf8mb4 */;
USE pool_base;

DROP TABLE IF EXISTS blocks_stats;
CREATE TABLE `blocks_stats` (
  `id_stat` int(10) unsigned NOT NULL AUTO_INCREMENT,
  `id_block` int(10) unsigned NOT NULL,
  `id_miner` int(10) unsigned NOT NULL,
  `shares` int(11) DEFAULT NULL,
  PRIMARY KEY (`id_stat`),
  KEY `id_miner_foreign_idx` (`id_miner`),
  KEY `id_block_foreign_idx` (`id_block`),
  CONSTRAINT `id_block_foreign` FOREIGN KEY (`id_block`) REFERENCES `mined_blocks` (`id_block`) ON DELETE CASCADE ON UPDATE CASCADE,
  CONSTRAINT `id_miner_foreign` FOREIGN KEY (`id_miner`) REFERENCES `miners` (`id_miner`) ON DELETE CASCADE ON UPDATE CASCADE
) ENGINE=InnoDB AUTO_INCREMENT=71 DEFAULT CHARSET=utf8mb4;

DROP TABLE IF EXISTS mined_blocks;
CREATE TABLE `mined_blocks` (
  `id_block` int(10) unsigned NOT NULL AUTO_INCREMENT,
  `hash` varchar(256) NOT NULL,
  `date_mined` datetime NOT NULL,
  `height` int(10) unsigned NOT NULL,
  `reward` decimal(14,9) unsigned NOT NULL,
  PRIMARY KEY (`id_block`),
  UNIQUE KEY `hash_UNIQUE` (`hash`),
  UNIQUE KEY `date_mined_UNIQUE` (`date_mined`)
) ENGINE=InnoDB AUTO_INCREMENT=11 DEFAULT CHARSET=utf8mb4;

DROP TABLE IF EXISTS miners;
CREATE TABLE `miners` (
  `id_miner` int(10) unsigned NOT NULL AUTO_INCREMENT,
  `name` varchar(45) DEFAULT NULL,
  PRIMARY KEY (`id_miner`),
  UNIQUE KEY `id_miner_UNIQUE` (`id_miner`),
  UNIQUE KEY `name_UNIQUE` (`name`)
) ENGINE=InnoDB AUTO_INCREMENT=8 DEFAULT CHARSET=utf8mb4;

DROP TABLE IF EXISTS transactions;
CREATE TABLE `transactions` (
  `id_payment` int(10) unsigned NOT NULL AUTO_INCREMENT,
  `id_block` int(10) unsigned NOT NULL,
  `hash_txn` varchar(128) DEFAULT NULL,
  `status` varchar(45) NOT NULL,
  `amount` decimal(16,8) unsigned zerofill DEFAULT NULL,
  PRIMARY KEY (`id_payment`),
  UNIQUE KEY `id_payment_UNIQUE` (`id_payment`),
  UNIQUE KEY `id_block_UNIQUE` (`id_block`),
  CONSTRAINT `id_block_foreign_txn` FOREIGN KEY (`id_block`) REFERENCES `mined_blocks` (`id_block`) ON DELETE CASCADE ON UPDATE CASCADE
) ENGINE=InnoDB AUTO_INCREMENT=8 DEFAULT CHARSET=latin1;

CREATE OR REPLACE VIEW `stats_blocks_view` AS select `mb`.`id_block` AS `id_block`,`mb`.`hash` AS `hash`,`mb`.`height` AS `height`,`u`.`name` AS `user`,`bs`.`shares` AS `shares`,`mb`.`date_mined` AS `date_mined` from ((`blocks_stats` `bs` left join `miners` `u` on((`bs`.`id_miner` = `u`.`id_miner`))) left join `mined_blocks` `mb` on((`bs`.`id_block` = `mb`.`id_block`)));

DROP PROCEDURE IF EXISTS get_mature_blocks;
CREATE PROCEDURE `get_mature_blocks`( IN cur_height INT UNSIGNED, IN maturity  INT UNSIGNED)
BEGIN
	SELECT mb.id_block, mb.hash, mb.date_mined, mb.height, mb.reward 
        FROM pool_base.mined_blocks mb 
            LEFT JOIN pool_base.transactions tx 
	            ON mb.id_block = tx.id_block 
	        WHERE tx.status is null
                AND height < (cur_height -  maturity);
END;





/*!40111 SET SQL_NOTES=@OLD_SQL_NOTES */;
/*!40101 SET SQL_MODE=@OLD_SQL_MODE */;
/*!40014 SET FOREIGN_KEY_CHECKS=@OLD_FOREIGN_KEY_CHECKS */;
/*!40101 SET CHARACTER_SET_CLIENT=@OLD_CHARACTER_SET_CLIENT */;
/*!40101 SET CHARACTER_SET_RESULTS=@OLD_CHARACTER_SET_RESULTS */;
/*!40101 SET COLLATION_CONNECTION=@OLD_COLLATION_CONNECTION */;

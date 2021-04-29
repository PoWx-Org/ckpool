CREATE PROCEDURE `get_mature_blocks`( IN cur_height INT UNSIGNED, IN maturity  INT UNSIGNED)
BEGIN
	SELECT mb.id_block, mb.hash, mb.date_mined, mb.height, mb.reward 
        FROM pool_base.mined_blocks mb 
            LEFT JOIN pool_base.transactions tx 
	            ON mb.id_block = tx.id_block 
	        WHERE tx.status is null
                AND height < (cur_height -  maturity);
END
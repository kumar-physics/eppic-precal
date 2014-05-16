#!/bin/bash

if [ -z "$1" ]
then
	echo "Usage: $0 <db_name>"
	exit 1
fi

db=$1


mysql $db << EOF

DROP FUNCTION IF EXISTS get_homologs;
DELIMITER $$
CREATE FUNCTION get_homologs(pdbuid INT,chain VARCHAR(255)) RETURNS INT(12)
BEGIN
DECLARE x INT(12);
SET x=(SELECT numHomologs 
FROM ChainCluster 
WHERE pdbInfo_uid=pdbuid 
AND (repChain=chain OR memberChains LIKE BINARY CONCAT("%",chain,"%")));
RETURN x;
END$$
DELIMITER ;

DROP FUNCTION IF EXISTS get_idcutoff;
DELIMITER $$
CREATE FUNCTION get_idcutoff(pdbuid INT,chain VARCHAR(255)) 
RETURNS DOUBLE
BEGIN
DECLARE x DOUBLE;
SET x=(SELECT seqIdCutOff 
FROM ChainCluster 
WHERE pdbInfo_uid=pdbuid 
AND (repChain=chain OR memberChains LIKE BINARY CONCAT("%",chain,"%")));
RETURN x;
END$$
DELIMITER ;

DROP FUNCTION IF EXISTS pred;
DELIMITER $$
CREATE FUNCTION pred(i_uid int(11),m VARCHAR(15)) RETURNS varchar(6)
BEGIN
DECLARE res VARCHAR(6);
SET res=(SELECT callName 
FROM InterfaceScore
WHERE interfaceItem_uid=i_uid
AND method=m);
RETURN res;
END$$
DELIMITER ;

DROP FUNCTION IF EXISTS score;
DELIMITER $$
CREATE FUNCTION score(i_uid int(11),m VARCHAR(15),s varchar(255)) RETURNS DOUBLE
BEGIN
DECLARE res DOUBLE;
IF s = "1" THEN
SET res=(SELECT score1 FROM InterfaceScore WHERE interfaceItem_uid=i_uid AND method=m);
ELSEIF s = "2" THEN
SET res=(SELECT score2 FROM InterfaceScore WHERE interfaceItem_uid=i_uid AND method=m);
ELSE 
SET res=(SELECT score FROM InterfaceScore WHERE interfaceItem_uid=i_uid AND method=m);
END IF;
RETURN res;
END$$
DELIMITER ;


DROP VIEW IF EXISTS PdbChains;
CREATE VIEW PdbChains AS 
SELECT p.uid AS pdbInfo_uid,p.pdbCode AS pdbCode,group_concat(concat_ws(',',c.repChain,c.memberChains) separator',') AS chains 
FROM (PdbInfo p join ChainCluster c on((p.uid = c.pdbInfo_uid))) 
GROUP BY c.pdbInfo_uid; 


DROP VIEW IF EXISTS full_table;
CREATE VIEW full_table AS
SELECT
p.pdbCode,
p.resolution,
p.rfreeValue RFree,
p.expMethod,
p.spaceGroup,
c.chains,
(length(c.chains)+1)/2 c,
i.interfaceId,
i.chain1,
i.chain2,
i.area,
i.operator,
i.operatorType,
i.infinite,
get_homologs(p.uid,i.chain1) homologs1,
get_idcutoff(p.uid,i.chain1) idcutoff1,
get_homologs(p.uid,i.chain2) homologs2,
get_idcutoff(p.uid,i.chain2) idcutoff2,
score(i.uid,"eppic-gm","1") gm1,
score(i.uid,"eppic-gm","2") gm2,
score(i.uid,"eppic-gm","final") gm,
pred(i.uid,"eppic-gm") Geometry,
score(i.uid,"eppic-cr","1") cr1,
score(i.uid,"eppic-cr","2") cr2,
score(i.uid,"eppic-cr","final") cr,
pred(i.uid,"eppic-cr") CoreRim,
score(i.uid,"eppic-cs","1") cs1,
score(i.uid,"eppic-cs","2") cs2,
score(i.uid,"eppic-cs","final") cs,
pred(i.uid,"eppic-cs") CoreSur,
pred(i.uid,"eppic") final
FROM PdbInfo as p
INNER JOIN InterfaceCluster AS ic ON ic.pdbInfo_uid=p.uid
INNER JOIN Interface AS i ON i.interfaceCluster_uid=ic.uid
INNER JOIN PdbChains AS c ON c.pdbInfo_uid=p.uid
WHERE p.pdbCode IS NOT NULL;
#INNER JOIN Job AS j ON j.uid=p.jobItem_uid AND length(j.jobId)=4 AND j.status="Finished";

EOF




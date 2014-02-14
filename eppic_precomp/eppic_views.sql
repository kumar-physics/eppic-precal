


DROP FUNCTION IF EXISTS get_result;
DELIMITER $$
CREATE FUNCTION get_result(interfaceid INT,met VARCHAR(255)) RETURNS VARCHAR(255)
BEGIN
DECLARE res VARCHAR(255);
SET res=(SELECT callName FROM InterfaceScore WHERE interfaceItem_uid=interfaceid and method like met);
RETURN res;
END $$
DELIMITER ;

DROP FUNCTION IF EXISTS get_homologs;
DELIMITER $$
CREATE FUNCTION get_homologs(pdbuid INT,chain VARCHAR(255)) RETURNS INT(12)
BEGIN
DECLARE x INT(12);
SET x=(SELECT numHomologs 
FROM HomologsInfoItem 
WHERE pdbScoreItem_uid=pdbuid 
AND chains LIKE BINARY CONCAT("%",chain,"%"));
RETURN x;
END$$
DELIMITER ;

DROP VIEW IF EXISTS webview;
CREATE VIEW webview as
SELECT 
p.pdbName,
p.expMethod,
p.resolution,
get_homologs(p.uid,i.chain1) h1,
get_homologs(p.uid,i.chain2) h2,
i.id,
i.area,
i.isInfinite,
i.size1,
i.size2,
get_result(i.uid,"Geometry") geometry,
get_result(i.uid,"Entropy") corerim,
get_result(i.uid,"Z-scores") coresurface,
i.finalCallName final
from PdbScore as p inner join Interface as i
on i.pdbScoreItem_uid=p.uid inner join Job as j on length(j.jobId)=4 and j.uid=p.jobItem_uid;

drop view if exists dc_bio;
create view dc_bio as 
select * from webview as w inner join benchmark.dc_bio as dc on w.pdbName=dc.pdb and w.id=dc.interfaceid;
drop view if exists dc_xtal;
create view dc_xtal as 
select * from webview as w inner join benchmark.dc_xtal as dc on w.pdbName=dc.pdb and w.id=dc.interfaceid; 

drop view if exists po_bio;
create view po_bio as 
select * from webview as w inner join benchmark.ponstingl_bio as dc on w.pdbName=dc.pdb and w.id=dc.interfaceid;
drop view if exists po_xtal;
create view po_xtal as 
select * from webview as w inner join benchmark.ponstingl_xtal as dc on w.pdbName=dc.pdb and w.id=dc.interfaceid; 

drop view if exists many_bio;
create view many_bio as
select * from webview where size1>10 and size2>10 and resolution<2.5 and area>1000 and area<2000;

drop view if exists many_xtal;
create view many_xtal as
select * from webview where resolution<2.5 and isInfinite=1 and area>1000;









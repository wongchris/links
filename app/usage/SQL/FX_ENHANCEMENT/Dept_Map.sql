select 
case when mat.ae_team_name like 'PRC-TEAM 1-MAINLAND%' then 'CN' 
	 when mat.ae_team_name like 'PRC-TEAM 1-FUTURES%' then 'CN'
	 when (mat.ae_team_id in ( 'PRC-SFD', 'PRC-IBDRF', 'PRC-ZBRF', 
		'PRC-AEHK', 'PRC-TEAM 2', 'HQR')
		or
		mat.ae_team_name like 'PRC-MKT%') then 'CN'
	 when mat.ae_team_id like 'PRC-MKT%' then 'CN'
	 when mat.ae_team_id like '%PRC-SPD%' then 'CN'
	 when (mat.ae_team_id = 'HKG_H TEAM' or mat.ae_team_id = 'HKG_PB') then 'HK'
	 when mat.ae_team_id between 'H0000' and 'H9999ZZ' then 'HK'
	 when mat.ae_team_id between 'H0000' and 'H9999ZZ' then 'HK'
	 when (mat.ae_team_id in ('HKG_A TEAM', 'HKG_WM') or mat.ae_team_id between 'A0000' and 'A9999ZZ') then 'HK'
	 when mat.ae_team_id ='INS' then 'INS'
	 when mat.ae_team_id in ('ZBD', 'AMT', 'FPI', 'HQ', 'STF', 'ERR') then 'OTHERS'
else 'N/A' end AS department,
ma.account_no

from MST_ACCOUNT ma
inner join MST_AE mae
on ma.ae_code = mae.ae_code
inner join MST_AE_TEAM mat
on mae.ae_team_id = mat.ae_team_id
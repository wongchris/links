select ISNULL(ma2.account_no, ma.account_no) as account_group_main
	  ,ISNULL(ma2.account_name2, ma.account_name2) as account_name2_main
	  ,ISNULL(ma2.account_name, ma.account_name) as account_name_main
	  ,case when ac.country_code = 'N/A' then ac2.country_name else ac.country_name end as country_name
	  ,ma.account_no
from mst_main_account mma
inner join mst_account ma
on mma.main_account_no = ma.account_no
inner join mst_ae mae
on mae.ae_code = ma.ae_code
left join mst_account ma2
on mma.account_group = ma2.account_no
inner join MST_ACCOUNT_IDENTITY mai
on ISNULL(ma2.account_no, ma.account_no)  = mai.account_no
inner join MST_IDENTITY mi
on mi.id_row_no = mai.id_row_no
left join ADM_COUNTRY ac
on ac.country_code = mi.country_code
left join ADM_COUNTRY ac2
on ac2.country_code = mi.place_of_birth
where mma.chk_status = 'A'
and ma.chk_status = 'A'
and mae.ae_code in <<param_ae_code>>

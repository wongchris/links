select account_no, 
	   trade_ccy, 
	   sum(month_com) as month_com, 
	   sum(year_com) as year_com 
from 
(
select account_no, 
trade_ccy,
tctf.commission as month_com,
0				as year_com
from trn_client_trade tct
inner join VIEW_TRN_CLIENT_TRADE_FEE_V2 tctf
on tct.ref_no = tctf.ref_no
where tct.chk_status = 'A'
and tct.trade_date >= <<param_start_date>>
and tct.trade_date <= <<param_end_date>>
and tct.ae_code in <<param_ae_code>>

UNION ALL

select account_no, 
trade_ccy,
0				as month_com,
tctf.commission	as year_com
from trn_client_trade tct
inner join VIEW_TRN_CLIENT_TRADE_FEE_V2 tctf
on tct.ref_no = tctf.ref_no
where tct.chk_status = 'A'
and tct.trade_date >= left(<<param_end_date>>,4) +'-01-01'
and tct.trade_date <= <<param_end_date>>
and tct.ae_code in <<param_ae_code>>
) tmp
group by tmp.account_no, tmp.trade_ccy


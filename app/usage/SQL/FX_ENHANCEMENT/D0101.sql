SELECT 
        BAB.company_code AS company_code                      , 
        BAB.ccy          AS ccy                               , 
        BAB.account_no   AS account_no                        , 
        MA.account_name  AS account_name                      , 
        MA.account_name2 AS chinese_name                      , 
        MA.ae_code       AS ae_code                           , 
        MMA.main_account_type                                 , 
        bals.ledger_baL                  AS ledger_bal        , 
        bals.avail_bal                   AS avail_bal         , 
        (BAB.ledger_in + BAB.ledger_out) AS forward_amt       , 
        BAB.t1_net_bs                    AS t1_net_settle_amt , 
        BAB.t2_net_bs                    AS t2_net_settle_amt , 
        BAB.t3_net_bs                    AS t3_net_settle_amt , 
        BAB.tn_net_bs                    AS tn_net_settle_amt , 
        BAB.accrued_dr_int               AS accrued_dr_int    , 
        BAB.accrued_cr_int               AS accrued_cr_int    , 
        ISNULL(HAIB.day_int_update, 0)   AS day_int           , 
        (BAB.ledger_in + BAB.ledger_out) AS forward_amt       , 
        MAE.ae_team_id                   AS ae_team_id 
FROM 
        BAL_ACCOUNT_BALANCE BAB(NOLOCK) 
INNER JOIN SYS_SYSTEM SS on 1=1
LEFT JOIN HST_ACCOUNT_INTEREST_BALANCE HAIB(NOLOCK)
ON BAB.account_no = HAIB.account_no
AND BAB.company_code = HAIB.company_code
AND BAB.ccy = HAIB.ccy
AND
        ( BAB.accrued_cr_int          <> 0
                OR BAB.accrued_dr_int <> 0 )
AND HAIB.int_date = SS.sys_date
INNER JOIN MST_ACCOUNT MA(NOLOCK)       ON BAB.account_no     = MA.account_no
INNER JOIN MST_AE MAE(NOLOCK)           ON MA.ae_code         = MAE.ae_code 
INNER JOIN MST_MAIN_ACCOUNT MMA(NOLOCK) ON MA.main_account_no = MMA.main_account_no OUTER APPLY 
        (SELECT 
                (BAB.day_open  + BAB.auto_settle + BAB.cash_in + BAB.cash_out + BAB.cheque_in + BAB.cheque_out + BAB.today_net_bs + BAB.today_net_pl)                                                                                                   AS avail_bal, 
                ( BAB.day_open + BAB.auto_settle + BAB.cash_in + BAB.cash_out + BAB.cheque_in + BAB.cheque_out + BAB.today_net_bs + BAB.today_net_pl + BAB.ledger_in + BAB.ledger_out + BAB.t1_net_bs + BAB.t2_net_bs + BAB.t3_net_bs + BAB.tn_net_bs ) AS ledger_baL 
        ) bals 
where   (MA.account_status <>'C' 
                OR 
                (MA.account_status ='C' 
                        AND 
                        (BAB.day_open + BAB.auto_settle + BAB.cash_in + BAB.cash_out + BAB.cheque_in + BAB.cheque_out + BAB.today_net_bs + BAB.today_net_pl) 
                        <>0 
                        OR 
                        ( BAB.day_open + BAB.auto_settle + BAB.cash_in + BAB.cash_out + BAB.cheque_in + BAB.cheque_out + BAB.today_net_bs + BAB.today_net_pl + BAB.ledger_in + BAB.ledger_out + BAB.t1_net_bs + BAB.t2_net_bs + BAB.t3_net_bs + BAB.tn_net_bs ) 
                        <> 0 )) 
order by 
        BAB.company_code, 
        BAB.account_no  , 
        BAB.ccy
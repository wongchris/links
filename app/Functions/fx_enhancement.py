from app.models import Database
import pyodbc
import os
from app.Utils.sys_dir import SystemPath
import pandas as pd
import json
import datetime


class FxEnhancement():

    def __init__(self, database, fx_file, export_path):
        self.fx_file = fx_file
        self.app_dir = SystemPath.APP_DIR
        self.project_dir = SystemPath.PROJECT_DIR
        self.sql_dir = os.path.join(SystemPath.SQL_DIR, "FX_ENHANCEMENT")
        self.map_dir = os.path.join(SystemPath.MAP_DIR, "FX_ENHANCEMENT")
        self.export_path = export_path
        try:
            server = database.host
            user = database.login
            password = database.get_password()
            db = database.db_name
            driver = database.driver
            remark = database.remark
            self.conn = pyodbc.connect('driver={%s};server=%s;database=%s;uid=%s;pwd=%s' % (driver, server, db, user, password))
        except:
            print("DB Connection Error")

    def export_file(self):
        fd = open(os.path.join(self.sql_dir, 'D0101.sql'), 'r')
        d0101_list = fd.read()
        # account_list = account_list.replace("<<param_ae_code>>", ae_code)
        fd.close()
        dfD0101 = pd.read_sql_query(d0101_list, self.conn)

        print("D0101 Data Retrieved...")

        fd = open(os.path.join(self.sql_dir, 'Dept_Map.sql'), 'r')
        dept_map_list = fd.read()
        # account_list = account_list.replace("<<param_ae_code>>", ae_code)
        fd.close()
        dfDept = pd.read_sql_query(dept_map_list, self.conn)

        print("Department Mapping Retrieved...")

        print("Data Processing...")

        targetD0101 = dfD0101.loc[(dfD0101['ccy'] != 'HKD') & (dfD0101['avail_bal'] < 0)]
        templist1 = targetD0101['account_no']
        # targetAcctList
        target_2_D0101 = dfD0101.loc[(dfD0101['avail_bal'] < 0) & (dfD0101['ccy'] == 'HKD')]
        target_2_D0101_2 = dfD0101.loc[
            (dfD0101['account_no'].isin(target_2_D0101['account_no'])) & (dfD0101['ccy'] != 'HKD') & (
                        dfD0101['avail_bal'] != 0)]

        templist2 = target_2_D0101_2['account_no']

        templist = templist1.tolist() + templist2.tolist()

        targetAcctList = dfD0101.loc[dfD0101['account_no'].isin(templist)]
        targetAcctList = targetAcctList.reset_index()

        print("Export Data to Excels...")
        dfAll = pd.merge(targetAcctList, dfDept, how='inner', on=['account_no'])


        dfFinal = dfAll[
            ['department', 'ccy', 'account_no', 'account_name', 'ae_code', 'main_account_type', 'avail_bal']]

        fd = open(os.path.join(self.sql_dir, 'SPSAAcct.sql'), 'r')
        spsa_list = fd.read()
        fd.close()
        dfSpsa = pd.read_sql_query(spsa_list, self.conn)

        print("SPSA Acct Retrieved...")

        dfFinal = dfFinal[~dfFinal.account_no.isin(dfSpsa['account_no'])]

        depts = dfFinal.department.unique()
        for dept in depts:
            to_xls = dfFinal.loc[(dfFinal['department'] == dept)]
            dept = dept.replace('/', '')
            to_xls.to_excel(os.path.join(self.export_path,
                                         datetime.datetime.now().strftime("%Y-%m-%d") + '_' + dept + '.xlsx'),
                            sheet_name='Sheet1', index=False)

        print("Program Part 1 End...")

        print("Program Part 2 Start...")
        dfFxRate = pd.read_excel(self.fx_file, sheet_name='Sheet1')

        # dfFxRate = pd.read_sql_query(fx_rate_list, self.conn)

        print("FX RATE Data Retrieved...")

        fd = open(os.path.join(self.sql_dir, 'SYS_DATE.sql'), 'r')
        sys_date = fd.read()
        fd.close()
        dfSysDate = pd.read_sql_query(sys_date, self.conn)

        print("SYS DATE Retrieved...")

        print("Filtering out SPSA records...")
        dfFianlWithoutSPSA = dfFinal[~dfFinal.account_no.isin(dfSpsa['account_no'])]

        print("Get Mapping File...")
        cash_io_dic = json.load(open(os.path.join(self.map_dir, "map.txt"), 'r', encoding='utf8'))

        print("Processing Cash IO File...")
        dfCashIO = pd.DataFrame(columns=['Account No', 'Currency', 'Settle Date'
            , 'Tran Type', 'Bank A/C Code', 'Cash Amount'
            , 'Remark', 'Cash Type', 'Batch Id'])

        accts = dfFianlWithoutSPSA.account_no.unique()

        def gen_cash_IO(fm_ccy, to_ccy, fm_avail, to_avail, fx_rate):
            dfCashIO = pd.DataFrame(columns=['Account No', 'Currency', 'Settle Date'
                , 'Tran Type', 'Bank A/C Code', 'Cash Amount'
                , 'Remark', 'Cash Type', 'Batch Id'])
            dfCashIO.loc[-1] = [row['account_no'], fm_ccy,
                                dfSysDate['sys_date'][0].strftime("%d/%m/%Y")
                , cash_io_dic["TranType"], cash_io_dic["bankAcctCode"]
                , "{0:.2f}".format(fm_avail), cash_io_dic["RemarkPrefix"] + str(fx_rate)
                , cash_io_dic["CashType"], cash_io_dic["BatchId"]]  # adding a row
            dfCashIO.index = dfCashIO.index + 1  # shifting index

            dfCashIO.loc[-1] = [row['account_no'], to_ccy, dfSysDate['sys_date'][0].strftime("%d/%m/%Y")
                , cash_io_dic["TranType"], cash_io_dic["bankAcctCode"]
                , "{0:.2f}".format(to_avail), cash_io_dic["RemarkPrefix"] + str(fx_rate)
                , cash_io_dic["CashType"], cash_io_dic["BatchId"]]  # adding a row
            dfCashIO.index = dfCashIO.index + 1  # shifting index
            dfCashIO = dfCashIO.sort_index()  # sorting by index
            return dfCashIO

        for acct in accts:
            dfAcct = dfFianlWithoutSPSA.loc[dfFianlWithoutSPSA['account_no'] == acct]
            dfAcct = dfAcct.sort_values('ccy', ascending=False)
            for index, row in dfAcct.iterrows():
                # loop all the negative records - other ccy first
                if dfAcct.at[index, 'ccy'] != "HKD" and dfAcct.at[index, 'avail_bal'] < 0:
                    # use HKD to fully cover negative records and update
                    for index_hkd, row_hkd in dfAcct.iterrows():
                        if dfAcct.at[index_hkd, 'ccy'] == "HKD" and dfAcct.at[index_hkd, 'avail_bal'] > 0 and dfAcct.at[index, 'avail_bal'] < 0:
                            dfCCY = dfFxRate.loc[(dfFxRate['fm_ccy'] == dfAcct.at[index_hkd, 'ccy']) & (
                                        dfFxRate['to_ccy'] == row['ccy'])].reset_index()
                            if not dfCCY.empty:
                                fx_rate = dfCCY['last_rate'][0]
                                neg_ccy_avail_hkd = fx_rate * dfAcct.at[index, 'avail_bal']
                                if dfAcct.at[index_hkd, 'avail_bal'] >= abs(neg_ccy_avail_hkd):
                                    dfCashIO = dfCashIO.append(gen_cash_IO(dfAcct.at[index_hkd, 'ccy'], row['ccy']
                                                                           , neg_ccy_avail_hkd,
                                                                           abs(dfAcct.at[index, 'avail_bal']), fx_rate),
                                                               ignore_index=True)
                                    dfAcct.at[index_hkd, 'avail_bal'] = dfAcct.at[index_hkd, 'avail_bal'] + neg_ccy_avail_hkd
                                    dfAcct.at[index, 'avail_bal'] = 0

                    # use HKD to partly cover negative records and update
                    for index_hkd_2, row_hkd_2 in dfAcct.iterrows():
                        if dfAcct.at[index_hkd_2, 'ccy'] == "HKD" and dfAcct.at[index_hkd_2, 'avail_bal'] > 0 and \
                                dfAcct.at[index, 'avail_bal'] < 0:
                            dfCCY = dfFxRate.loc[(dfFxRate['fm_ccy'] == dfAcct.at[index_hkd_2, 'ccy']) & (
                                        dfFxRate['to_ccy'] == row['ccy'])].reset_index()
                            if not dfCCY.empty:
                                fx_rate = dfCCY['last_rate'][0]
                                neg_ccy_avalid_hkd_2 = fx_rate * dfAcct.at[index, 'avail_bal']
                                if dfAcct.at[index_hkd_2, 'avail_bal'] < abs(neg_ccy_avalid_hkd_2):
                                    dfCashIO = dfCashIO.append(gen_cash_IO(dfAcct.at[index_hkd_2, 'ccy'], row['ccy']
                                                                           , dfAcct.at[index_hkd_2, 'avail_bal'] * -1, abs(dfAcct.at[index_hkd_2, 'avail_bal'] / fx_rate), fx_rate), ignore_index=True)
                                    dfAcct.at[index, 'avail_bal'] = dfAcct.at[index, 'avail_bal'] + dfAcct.at[index_hkd_2, 'avail_bal'] / fx_rate
                                    dfAcct.at[index_hkd_2, 'avail_bal'] = 0

                    # use other ccy to fully cover negative records and update
                    for index_other_ccy, row_other_ccy in dfAcct.iterrows():
                        if dfAcct.at[index_other_ccy, 'ccy'] != "HKD" and dfAcct.at[
                            index_other_ccy, 'avail_bal'] > 0 and dfAcct.at[index, 'avail_bal'] < 0:
                            dfCCY = dfFxRate.loc[(dfFxRate['fm_ccy'] == dfAcct.at[index_other_ccy, 'ccy']) & (
                                        dfFxRate['to_ccy'] == row['ccy'])].reset_index()
                            if not dfCCY.empty:
                                fx_rate = dfCCY['last_rate'][0]
                                neg_ccy_avalid_other_ccy = fx_rate * dfAcct.at[index, 'avail_bal']
                                if dfAcct.at[index_other_ccy, 'avail_bal'] >= abs(neg_ccy_avalid_other_ccy):
                                    dfCashIO = dfCashIO.append(gen_cash_IO(dfAcct.at[index_other_ccy, 'ccy'], row['ccy']
                                                                           , neg_ccy_avalid_other_ccy,
                                                                           abs(dfAcct.at[index, 'avail_bal']), fx_rate),
                                                               ignore_index=True)
                                    dfAcct.at[index_other_ccy, 'avail_bal'] = dfAcct.at[index_other_ccy, 'avail_bal'] + neg_ccy_avalid_other_ccy
                                    dfAcct.at[index, 'avail_bal'] = 0

                    # use other ccy to partly cover negative records and update
                    for index_other_ccy_2, row_other_ccy_2 in dfAcct.iterrows():
                        if dfAcct.at[index_other_ccy_2, 'ccy'] != "HKD" and dfAcct.at[
                            index_other_ccy_2, 'avail_bal'] > 0 and dfAcct.at[index, 'avail_bal'] < 0:
                            dfCCY = dfFxRate.loc[(dfFxRate['fm_ccy'] == dfAcct.at[index_other_ccy_2, 'ccy']) & (
                                        dfFxRate['to_ccy'] == row['ccy'])].reset_index()
                            if not dfCCY.empty:
                                fx_rate = dfCCY['last_rate'][0]
                                neg_ccy_avalid_other_ccy_2 = fx_rate * dfAcct.at[index, 'avail_bal']
                                if dfAcct.at[index_other_ccy, 'avail_bal'] < abs(neg_ccy_avalid_other_ccy_2):
                                    dfCashIO = dfCashIO.append(
                                        gen_cash_IO(dfAcct.at[index_other_ccy_2, 'ccy'], row['ccy']
                                                    , dfAcct.at[index_other_ccy_2, 'avail_bal'] * -1,
                                                    abs(dfAcct.at[index_other_ccy_2, 'avail_bal'] / fx_rate), fx_rate),
                                        ignore_index=True)
                                    dfAcct.at[index, 'avail_bal'] = dfAcct.at[index, 'avail_bal'] + dfAcct.at[
                                        index_other_ccy_2, 'avail_bal'] / fx_rate
                                    dfAcct.at[index_other_ccy_2, 'avail_bal'] = 0

                    # use HKD to partly cover all records(include negative HKD record)
                    for index_hkd_3, row_hkd_3 in dfAcct.iterrows():
                        if dfAcct.at[index_hkd_3, 'ccy'] == "HKD" and dfAcct.at[index, 'avail_bal'] < 0:
                            dfCCY = dfFxRate.loc[(dfFxRate['fm_ccy'] == dfAcct.at[index_hkd_3, 'ccy']) & (
                                        dfFxRate['to_ccy'] == row['ccy'])].reset_index()
                            if not dfCCY.empty:
                                fx_rate = dfCCY['last_rate'][0]
                                neg_ccy_avalid_hkd_3 = fx_rate * dfAcct.at[index, 'avail_bal']
                                dfCashIO = dfCashIO.append(gen_cash_IO(dfAcct.at[index_hkd_3, 'ccy'], row['ccy']
                                                                       , neg_ccy_avalid_hkd_3,
                                                                       abs(dfAcct.at[index, 'avail_bal']), fx_rate),
                                                           ignore_index=True)
                                dfAcct.at[index_hkd_3, 'avail_bal'] = dfAcct.at[index_hkd_3, 'avail_bal'] + neg_ccy_avalid_hkd_3
                                dfAcct.at[index, 'avail_bal'] = 0
                                # Gen Cash In Out Record

            for index, row in dfAcct.iterrows():
                # use Other ccy to cover HKD records
                if dfAcct.at[index, 'ccy'] == "HKD" and dfAcct.at[index, 'avail_bal'] < 0:
                    for index_other_ccy, row_other_ccy in dfAcct.iterrows():
                        if dfAcct.at[index_other_ccy, 'ccy'] != "HKD" and dfAcct.at[index_other_ccy, 'avail_bal'] > 0:
                            dfCCY = dfFxRate.loc[(dfFxRate['fm_ccy'] == dfAcct.at[index_other_ccy, 'ccy']) & (
                                        dfFxRate['to_ccy'] == dfAcct.at[index, 'ccy'])].reset_index()
                            if not dfCCY.empty:
                                fx_rate = dfCCY['last_rate'][0]
                                neg_hkd_avail_other_ccy = fx_rate * dfAcct.at[index, 'avail_bal']
                                if abs(neg_hkd_avail_other_ccy) <= dfAcct.at[index_other_ccy, 'avail_bal']:
                                    dfCashIO = dfCashIO.append(
                                        gen_cash_IO(dfAcct.at[index_other_ccy, 'ccy'], row['ccy']
                                                    , neg_hkd_avail_other_ccy, abs(dfAcct.at[index, 'avail_bal']),
                                                    fx_rate), ignore_index=True)
                                    dfAcct.at[index_other_ccy, 'avail_bal'] = dfAcct.at[index_other_ccy, 'avail_bal'] + neg_hkd_avail_other_ccy
                                    dfAcct.at[index, 'avail_bal'] = 0
                                    # Gen Cash In Out Record
                                else:
                                    dfCashIO = dfCashIO.append(
                                        gen_cash_IO(dfAcct.at[index_other_ccy, 'ccy'], row['ccy']
                                                    , dfAcct.at[index_other_ccy, 'avail_bal'] * -1,
                                                    dfAcct.at[index_other_ccy, 'avail_bal'] / fx_rate,
                                                    fx_rate), ignore_index=True)
                                    dfAcct.at[index, 'avail_bal'] = dfAcct.at[index, 'avail_bal'] + dfAcct.at[index_other_ccy, 'avail_bal'] / fx_rate
                                    dfAcct.at[index_other_ccy, 'avail_bal'] = 0
                                    # Gen Cash In Out Record

        print("Export Cash IO to Excels...")
        dfCashIO.to_excel(
            os.path.join(self.export_path,
                         datetime.datetime.now().strftime("%Y-%m-%d") + '_' + cash_io_dic["file_name"] + '.xlsx'),
            sheet_name='Sheet1', index=False)

        print("Program Part 2 End...")
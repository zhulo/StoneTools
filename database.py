import time

import pymysql


class OperateSQL(object):
    def __init__(self, config):
        self.config = config
        self.conn = pymysql.connect(**self.config, charset='utf8')
        self.cursor = self.conn.cursor(cursor=pymysql.cursors.DictCursor)

    # 查询一条数据
    def query(self, sql, fetch='one'):
        try:
            for i in range(10):
                self.cursor.execute(sql)
                if fetch == 'one':
                    result = self.cursor.fetchone()
                    print("Query {} Database, SQL '{}', result '{}'".format(self.config, sql, result))
                    if result is not None:
                        return result
                if fetch == 'all':
                    result = self.cursor.fetchall()
                    print("Query {} Database, SQL '{}', result '{}'".format(self.config, sql, result))
                    if result is not None:
                        return result
                time.sleep(2)
            return None
        except Exception as e:
            print("Connect/Query {} Database error,SQL {}, msg: '{}'".format(self.config, sql, e))
        finally:
            self.cursor.close()
            self.conn.close()

    # 修改数据相关（增删改查）
    def modify(self, sql):
        try:
            result = self.cursor.execute(sql)
            self.conn.commit()
            print("Update Database {}, SQL '{}', Affected rows '{}'".format(self.config, sql, result))
        except Exception as e:
            self.conn.rollback()
            print("Connect/Modify {} Database error,SQL {}, msg: '{}'".format(self.config, sql, e))
        finally:
            self.cursor.close()
            self.conn.close()


def update_repay(loan_id):
    config = {'host': '18.16.200.42', 'database': 'invstone-shb-real', 'user': 'root', 'password': 'shitou$root'}
    step1 = "UPDATE t_loan_info SET LOANS_TIME = DATE_FORMAT(DATE_ADD(loans_time,INTERVAL - 1  MONTH),'%%Y-%%m-%%d %%T') WHERE loan_id = %s" % loan_id
    step2 = "UPDATE t_loan_repay_plan  SET repaytime = DATE_FORMAT(DATE_ADD(repaytime,INTERVAL - 1 MONTH),'%%Y-%%m-%%d %%T')  WHERE loanid = %s" % loan_id
    step3 = "UPDATE t_loan_repay_plan SET days = DATEDIFF(repaytime,DATE_FORMAT(DATE_ADD(repaytime,INTERVAL - 1 MONTH),'%%Y-%%m-%%d %%T')) WHERE loanid = %s" % loan_id
    step4 = "UPDATE t_loan_repay_plan t1,t_loan_repay_userplan t2 SET t2.`REPAY_TIME` = t1.`REPAYTIME` WHERE t1.`ID` = t2.`PLANID` AND t1.`ISSUE` = t2.`ISSUE` AND t1.`LOANID` = t2.`LOANID` AND t1.`LOANID` = %s" % loan_id
    OperateSQL(config).modify(step1)
    OperateSQL(config).modify(step2)
    OperateSQL(config).modify(step3)
    OperateSQL(config).modify(step4)


if __name__ == '__main__':
    update_repay(loan_id=47262)

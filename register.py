import random
from datetime import date
from datetime import timedelta


def china_phone():
    tel_header = [
        '130', '133', '132', '133', '134', "136", "137",
        "138", "139", "147", "150", "151", "152", "153",
        "155", "156", "157", "158", "159", "186", "187", "188"]
    result = random.choice(tel_header) + "".join(
        random.choice("0123456789") for i in range(8))
    print('手机号 {}'.format(result))
    return result


def china_name():
    last_names = []
    with open('name.txt', "rb") as file:
        for i in file:
            last_names.append(i.strip().decode('utf-8').split("   ")[1])
    num1 = random.randint(1, 127)
    num2 = random.randint(1, 127)
    num3 = random.randint(1, 127)
    nameOld = last_names[num1] + last_names[num2] + last_names[num3]
    nameNew = ''.join(nameOld.split())
    print('姓名 {}'.format(nameNew))
    return nameNew


def bank_id():
    file_path = 'bank.txt'
    try:
        with open(file_path, 'r') as init_data:
            init_bank_id = init_data.readline()
        with open(file_path, 'w') as update_data:
            update_data.write(str(int(init_bank_id) + 1))
        with open(file_path, 'r') as load_data:
            load_bank_id = load_data.readline()
        if int(load_bank_id) >= 6214664212313320500 \
                and int(load_bank_id) <= 6214664212313321000:
            print('建设银行卡号 {}'.format(load_bank_id))
            return load_bank_id
        else:
            print('汇付托管建设银行卡卡号超过限制了,更换银行卡卡段')
    except Exception as e:
        print('读取更新汇付托管建设银行卡卡号异常 %s' % e)


class ChinaCardId(object):

    def __init__(self):
        self.china_path = 'china.txt'

    def china(self):
        '''
        随机生成中国城市、省份、代码
        :return:
        '''
        with open(self.china_path, encoding='utf-8') as f:
            data = f.read()
            chinaList = data.split('\n')
        for node in chinaList:
            if node[10:11] != ' ':
                state = node[10:].split()
            if node[10:11] == ' ' and node[12:13] != ' ':
                city = node[12:].split()
            if node[10:11] == ' ' and node[12:13] == ' ':
                district = node[14:].split()
                code = node[0:6]
                CodeList.append({'state': state, 'city': city, 'district': district, 'code': code})

    def cardid(self):
        '''
        随机生成有规则的身份证号，校检码算法有问题，但身份证号码可正常注册
        全局变量 codelist
        :return:
        '''
        global CodeList
        CodeList = []
        if not CodeList:
            ChinaCardId().china()
        id = CodeList[random.randint(0, len(CodeList))]['code']  # 地区
        id = id + str(random.randint(1975, 1995))  # 年份
        month = date.today() + timedelta(days=random.randint(1, 365))  # 月份
        id = id + month.strftime('%m%d')
        id = id + str(random.randint(100, 300))  # ，顺序号简单处理
        # print(id)

        i = 0
        count = 0
        weight = [7, 9, 10, 5, 8, 4, 2, 1, 6, 3, 7, 9, 10, 5, 8, 4, 2]  # 权重项
        checkCode = {'0': '1', '1': '0', '2': 'X', '3': '9', '4': '8', '5': '7', '6': '6', '7': '5', '8': '4', '9': '3',
                     '10': '2'}  # 校验码映射
        '''
        第十八位数字的身份证校检码算法
        将前面的身份证号码17位数分别乘以不同的系数。从第一位到第十七位的系数分别为：[7, 9, 10, 5, 8, 4, 2, 1, 6, 3, 7, 9, 10, 5, 8, 4, 2]
        将这17位数字和系数相乘的结果相加。
        用加出来和除以11，看余数是多少
        余数只可能有0,1,2,3,4,5,6,7,8,9,10
        这11个数字。其分别对应的最后一位身份证的号码为{'0': '1', '1': '0', '2': 'X', '3': '9', '4': '8', '5': '7', '6': '6', '7': '5', '8': '4', '9': '3',
                     '10': '2'}
        '''

        for a in range(0, len(id)):
            count += int(id[a]) * weight[a]
        id = id + checkCode[str(count % 11)]
        print('身份照号码 {}'.format(id))
        return id


def china_card_id():
    return ChinaCardId().cardid()


if __name__ == '__main__':
    china_name()
    china_phone()
    china_card_id()
    bank_id()

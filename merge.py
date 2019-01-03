import time
from datetime import datetime
from time import sleep

import jenkins
import requests
import xlrd

# 更新以下三个值即可
username = 'admin'
test_token = 'a6c70fafb72711c214bff22a6b8ebc81'
pre_token = '8a768661528376bed4edf30e2a27ec90'

test_url = 'http://18.16.200.12:8080/jenkins'
pre_url = 'http://18.16.200.51:8080/jenkins'
pull_name = 'git-pull and merge'


def jenkins_info(env):
    data = {}
    if env == 'test':
        data.update({'url': test_url, 'username': username, 'password': test_token})
    elif env == 'pre':
        data.update({'url': pre_url, 'username': username, 'password': pre_token})
    else:
        print('环境错误')
    return data


class MergeBranchJenkins(object):
    def __init__(self, env, items, branch_list):
        self.git_url_list = []
        self.job_name_list = []
        self.env = env
        self.items = items
        self.branch_list = branch_list
        self.data = jenkins_info(env)

        self.server = jenkins.Jenkins(self.data['url'],
                                      username=self.data['username'],
                                      password=self.data['password']
                                      )
        self.wb = xlrd.open_workbook('branch.xlsx')
        sheet = self.wb.sheets()[0]
        for i in items:
            for row in range(0, sheet.nrows):
                excel_list = sheet.row_values(row)
                if excel_list[3] == i:
                    self.git_url_list.append(excel_list[0])
                    if self.env == 'test':
                        self.job_name_list.append(excel_list[1])
                    if self.env == 'pre':
                        self.job_name_list.append(excel_list[2])
        print('核对git url:{}'.format(self.git_url_list))
        print('核对job_name:{}'.format(self.job_name_list))

    def pull_merge_branch(self, i):
        params = {}
        if self.env == 'test':
            pull_params = {'GIT_URL': self.git_url_list[i],
                           'CODE_BRANCH': self.branch_list[i],
                           'GIT_APP_NAME': self.items[i],
                           'token': self.data['password']}
            params.update(pull_params)
        elif self.env == 'pre':
            now = time.strftime('_%Y%m%d%H%M', time.localtime(time.time()))
            tag = str(self.items[i]) + ''.join(now)
            pull_params = {'GIT_URL': self.git_url_list[i],
                           'CODE_BRANCH': self.branch_list[i],
                           'GIT_APP_NAME': self.items[i],
                           'TAG': tag,
                           'token': self.data['password']}
            params.update(pull_params)
        print('┌--{}'.format('-' * 100))
        print('├ 开始合并第 %s 个分支 %s ' % (i + 1, self.branch_list[i]))
        print('├ 参数 %s' % params)
        print('└--{}'.format('-' * 100))
        self.server.build_job(pull_name, params)
        sleep(3)
        while True:
            last_build_url = self.server.get_job_info(
                pull_name)['lastBuild']['url'] + 'api/json'
            if self.env == 'pre':
                last_build_url = last_build_url.replace("http://18.16.200.51:8080/",
                                                        "http://18.16.200.51:8080/jenkins/")
            result = requests.get(last_build_url).text
            if self.branch_list[i] in result and username in result:
                build_number = self.server.get_job_info(pull_name)['lastBuild']['number']
                while 1:
                    status = self.server.get_build_info(pull_name, build_number)['building']
                    if status == True:
                        print('{} 项目 {}, 分支 {}, 构建号 {}, 正在建构合并中......'.format(
                            datetime.now(), pull_name, self.branch_list[i], build_number))
                        sleep(3)
                    else:
                        result = self.server.get_build_info(pull_name, build_number)['result']
                        if result == 'SUCCESS':
                            print('项目 {}, 分支 {}, 构建合并结果 {}'.format(pull_name, self.branch_list[i], result))
                            return True
                        if result == 'ABORTED':
                            sleep(10)
                            print('{} 项目 {}, 分支 {}, 正在队列中...... '.format(
                                datetime.now(), pull_name, self.branch_list[i]))
                        else:
                            print('项目 {}, 分支 {}, 构建合并结果 {}, 合并代码失败，请查看详情,终止构建过程！'.format(
                                pull_name, self.branch_list[i], result))
                            return False
            else:
                sleep(5)
                print('{} 其他分支/项目正在合并，当前分支 {} 等待5s继续合并......'.format(
                    datetime.now(), self.branch_list[i]))

    def build_project(self, i):
        print('┌--{}'.format('-' * 100))
        print('├ 开始构建分支 %s 对应项目 %s ' % (self.branch_list[i], self.job_name_list[i]))
        print('└--{}'.format('-' * 100))
        job_name = str(self.job_name_list[i])
        self.server.build_job(job_name)
        sleep(3)
        while True:
            last_build_url = self.server.get_job_info(job_name)['lastBuild']['url'] + 'api/json'
            if self.env == 'pre':
                last_build_url = last_build_url.replace("http://18.16.200.51:8080/",
                                                        "http://18.16.200.51:8080/jenkins/")
            result = requests.get(last_build_url).text
            if username in result:
                build_number = self.server.get_job_info(job_name)['lastBuild']['number']
                while 1:
                    sleep(3)
                    status = self.server.get_build_info(job_name, build_number)['building']
                    if status == True:
                        print('{} 项目 {}, 构建号 {}, 正在构建中......'.format(datetime.now(), job_name, build_number))
                        sleep(10)
                    else:
                        result = self.server.get_build_info(job_name, build_number)['result']
                        if result == 'ABORTED':
                            print('{} 项目 {}, 构建号 {}, 正在队列中...... '.format(datetime.now(), job_name, build_number))
                            sleep(10)
                        elif result == 'SUCCESS':
                            print('项目 {}, 构建号 {}, 构建结果 {}'.format(job_name, build_number, result))
                            return True
                        elif result == 'UNSTABLE':
                            print(
                                '项目 {}, 构建号 {}, 构建结果 {}, 构建结果不稳定，请确认结果是否正常'.format(
                                    job_name, build_number, result))
                        else:
                            print('项目 {}, 构建号 {}, 构建结果 {}, 构建项目失败，请查看详情,终止构建过程'.format(
                                job_name, build_number, result))
                            return False

    def __call__(self):
        if len(self.branch_list) == len(self.items) == \
                len(self.git_url_list) == len(self.job_name_list):
            print('分支:        {}'.format(self.branch_list))
            print('项目:        {}'.format(self.items))
            print('git url     {}'.format(self.git_url_list))
            print('job name    {}'.format(self.job_name_list))
            for i in range(len(self.branch_list)):
                pull_result = self.pull_merge_branch(i)
                if pull_result:
                    result = self.build_project(i)
                    if result is False:
                        return
                if pull_result is False:
                    return
            print('全部构建完成')
        else:
            print('合并/构建异常，请检查以下内容')
            print('分支:        {}'.format(self.branch_list))
            print('项目:        {}'.format(self.items))
            print('git url     {}'.format(self.git_url_list))
            print('job name    {}'.format(self.job_name_list))


if __name__ == '__main__':
    # 项目列表
    items = ['1', '2']
    # 分支列表
    branch_list = ['111', '222']
    # env = pre , env = test
    run = MergeBranchJenkins(env='test', items=items, branch_list=branch_list)
    run()

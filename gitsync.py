#!/usr/bin/python
# -*- coding: UTF-8 -*-
import datetime
import os
import shutil
import sys
import time
import urllib.parse
import argparse
import json



class Logger(object):
    def __init__(self, file_name="Default.log", stream=sys.stdout):
        self.terminal = stream
        self.log = open(file_name, "a")

    def write(self, message):
        self.terminal.write(message)
        self.log.write(message)

    def flush(self):
        pass

class GitSync():
    def __init__(self, authentication, workspace):
        self.authentication = authentication
        self.workspace = workspace
        self.logger = Logger('gitsync.log')
        sys.stdout = self.logger
    
    def prints(self, message):
        print(time.strftime("%Y-%m-%d %H:%M:%S", time.localtime()), " ", message)

    def gitPush(self, config):
        '''
        推送最新的代码到目标分支
        '''
        name = config['name']
        source = config['source']
        source_branch = source['branch']
        target = config['target']
        target_branch = target['branch']

        projectPath = os.path.join(self.workspace, name)
        if os.path.exists(projectPath):
            os.system('cd "{}" && git push -u origin {}:{}'.format(projectPath, source_branch, target_branch))


    def addRepo(self, config):
        '''
         添加目标远程仓库
        '''
        name = config['name']
        target = config['target']
        projectGitUrl = target['url']
        authenticationId = target['authentication']

        projectPath = os.path.join(self.workspace, name)
        if os.path.exists(projectPath):
            if authentication and authenticationId in self.authentication:
                username = self.authentication[authenticationId]['username']
                password = self.authentication[authenticationId]['password']
                userInfo = urllib.parse.quote(username) + ":" + urllib.parse.quote(password) + "@"
                projectGitUrl = projectGitUrl.replace("http://", "http://%s" % userInfo).replace("https://",
                                                                                        "https://%s" % userInfo)
    
            os.system(
                'cd "{}" && git remote rename origin old-origin && git remote add origin {} && git push '.format(
                    projectPath, projectGitUrl))


    def gitClone(self, config):
        '''
         克隆代码到本地
        '''
        
        name = config['name']
        source = config['source']
        projectGitUrl = source['url']
        branch = source['branch']
        authenticationId = source['authentication']

        projectPath = os.path.join(self.workspace, name)
        if os.path.exists(projectPath):
            return False
        if authentication and authenticationId in self.authentication:
            username = self.authentication[authenticationId]['username']
            password = self.authentication[authenticationId]['password']
            userInfo = urllib.parse.quote(username) + ":" + urllib.parse.quote(password) + "@"
            projectGitUrl = projectGitUrl.replace("http://", "http://%s" % userInfo).replace("https://", "https://%s" % userInfo)
        os.system('cd "{}" && git clone -b "{}" "{}" "{}"'.format(self.workspace, branch, projectGitUrl, name))
        return True


    def gitPull(self, config):
        '''
        执行git仓库更新
        '''
        name = config['name']

        projectPath = os.path.join(self.workspace, name)
        if os.path.exists(projectPath):
            os.system('cd "{}" && git pull old-origin'.format(projectPath))


    def clear(self, config):
        '''
         清除本地仓库
        '''
        name = config['name']
        projectPath = os.path.join(self.workspace, name)
        if os.path.exists(projectPath):
            shutil.rmtree(projectPath)
            print(f"文件夹 {projectPath} 已成功删除")

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='GitSync')
    parser.add_argument('-w', '--workspace', type=str, default=os.getcwd(), help='工作空间路径')
    
    subparsers = parser.add_subparsers(dest='command')
    
    clone_parser = subparsers.add_parser('clone', help='批量clone')
    push_parser = subparsers.add_parser('push', help='批量push')
    push_parser = subparsers.add_parser('clear', help='批量clear')
    push_parser = subparsers.add_parser('pull', help='批量pull')

    args = parser.parse_args()

    if args.command not in ("clone", "push", "clear", "pull"):
        parser.print_help()
        exit()

    workspace = args.workspace

    starttime = time.time()
    configPath = "config.json"
    if workspace is not None:
        configPath = os.path.join(workspace, "config.json")
    # 如果不存在配置文件，则创建一个空文件
    if not os.path.exists(configPath):
        with open(configPath, "w") as fp:
            json.dump({}, fp)
        
    with open(configPath) as cfgFile:
        config = json.load(cfgFile)
        if config is not None:
            repository_list = config["repository"]
            authentication = config["authentication"]
            gitsync = GitSync(authentication, workspace)
            gitsync.prints("开始任务")
            for item in repository_list:
                if args.command == "clone":
                    gitsync.gitClone(item)
                    gitsync.addRepo(item)
                    gitsync.prints("克隆项目: {}".format(item['name']))
                if args.command == "push":
                    gitsync.gitPush(item)
                    gitsync.prints("推送项目: {}".format(item['name']))
                if args.command == "pull":
                    gitsync.gitPull(item)
                    gitsync.prints("更新项目: {}".format(item['name']))
                if args.command == "clear":
                    gitsync.clear(item)
                    gitsync.prints("删除项目: {}".format(item['name']))
            endtime = time.time()
            dtime = endtime - starttime
            gitsync.prints("程序运行时间：%.8s s" % dtime)  # 显示到微秒
        


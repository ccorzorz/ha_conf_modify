#!/usr/bin/env python
# -*-coding=utf-8-*-
# Auther:ccorz Mail:ccniubi@163.com Blog:http://www.cnblogs.com/ccorz/
# GitHub:https://github.com/ccorzorz

import json,time,os

time_now=time.strftime('%Y-%m-%d %H:%M:%S')
time_flag=time.strftime('%Y-%m-%d-%H-%M-%S')
#定义通过域名查询ha配置文件函数
def search_backend(search_info):
    """
    :param search_info: 用户输入的需要查询的域名
    :return: result_list :结果列表,供增删改使用
    """
    b_flag=1    #设置初始标识符
    result_list=[]  #设置查询结果为空列表
    with open('ha','r') as ha_read:
        for line in ha_read.readlines():    #将内容通过readlines转化为列表
            line=line.strip()   #每一行去掉两头的空格和回车
            if line=='backend %s'%search_info:  #发现内容匹配
                b_flag=0    #更改标识符值
            elif line.startswith('backend'):    #发现以'backend'开头的内容
                b_flag=1    #更改标识符为初始值
            elif b_flag==0 and  len(line)!=0:   #将标识符为0的非空内容加入查询结果列表
                result_list.append(line)
    return result_list


def add_backend():
    """
    :return: None
    """
    while True:
        add_contect_str=input('Input the server_info:') #提示用户输入配置文件信息
        res=enter_query(add_contect_str)    #将确认格式函数的返回值赋予res变量
        if res==False:  #如果变量为Flase,提醒用户输入的字符串格式不正确
            print('String format error,try again!')
        if res == True:     #如果变量值为True,即用户输入格式正确，执行以下
            # print(result_list)
            add_contect=json.loads(add_contect_str) #通过json模块，将字符串转化为列表
            search_info=add_contect['backend']  #变量赋值
            weight=add_contect['record']['weight']
            server=add_contect['record']['server']
            maxconn=add_contect['record']['maxconn']
            server_info='server %s %s weight %s maxconn %s'%(server,server,weight,maxconn)
            result_list=search_backend(search_info)     #将字符串中解析得到的列表赋值于result_list
            print(result_list)
            if len(result_list)==0:     #如果无对应的域名，新增域名以及对应的记录
                with open('ha','r') as ha_read,open('ha_new','w') as ha_wirte:
                    con_list=ha_read.readlines()        #通过readlines将ha文件中的内容转化为列表
                    con_list.append('\n')   #列表中加一空行
                    con_list.append('backend %s\n'%search_info)     #列表中新增域名信息
                    con_list.append('%s%s'%(8*' ',server_info))     #列表中追加域名对应服务器信息
                    ha_wirte.writelines(con_list)       #将列表通过writelines全部写入ha_write文件
                #回显，提示用户无域名信息，将新增信息到配置文件最后
                print('No domain target,will add to the end of the "ha",has been add the end of file..')
                time.sleep(1)
                print('\033[31;1mInformation has been added successly!!!!\033[0m')
                os.rename('ha', 'ha_bak.%s' % time_flag)  # 系统改名
                os.rename('ha_new', 'ha')
                with open('modify.log', 'a') as log:    #写入日志文件
                    log.write('%s domain %s add server info: %s\n' % (time_now, search_info, server_info))
            else:       #列表不为空
                if server_info in result_list:  #如果服务器信息重叠，提示用户信息已重叠，不操作文件
                    print('\033[31;1mThe server info had been in %s domain,do not need to add...\033[0m'%search_info)
                else:
                    result_list.append(server_info)     #服务器信息不重叠
                    with open('ha','r') as ha_read,open('ha_add','w') as ha_add:
                        a_flag=1    #设置取配置文件中目标内容的标识符
                        exit2_flag=1    #设置限制目标内容循环的标识符
                        for line in ha_read.readlines():    #转化列表，遍历列表
                            if line.strip()=='backend %s'%search_info:  #如果其中一行的内容为“backend 域名名称”,更改目标内容标识符的值
                                a_flag=0
                            # 更改目标内容标识符后，继续遍历列表，发现以backend开头的行，再次更改目标内容标识符的值，
                            # 两个标识符中间的内容为即将修改的目标内容
                            elif line.strip().startswith('backend'):
                                a_flag=1
                            if a_flag==1:   #如果非目标内容写入ha_add文件
                                ha_add.write(line)
                            elif a_flag==0 and exit2_flag==1:   #如果是目标内容，并且限制循环的标识符为初始值
                                ha_add.write('backend %s\n'%search_info)    #添加一行域名信息
                                for line in result_list:    #遍历即将修改的列表，在元素内容前加入8个空格
                                    num=result_list.index(line)
                                    result_list[num]='%s%s\n'%(8*' ',line)
                                ha_add.writelines(result_list)  #将列表中内容写入ha_add文件
                                ha_add.write('\n')  #添加一行空白行
                                exit2_flag=0    #更改限制循环标识符的初始值，使其只循环一次，避免多次写入列表中的服务器信息
                    os.rename('ha','ha_bak.%s'%time_flag)   #系统改名
                    os.rename('ha_add','ha')
                    with open('modify.log','a') as log: #写入修改日志文件
                        log.write('%s %s add server info: %s\n'%(time_now,search_info,server_info))
                    print('\033[31;1mModify success!!!!\033[0m')    #回显
            break

#定义删除函数
def del_backend(del_domain):
    with open('ha','r') as ha_read,open('ha_del','w') as ha_del:
        b_flag=1    #设置目标内容初始值
        for line in ha_read.readlines():    #将内容通过readlines转化为列表
            if line.strip()=='backend %s'%del_domain:  #发现内容匹配
                b_flag=0    #更改标识符值
            elif line.strip().startswith('backend'):    #发现以'backend'开头的内容
                b_flag=1    #更改标识符为初始值
            if b_flag==1:   #只将非目标内容写入ha_del文件
                ha_del.write(line)
    with open('modify.log', 'a') as log:    #操作日志写入日志文件
        log.write('%s delete the domain %s and the related info.\n' % (time_now, del_domain))
    os.rename('ha','ha_bak.%s'%time_flag)   #系统改名ha以及操作文件
    os.rename('ha_del','ha')
    print('域名以及域名信息已全部删除...')


#定义确认用户输入格式是否为ha配置文件所需格式函数
def enter_query(add_contect_str):
    """
    :param add_contect_str: 用户选择修改配置文件后，输入的格式必须为字典
    :return: Flase=用户输入格式不正确  True=用户输入格式正确
    """
    try:    #尝试将用户输入字符串转化为列表，并给变量赋值
        add_contect=json.loads(add_contect_str)
        search_info=add_contect['backend']
        weight=add_contect['record']['weight']
        server=add_contect['record']['server']
        maxconn=add_contect['record']['maxconn']
    except: #如果异常，return 值为False
        return False
    else:   #如果无报错，return 值为False
        return True


#定义主函数
def main():
    while True:
        start_num=input("""1.查询
2.修改
3.删除
q.退出""")
        if start_num.isdigit():
            start_num=int(start_num)
            while True:
                if start_num==1:
                    search_info=input('Please enter the domain name:')
                    result_list=search_backend(search_info)
                    if len(result_list)==0: #如果配置文件中无查询的内容,回显
                        print('\033[31;1mSorry,the configuration file does not have the information you want to query!\033[0m')
                    else:   #如果配置文件中有要查询的内容,打印查询结果
                        for line in result_list:
                            print('\033[31;1m%s\033[0m'%line)
                    break
                elif start_num==2:
                    add_backend()
                    break
                elif start_num==3: #如果选择删除，提示用户输入所需删除的域名
                    del_domain=input('Input the domain want to delete:')
                    result_list=search_backend(del_domain)  #列表赋值于变量
                    if len(result_list)==0:     #如果列表为空，无域名相应信息，提示用户
                        print('\033[31;1mSorry,the configuration file does not have the information you want to delete!\033[0m')
                    else:   #如果有相应信息，执行删除函数
                        del_backend(del_domain)
                    break
                else:   #其他输入，提示用户输入错误，请重新输入
                    print('Information is incorrect, please re-enter...')
                    break
        elif start_num=='q':    #选择退出
            print('Bye!!!!')
            break
        else:   #输入无相应功能，提示重新输入
            print('Information is incorrect, please re-enter...')

#执行主函数
main()
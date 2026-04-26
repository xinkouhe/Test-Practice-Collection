#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
因为routest.py是内存字典，无法reset数据库，所以单接口的工具函数采用了随机账号和隐式写入
"""

import unittest
import requests
import secrets
import string


class TestUserAPI(unittest.TestCase):

    # 每个用例初始化
    def setUp(self) -> None:
        self.BaseUrl = 'http://127.0.0.1:5000'
        self.Headers = {}
        self.Body = {}
        self.AccountSet = {
            "account": "tester_" + ''.join(
                secrets.choice(string.ascii_letters + string.digits + "!@#$%^&*") for _ in range(5)),
            "password": "P_user_" + ''.join(
                secrets.choice(string.ascii_letters + string.digits + "!@#$%^&*") for _ in range(5))
        }

    # 工具函数
    # helper method
    def creat_user(self):
        self.Body.update(self.AccountSet)
        res = requests.post(self.BaseUrl + '/register', json=self.Body)
        return {'id': res.json()['id'], 'Token': res.json()['token']}

    # 单接口测试-正向
    # 注册
    def test_register(self):
        self.Body.update(self.AccountSet)
        res = requests.post(self.BaseUrl + '/register', json=self.Body)

        self.assertEqual(201, res.status_code)
        self.assertIn('id', res.json())
        self.assertIn('token', res.json())

    # 登录
    def test_login(self):
        user_token = self.creat_user()['Token']
        res = requests.post(self.BaseUrl + '/login', json=self.Body)

        self.assertEqual(200, res.status_code)
        self.assertIn('token', res.json())
        self.assertNotEqual(user_token, res.json()['token'])

    # 查询
    def test_get_user(self):
        user = self.creat_user()
        self.Headers['Token'] = user['Token']
        res = requests.get(self.BaseUrl + '/user/' + user['id'], headers=self.Headers)

        self.assertEqual(200, res.status_code)
        self.assertEqual(user['id'], res.json()['id'])
        self.assertEqual(self.Body['account'], res.json()['account'])
        self.assertNotEqual(self.Body['password'], res.json()['password'])

    # 删除
    def test_delete_user(self):
        user = self.creat_user()
        self.Headers['Token'] = user['Token']
        res = requests.delete(self.BaseUrl + '/user/' + user['id'], headers=self.Headers)

        self.assertEqual(200, res.status_code)
        self.assertEqual('application/json', res.headers['Content-Type'])
        self.assertEqual('deleted', res.json()['message'])

    # 退出登录
    def test_logout(self):
        self.Headers['Token'] = self.creat_user()['Token']
        res = requests.post(self.BaseUrl + '/logout', headers=self.Headers)

        self.assertEqual(200, res.status_code)

    # 单接口测试-负向
    # 注册失败-400-重复注册
    def test_register_duplicate_account_400(self):
        self.Body.update(self.AccountSet)
        requests.post(self.BaseUrl + '/register', json=self.Body)
        res = requests.post(self.BaseUrl + '/register', json=self.Body)

        self.assertEqual(400, res.status_code)
        self.assertEqual('application/json', res.headers['Content-Type'])
        self.assertEqual('account exists', res.json()['error'])

    # 注册失败-400-重复注册-字母大写
    @unittest.expectedFailure
    def test_register_upper_account_400(self):
        self.Body.update(self.AccountSet)
        requests.post(self.BaseUrl + '/register', json=self.Body)
        self.Body['account'] = self.Body['account'].upper()
        res = requests.post(self.BaseUrl + '/register', json=self.Body)

        # bug,500,routest.py重复检测大小写不敏感:INTERNAL SERVER ERROR
        self.assertEqual(400, res.status_code)

    # 登录失败-401-输入异常-account为""
    def test_login_invalid_account_401(self):
        self.creat_user()
        self.Body['account'] = ''
        res = requests.post(self.BaseUrl+'/login', json=self.Body)

        self.assertEqual(401, res.status_code)
        self.assertEqual('application/json', res.headers['Content-Type'])
        self.assertEqual("invalid credentials", res.json()['error'])

    # 登录失败-401-输入异常-password为None
    @unittest.expectedFailure
    def test_login_invalid_password_401(self):
        self.creat_user()
        self.Body['password'] = None
        res = requests.post(self.BaseUrl + '/login', json=self.Body)

        # bug,500,routest.py未做参数校验:INTERNAL SERVER ERROR
        self.assertEqual(401, res.status_code)

    # 查询失败-401-权限异常-token无效
    def test_get_user_without_token_401(self):
        user_id = self.creat_user()['id']
        self.Headers['Token'] = 'token'
        res = requests.get(self.BaseUrl + '/user/' + user_id, headers=self.Headers)

        self.assertEqual(401, res.status_code)
        self.assertEqual('application/json', res.headers['Content-Type'])
        self.assertEqual('unauthorized', res.json()['error'])

    # 查询失败-401-权限异常-过期token(spec test)
    @unittest.expectedFailure
    def test_get_user_del_token_401(self):
        user = self.creat_user()
        self.Headers['Token'] = user['Token']
        requests.delete(self.BaseUrl + '/user/' + user['id'], headers=self.Headers)
        res = requests.get(self.BaseUrl + '/user/1', headers=self.Headers)

        # bug,200,routest.py未做token生命周期管理
        self.assertEqual(401, res.status_code)

    # 删除失败-404-资源异常-用户（id）不存在。
    def test_delete_user_invalid_id_404(self):
        user = self.creat_user()
        self.Headers['Token'] = user['Token']
        requests.delete(self.BaseUrl + '/user/' + user['id'], headers=self.Headers)
        res = requests.delete(self.BaseUrl + '/user/' + user['id'], headers=self.Headers)

        self.assertEqual(404, res.status_code)
        self.assertEqual('application/json', res.headers['Content-Type'])
        self.assertEqual('not found', res.json()['error'])

    # 业务流程测试
    # user流程测试：注册-登录-查询-删除
    def test_flow(self):
        self.Body.update(self.AccountSet)
        res = requests.post(self.BaseUrl + '/register', json=self.Body)
        user_id = res.json()['id']
        self.assertEqual(201, res.status_code)

        res = requests.post(self.BaseUrl + '/login', json=self.Body)
        self.Headers['Token'] = res.json()['token']
        self.assertEqual(200, res.status_code)

        res = requests.get(self.BaseUrl + '/user/' + user_id, headers=self.Headers)
        self.assertEqual(200, res.status_code)

        res = requests.delete(self.BaseUrl + '/user/' + user_id, headers=self.Headers)
        self.assertEqual(200, res.status_code)


if __name__ == '__main__':
    unittest.main()

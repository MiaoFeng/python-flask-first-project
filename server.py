from flask import Flask, request, jsonify
from flask_cors import CORS
import requests, re, ast, json
# Data analysis tool
import numpy as np
# Data source
import akshare as ak

app = Flask(__name__)
CORS(app)

user_agent = 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.36'

# /api/rankhandler
@app.route('/api/rankhandler', methods=['GET'])
def getrank():
    header = {
        'Referer': 'https://fund.eastmoney.com/data/fundranking.html',
        'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/125.0.0.0 Safari/537.36'
    }
    all_param = {
    'op': 'ph',
    'dt': 'kf',
    'ft': 'all', #全部，也可以是gp(股票型)，hh(混合型)等
    'rs': '', #更多筛选里面的条件
    'gs': 0,
    'sc': 'rzdf', #排名阶段，可以是rzdf(日增长率)，zzf(近1周)等
    'st': 'desc', #排序方式
    'sd': '2021-11-16', #这两个时间用于获取自定义时间段的增长率数据
    'ed': '2021-11-16',
    'qdii': '',
    'tabSubtype': ',,,,,',
    'pi': 1, #页码
    'pn': 50, #每页显示数据条数
    'dx': 1,
    'v': 0.12296642077721809
    }

    url = 'http://fund.eastmoney.com/data/rankhandler.aspx'

    try:
        resp = requests.get(url, headers=header, params=all_param)
        rankData = resp.text
        # all = re.findall(r'var rankData = (.*?);', rankData)[0]
        data_str = re.findall('datas:(.*?),allRecords', rankData)[0]
        content = ast.literal_eval(data_str)
    except Exception as e:
        print(e)
        return jsonify({'code': 500, 'data':[], 'message': 'Get Data Error'})

    # print(rankData)
    list = [[]]
    list.clear()

    # handle data
    columnsMap = ("fundCode",
    "fundName",
    "fundId",
    "publishDate",
    "unitNv",
    "accumNv",
    "accumNvGrowthRate",
    "week1GrowthRate",
    "month1GrowthRate",
    "month3GrowthRate",
    "month6GrowthRate",
    "year1GrowthRate",
    "year2GrowthRate",
    "year3GrowthRate",
    "yearSinceGrowthRate",
    "establishGrowthRate")

    for item in content:
        item = item.replace('"', '')
        row = item.split(',')[0:16]
        rowDict = {}
        index = 0
        while index < len(row):
            rowDict[columnsMap[index]] = row[index]
            index += 1
        list.append(rowDict)

    return jsonify({'code': 200,'data': list})

# /api/getAllFund
@app.route('/api/getAllFund', methods=['GET'])
def getAllFund():
    url = 'http://fund.eastmoney.com/js/fundcode_search.js'
    headers = {
        'User-Agent': user_agent
    }
    try:
        res = requests.get(url, headers=headers)
        # res.encoding = 'utf-8'
        content = ast.literal_eval(re.findall(r'\[.*\]', res.text)[0])
    except Exception as e:
        print(e)
        return jsonify({'code': 500, 'data':[], 'message': 'Get Data Error'})

    list = [[]]
    list.clear()

    columnsMap = ["fundCode", "fundShortName", "fundName", "fundType", "fullName"]
    length = 0
    for item in content:
        if length == 50:
            break
        rowDict = {}
        index = 0
        while index < len(item):
            rowDict[columnsMap[index]] = item[index]
            index += 1
        rowDict["id"] = item[0]
        list.append(rowDict)
        length += 1

    return jsonify({'data': list})

# /api/getAllFundCompany
@app.route('/api/getAllFundCompany', methods=['GET'])
def getAllFundCompany():
    '''
    Get fundName and fundcode of all fund companies, url: http://fund.eastmoney.com/js/jjjz_gs.js
    :return: name and code of all fund companies
    '''
    url = 'http://fund.eastmoney.com/js/jjjz_gs.js'
    headers = {
        'User-Agent': user_agent
    }
    try:
        res = requests.get(url, headers=headers)
        res.encoding = 'utf-8'
        content = ast.literal_eval(re.findall(r'\[.*\]', res.text)[0])
    except Exception as e:
        print(e)
        return jsonify({'code': 500, 'data':[], 'message': 'Get Data Error'})
    
    list = [[]]
    list.clear()

    # handle return data
    columnsMap = ["fundCode", "fundName"]
    length = 0
    for item in content:
        if length == 500:
            break
        rowDict = {}
        index = 0
        while index < len(item):
            rowDict[columnsMap[index]] = item[index]
            index += 1
        rowDict["id"] = item[0]
        list.append(rowDict)
        length += 1

    return jsonify({'code': 200, 'data': list})

# /api/getRealTimeFundInfo
@app.route('/api/getRealTimeFundInfo/<fundCode>', methods=['GET'])
def getRealTimeFundInfo(fundCode):
    '''
    Get fund information in last 24 hours, url: http://fundgz.1234567.com.cn/js/<fundCode>.js
    :return: real time fund information
    '''
    if fundCode == None or fundCode == '':
        return jsonify({'code': 400,'data': [],'msg': 'fundCode is required'})

    url = 'http://fundgz.1234567.com.cn/js/%s.js'%fundCode
    headers = {
        'User-Agent': user_agent
    }
    try:
        res = requests.get(url, headers=headers)
        res.encoding = 'utf-8'
        content = json.loads(re.findall(r'jsonpgz\((.*)\)', res.text)[0])
    except Exception as e:
        print(e)
        return jsonify({'code': 500, 'data':[], 'message': 'Get Data Error'})

    return jsonify({'code': 200,'data': content})

# /api/getFundHistoryInfo
@app.route('/api/getFundHistoryInfo', methods=['GET'])
def getFundHistoryInfo():
    symbol = request.args.get('fundCode')
    indicator = request.args.get('indicator')
    period = request.args.get('period') or '1月'

    if symbol == None or symbol == '':
        return jsonify({'code': 400,'data': [],'msg': 'fundCode is required'})
    if indicator == None or indicator == '':
        return jsonify({'code': 400,'data': [],'msg': 'indicator is required'})
    
    # 单位净值走势,累计净值走势,累计收益率走势,同类排名走势,同类排名百分比,分红送配详情,拆分详情
    # '''
    # Get fund history information of last x working days, url: http://fund.eastmoney.com/f10/F10DataApi.aspx?type=lsjz&code=00001&page=1&sdate=2024-05-06&edate=2024-06-06&per=20
    # :return: fund history information of last x working days
    # '''
    # url = 'http://fund.eastmoney.com/f10/F10DataApi.aspx?type=lsjz&code={}&page={}&sdate={}&edate={}&per={}'.format(
    #     fundCode, page, startDate, endDate, per
    # )
    #{"1月", "3月", "6月", "1年", "3年", "5年", "今年来", "成立来"}
    try:
        fund_data = ak.fund_open_fund_info_em(symbol, indicator, period)
    except Exception as e:
        print(e)
        return jsonify({'code': 500, 'data':[], 'message': 'Get Data Error'})

    fund_data_list = np.array(fund_data).tolist()

    return jsonify({'code': 200,'data': fund_data_list})

# /api/getFundHoldStructure
@app.route('/api/getFundHoldStructure', methods=['GET'])
def getFundHoldStructure():

    try:
        data = ak.fund_hold_structure_em()
        content = np.array(data).tolist()
    except Exception as e:
        print(e)
        return jsonify({'code': 500, 'data':[], 'message': 'Get Data Error'})
    
    # hanlde return data
    list = [[]]
    list.clear()
    chartDataOrgi = [[]]
    chartDataOrgi.clear()
    chartDataPrivate = [[]]
    chartDataPrivate.clear()
    chartDataInternal = [[]]
    chartDataInternal.clear()
    chartDate = [[]]
    chartDate.clear()

    columnsMap = ["id","date", "amount" ,"organization", "private","internal","capital"]

    for item in content:
        date = "{:%Y-%m-%d}".format(item[1])
        chartDataOrgi.append(item[3])
        chartDataPrivate.append(item[4])
        chartDataInternal.append(item[5])
        chartDate.append(date)
        rowDict = {}
        index = 0
        while index < len(columnsMap):
            if index == 1:
                rowDict[columnsMap[index]] = date
            else: rowDict[columnsMap[index]] = item[index]
            index += 1
        list.append(rowDict)

    return jsonify({'code': 200,'data': {'table': list, 'chartDataOrgi': chartDataOrgi, 'chartDataPrivate':chartDataPrivate, 'chartDataInternal':chartDataInternal, 'chartDate':chartDate}})

# error handler - 500
# @app.errorhandler(500)
def internal_server_error(error):
    return jsonify({'code': 500,'data': [],'msg': 'Internal Server Error'})

#dev runtime
# if __name__ == '__main__':
#     app.run(debug=True, port=8080)

# SCF runtime
if __name__ == '__main__':
    app.run(host='0.0.0.0', port=9000)
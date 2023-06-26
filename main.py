from web3 import Web3
import json


# 读取 JSON 文件
def read_json_file(file_path):
    with open(file_path, 'r') as file:
        data = file.read()
        return data

def reqContract(w3, contractAddress, abi, func):

    # 根据contractName获取合约地址
    contract = w3.eth.contract(address=contractAddress, abi=abi)

    try:
        if "," in func:
            args = func.split(",")[1].split("|")
            for i in range(len(args)):
                if "$" in args[i]:
                    args[i] = globals()[args[i].replace("$", "")]
                elif args[i].isdigit():
                    args[i] = int(args[i])
            res = contract.functions[func.split(",")[0]](*args).call()
        else:
            res = contract.functions[func]().call()
    except Exception as e:
        res = str(e)

    return res

def check(w3, config, reqResult, exp, contractName, func):

    if type(reqResult) == bytes:
        reqResult = w3.to_hex(reqResult)
    if isinstance(reqResult, list) and all(isinstance(item, bytes) for item in reqResult):
        reqResult = [w3.to_hex(item) for item in reqResult]
    if "length" in str(exp):
        if len(reqResult) == int(exp.split("|")[1]):
            print(f"\033[42m合约 {contractName} 执行 {func} 成功，实际结果为：{reqResult} \033[0m")
        else:
            print(f"\033[41m合约 {contractName} 执行 {func} 失败，实际结果为：{reqResult} \033[0m")
            print(f"\033[32m期望结果为: {exp} \033[0m")
    else:
        if type(exp) == str and "." in exp:
            es = exp.split(".")

            expres = config
            for e in es:
                expres = expres[e]
        else:     
            expres = exp

        if expres == reqResult:
            print(f"\033[42m合约 {contractName} 执行 {func} 成功，实际结果为：{reqResult} \033[0m")
        else:
            print(f"\033[41m合约 {contractName} 执行 {func} 失败，实际结果为：{reqResult} \033[0m")
            print(f"\033[32m期望结果为: {expres} \033[0m")

def getAbi(path):
        path = "abi/contracts/" + path
        abi = json.loads(read_json_file(path))
        if "out" in path:
            abi = abi["abi"]
        return abi

if __name__ == "__main__":
    # JSON 文件路径
    json_file_path = './config.json'
    # 读取 JSON 文件
    json_data = read_json_file(json_file_path)
    # 解析 JSON 数据
    config = json.loads(json_data)

    # 设置全局变量
    for cName, cAddress in config["contractAddress"].items():
        globals()[cName] = cAddress

    for m in config["contractMsgs"]:
        print(f'============================start check {m["name"]}=================================')
        contractAddress = config["contractAddress"][m["name"]]

        rpc = config["l1rpc"]
        if m["type"] == "l2":
            rpc = config["l2rpc"]
        w3 = Web3(Web3.HTTPProvider(rpc))

        # 读取abi
        abi = getAbi(m["path"])

        for f, e in m["expects"].items():
            res = reqContract(w3, contractAddress, abi, f)
            check(w3, config, res, e, m["name"], f)

        print(f'============================finish check {m["name"]}=================================\n\n')
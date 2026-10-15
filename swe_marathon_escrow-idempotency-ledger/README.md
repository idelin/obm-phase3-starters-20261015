# 运行入口

使用Python3.13.12；观察对象为同版本的CPython字节码，Linux环境须提供相同版本。候选运行：`python3.13 sources/public/main.py /tmp/candidate-state < sources/public/examples.jsonl`。观察运行：`python3.13 sources/observe/main.pyc /tmp/observe-state < sources/public/examples.jsonl`。状态目录须分开。

`public/`为可修改的候选代码及普通输入示例。`observe/`是仅可调用的行为观察对象，禁止读取字节码内容、反编译或将其复制、导入成品；正式验收环境只复制候选代码，不提供observe目录。完整公开接口、返回字段与资源范围见proposal.json的C_agent_task。

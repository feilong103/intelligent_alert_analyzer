from langchain_community.chat_models import ChatTongyi
from langchain_core.output_parsers import StrOutputParser
from langchain_core.prompts import PromptTemplate

import config.settings as config


class DataCleanerService(object):

    def __init__(self):
        # 针对 RAG 语义分块专门设计的结构化提示词
        prompt_text = """你是一名资深 SRE / DevOps 运维专家，同时也是 AIOps 知识库构建工程师。

        你的任务是：
        对输入的监控、运维、故障排查类文档进行 **数据清洗 + 语义知识片段拆分**，
        以便将这些内容存入 RAG 向量数据库，用于未来的监控告警分析和自动故障诊断。

        ====================
        【知识拆分原则】
        ====================

        1. 语义独立
        每个输出片段必须是一个 **完整且独立的知识单元**，
        单独阅读也能理解其含义，不依赖上下文。

        2. 领域语义优先
        运维知识优先按以下语义结构拆分：

        - 故障现象
        - 指标说明
        - 可能原因
        - 排查步骤
        - 修复方案
        - 运维命令
        - 配置说明

        不要把多个不同主题混在同一个片段中。

        3. 标题上下文补全
        如果原文是层级结构：

        示例：
        Kubernetes
          Pod异常
            CrashLoopBackOff

        拆分后必须补全上下文，例如：

        【Kubernetes Pod CrashLoopBackOff 排查】

        而不是只写：

        CrashLoopBackOff 排查

        4. 命令完整保留
        所有命令、脚本、配置必须保持完整，不允许拆开，例如：

        kubectl get pods -A
        top
        ps aux --sort=-%cpu | head

        命令必须与对应说明放在同一个知识片段中。

        5. 片段粒度控制
        每个知识片段推荐长度：

        100 ~ 350 中文字符

        如果步骤是连续排查流程，必须保持完整，不要拆断。

        6. 数据清洗
        删除以下无意义内容：

        - 页眉页脚
        - 作者信息
        - 版权声明
        - 目录
        - 广告
        - 无意义空行
        - OCR乱码

        7. 表格 / 列表处理
        将零散列表或表格转换为自然语言描述，
        但必须保持原有技术含义。

        ====================
        【输出格式要求】
        ====================

        - 严格使用

        ----------

        （10个连字符）

        作为每个知识片段之间的唯一分隔符。

        - 不要输出解释文字
        - 不要输出额外说明
        - 只输出知识片段

        每个片段建议结构：

        【知识标题】

        知识内容

        ====================
        【示例】

        输入：

        Linux CPU 使用率过高

        CPU 使用率高通常说明系统正在执行大量计算任务。

        可能原因：
        1. 某个进程占用CPU
        2. 高并发请求
        3. 程序死循环

        排查：

        top
        ps aux --sort=-%cpu | head

        输出：

        【Linux CPU 使用率过高可能原因】

        CPU 使用率过高通常说明系统正在执行大量计算任务，常见原因包括：某个进程异常占用 CPU、高并发请求导致计算压力增大，或者程序出现死循环。

        ----------

        【Linux CPU 使用率过高排查步骤】

        可以使用以下命令定位高 CPU 进程：

        top  
        ps aux --sort=-%cpu | head

        ====================

        请处理以下原始文本：

        {raw_text}
        """

        self.prompt_template = PromptTemplate.from_template(prompt_text)

        # 建议适当调低 temperature 以保证模型输出格式的稳定性，减少幻觉
        self.chat_model = ChatTongyi(model=config.chat_model, temperature=0.1)

        self.chain = self.__get_chain()

    def __get_chain(self):
        def print_prompt(prompt):
            print("=" * 50 + " 正在发送给 LLM 的 Prompt " + "=" * 50)
            print(prompt.to_string())
            print("=" * 126)
            return prompt

        chain = self.prompt_template | print_prompt | self.chat_model | StrOutputParser()
        return chain


if __name__ == "__main__":

    # 模拟真实运维知识库
    data = """
    第3章 Kubernetes 运行故障排查

3.1 Pod 状态异常

在 Kubernetes 集群运行过程中，Pod 可能会进入异常状态，例如：
CrashLoopBackOff、ImagePullBackOff、Pending 等。

CrashLoopBackOff 通常表示容器启动失败并不断重启。

常见原因：

1. 应用程序启动失败
2. 配置文件错误
3. 依赖服务未启动
4. 环境变量配置错误
5. 端口被占用

排查步骤：

首先查看 Pod 状态：

kubectl get pods -n default

查看 Pod 详细信息：

kubectl describe pod <pod-name> -n default

查看容器日志：

kubectl logs <pod-name> -n default

如果容器持续重启，可以查看上一轮日志：

kubectl logs <pod-name> -p


-----------------------------------

3.2 Pod 一直处于 Pending

当 Pod 长时间处于 Pending 状态，通常表示调度失败。

常见原因：

1. 节点资源不足（CPU / Memory）
2. 节点标签不匹配
3. Taints/Tolerations 不匹配
4. PVC 未绑定

排查方法：

查看调度事件：

kubectl describe pod <pod-name>

查看节点资源情况：

kubectl top nodes

-----------------------------------

第4章 Linux 服务器监控指标

4.1 CPU 使用率

CPU 使用率是衡量服务器负载的重要指标。

当 CPU 使用率长期超过 80% 时，通常表示系统负载较高。

可能原因：

• 某个进程异常占用 CPU
• 大量并发请求
• 程序死循环
• 频繁 GC

排查步骤：

查看 CPU 使用率：

top

按 CPU 排序查看进程：

ps aux --sort=-%cpu | head

查看系统负载：

uptime

-----------------------------------

4.2 Load Average

Load Average 表示系统平均负载。

Load Average 包含三个值：

1分钟
5分钟
15分钟

经验规则：

Load < CPU 核数    → 系统正常  
Load ≈ CPU 核数    → 系统繁忙  
Load > CPU 核数    → 系统可能过载

-----------------------------------

第5章 MySQL 性能问题

5.1 MySQL 连接数过高

当 MySQL 连接数接近 max_connections 时，
新的客户端连接可能会失败。

常见报错：

Too many connections

可能原因：

1. 应用连接未释放
2. 突发流量
3. 连接池配置过小
4. 慢 SQL 堆积

排查方法：

查看当前连接数：

SHOW STATUS LIKE 'Threads_connected';

查看最大连接数：

SHOW VARIABLES LIKE 'max_connections';

查看当前运行 SQL：

SHOW FULL PROCESSLIST;

-----------------------------------

Prometheus 监控指标说明

node_cpu_seconds_total

该指标表示 CPU 时间统计，
通常用于计算 CPU 使用率。

常见 PromQL：

rate(node_cpu_seconds_total[5m])

node_memory_MemAvailable_bytes

表示当前可用内存。

计算内存使用率：

(1 - node_memory_MemAvailable_bytes / node_memory_MemTotal_bytes) * 100
    """

    data_cleaner_service = DataCleanerService()

    # 注意这里传入的变量名改为了 raw_text
    result_str = data_cleaner_service.chain.invoke({"raw_text": data})


    print("\n" + "=" * 50 + " LLM 返回的清洗结果 " + "=" * 50)
    print(result_str)

    print("\n" + "=" * 50 + " 解析为列表格式 " + "=" * 50)
    # 按分隔符切分并去除首尾空白
    chunks = [chunk.strip() for chunk in result_str.split("----------") if chunk.strip()]
    for i, chunk in enumerate(chunks):
        print(f"片段 {i + 1}:\n{chunk}\n")
# RAG 告警智能分析系统 API 文档

## 1. 系统简介

RAG 告警智能分析系统是一个基于检索增强生成（RAG）技术的智能告警分析平台，主要功能包括：

- **基于 RAG 的告警分析系统**：结合知识库检索和大型语言模型进行智能分析
- **接收监控告警 JSON**：支持标准的监控告警数据格式
- **调用知识库和 LLM 进行智能分析**：自动检索相关知识库内容，结合 LLM 进行深度分析
- **返回故障原因和排查建议**：提供详细的故障分析结果和解决方案

系统采用 FastAPI 框架构建，支持同步和流式两种响应模式。

## 2. API 概览

| 接口 | 方法 | 描述 |
|-----|-----|-----|
| /analyze-alert | POST | 同步告警分析接口 |
| /analyze-alert-stream | POST | 流式告警分析接口 |
| /kb/upload/prepare | POST | 知识库上传准备（解析+LLM分块） |
| /kb/upload/confirm | POST | 知识库上传确认（写入KB） |

## 3. 同步告警分析接口

### 接口地址
POST /analyze-alert

### 请求格式
Content-Type: application/json

### 请求参数

接口接受任意 JSON 格式的告警数据，系统会自动将请求体转换为字符串进行处理。

### 请求示例

```json
{
  "eve_detail": "HFISH(袭鑫宇)-VPHFISHAP03 Linux: HFISH(袭鑫宇)-VPHFISHAP03 Load average is too high 0.24",
  "eve_host": "HFISH(袭鑫宇)-VPHFISHAP03",
  "eve_ip": "11.24.200.52",
  "eve_labels": {
    "category": "S03",
    "class": "os",
    "component": "cpu",
    "scope": "performance",
    "sub_category": "OTHER",
    "target": "linux"
  },
  "eve_level": "5",
  "eve_metric": "Linux: {HOST.NAME} Load average is too high",
  "eve_metric_value": "0.24",
  "eve_source": "Zabbix",
  "eve_status": "RESOLVED",
  "eve_summary": "【Zabbix6.0】VPHFISHAP03 Linux: HFISH(袭鑫宇)-VPHFISHAP03 Load average is too high 0.24",
  "eve_time_create": "2026.03.06 04:37:04",
  "eve_time_resovled": "2026.03.06 04:37:04",
  "eve_uid": "VPHFISHAP03-211596",
  "tenant_id": "0004",
  "token": "AAbfi3HqJqquJW9bYGQ2n",
  "url": "https://oncall.rynnova.com/api/webhook:trigger/xqevwukg0wz"
}
```

### 返回格式

系统返回 JSON 格式的分析结果，可能包含以下结构：

- **字典格式**：如果 RAG 服务返回字典对象，直接返回
- **JSON 字符串**：如果返回 JSON 字符串，自动解析后返回
- **文本格式**：其他情况返回文本结果

### 返回示例

```json
{
  "result": "{\"analysis\": \"系统负载过高分析\", \"cause\": \"CPU使用率异常\", \"suggestion\": \"检查系统进程和资源使用情况\"}"
}
```

或

```json
{
  "analysis": "系统负载过高分析",
  "cause": "CPU使用率异常",
  "suggestion": "检查系统进程和资源使用情况",
  "confidence": 0.85
}
```

### CURL 调用示例

```bash
curl -X POST "http://localhost:8000/analyze-alert" \
  -H "Content-Type: application/json" \
  -d '{
    "eve_detail": "HFISH(袭鑫宇)-VPHFISHAP03 Linux: HFISH(袭鑫宇)-VPHFISHAP03 Load average is too high 0.24",
    "eve_host": "HFISH(袭鑫宇)-VPHFISHAP03",
    "eve_ip": "11.24.200.52",
    "eve_level": "5",
    "eve_source": "Zabbix",
    "eve_status": "RESOLVED"
  }'
```

### JavaScript 调用示例

```javascript
async function analyzeAlert(alertData) {
  try {
    const response = await fetch('http://localhost:8000/analyze-alert', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify(alertData)
    });
    
    if (!response.ok) {
      throw new Error(`HTTP error! status: ${response.status}`);
    }
    
    const result = await response.json();
    return result;
  } catch (error) {
    console.error('Error analyzing alert:', error);
    throw error;
  }
}

// 使用示例
const alertData = {
  eve_detail: "HFISH(袭鑫宇)-VPHFISHAP03 Linux: HFISH(袭鑫宇)-VPHFISHAP03 Load average is too high 0.24",
  eve_host: "HFISH(袭鑫宇)-VPHFISHAP03",
  eve_ip: "11.24.200.52",
  eve_level: "5",
  eve_source: "Zabbix",
  eve_status: "RESOLVED"
};

analyzeAlert(alertData).then(result => {
  console.log('Analysis result:', result);
});
```

---

## 4. 流式告警分析接口

### 接口地址
POST /analyze-alert-stream

### 说明

该接口返回 LLM 流式分析结果，适用于需要实时显示分析进度的场景。响应内容以文本流形式返回。

### 请求格式
Content-Type: application/json

### 请求参数

与同步接口相同，接受任意 JSON 格式的告警数据。

### CURL 流式调用示例

```bash
curl -X POST "http://localhost:8000/analyze-alert-stream" \
  -H "Content-Type: application/json" \
  -d '{
    "eve_detail": "HFISH(袭鑫宇)-VPHFISHAP03 Linux: HFISH(袭鑫宇)-VPHFISHAP03 Load average is too high 0.24",
    "eve_host": "HFISH(袭鑫宇)-VPHFISHAP03",
    "eve_ip": "11.24.200.52"
  }' \
  --no-buffer
```

### JavaScript Stream 调用示例

```html
<!DOCTYPE html>
<html>

<head>
    <meta charset="UTF-8">
    <title>RAG Stream Demo</title>
</head>

<body>

    <h2>告警分析流式输出</h2>

    <button onclick="sendRequest()">开始分析</button>

    <pre id="output"></pre>

    <script>

        async function sendRequest() {

            const output = document.getElementById("output")
            output.textContent = ""

            const response = await fetch("http://localhost:8000/analyze-alert-stream", {
                method: "POST",
                headers: {
                    "Content-Type": "application/json"
                },
                body: JSON.stringify({
                    alert_name: "cpu_high",
                    node: "node01",
                    value: "95%",
                    severity: "critical"
                })
            })

            const reader = response.body.getReader()
            const decoder = new TextDecoder("utf-8")

            while (true) {

                const { done, value } = await reader.read()

                if (done) break

                const chunk = decoder.decode(value)

                output.textContent += chunk

            }
        }

    </script>

</body>

</html>
```

---

## 5. 知识库上传接口

### 5.1 准备接口

#### 接口地址
POST /kb/upload/prepare

#### 请求格式
Content-Type: multipart/form-data

#### 请求参数

| 参数 | 类型 | 必填 | 说明 |
|------|------|------|------|
| file | UploadFile | 是 | 知识库文件（支持 txt/pdf/docx/xlsx/csv/html/vtt 等） |

#### 返回示例

```json
{
  "filename": "demo.pdf",
  "llm_result": "...省略...",
  "chunks": [
    "【知识标题】\n\n内容...",
    "【知识标题】\n\n内容..."
  ],
  "chunk_count": 2
}
```

#### CURL 调用示例

```bash
curl -X POST "http://localhost:8000/kb/upload/prepare" \
  -F "file=@/path/to/demo.pdf"
```

### 5.2 确认接口

#### 接口地址
POST /kb/upload/confirm

#### 请求格式
Content-Type: application/json

#### 请求参数

| 参数 | 类型 | 必填 | 说明 |
|------|------|------|------|
| filename | string | 是 | 原始文件名 |
| chunks | string[] | 是 | 用户最终确认后的知识片段数组 |

#### 请求示例

```json
{
  "filename": "demo.pdf",
  "chunks": [
    "【知识标题】\n\n内容...",
    "【知识标题】\n\n内容..."
  ]
}
```

#### 返回示例

```json
{
  "result": "[成功]知识库更新完成，共写入 2 个知识片段"
}
```

#### CURL 调用示例

```bash
curl -X POST "http://localhost:8000/kb/upload/confirm" \
  -H "Content-Type: application/json" \
  -d '{
    "filename": "demo.pdf",
    "chunks": [
      "【知识标题】\n\n内容...",
      "【知识标题】\n\n内容..."
    ]
  }'
```

---

## 6. 错误处理

系统使用标准的 HTTP 状态码进行错误处理：

| 状态码 | 说明 | 可能原因 |
|------|------|---------|
| 400 | 请求参数错误 | 请求体格式不正确或缺少必要参数 |
| 500 | 服务内部错误 | RAG 服务异常、模型调用失败等 |

### 错误响应示例

```json
{
  "detail": "RAG service initialization failed"
}
```

或

```json
{
  "detail": "Missing alert field in request body"
}
```

---

## 7. 系统配置

### 服务启动

```bash
cd /Users/feilong/Documents/coding/intelligent_alert_analyzer
uvicorn apps.app:app --host 0.0.0.0 --port 8000
```

### 默认端口
- **开发环境**: 8000
- **访问地址**: http://localhost:8000

### CORS 配置
系统已配置跨域支持，允许所有来源访问（生产环境建议配置具体域名）。

---

## 8. 技术架构

### 核心组件
- **FastAPI**: Web 框架
- **LangChain**: RAG 框架
- **ChromaDB**: 向量数据库
- **DashScope**: 阿里云通义千问模型

### 处理流程
1. 接收告警 JSON 数据
2. 向量化检索相关知识库内容
3. 构建包含上下文和告警信息的提示词
4. 调用 LLM 进行智能分析
5. 返回格式化分析结果

---

## 9. 使用建议

1. **数据格式**: 建议使用结构化的告警数据格式
2. **流式接口**: 对于长文本分析，建议使用流式接口获得更好的用户体验
3. **错误处理**: 客户端应妥善处理 500 错误，建议添加重试机制
4. **性能优化**: 系统已实现全局 RAG 服务初始化，避免重复加载模型

---

*文档最后更新: 2026-03-12*
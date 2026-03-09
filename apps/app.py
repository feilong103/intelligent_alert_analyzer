from fastapi import FastAPI, HTTPException, Request
from src.rag import RagService

app = FastAPI()

# 全局初始化（避免每次请求都加载模型）
rag_service = RagService()


@app.post("/analyze-alert")
async def analyze_alert(request: Request):
    try:
        # 获取 JSON 请求体
        body = await request.json()

        # 转换为 str
        alert = str(body)

        # 调用 RAG chain
        result = rag_service.chain.invoke(alert)

        # 如果返回的是 dict 直接返回
        if isinstance(result, dict):
            return result

        # 如果是字符串（LLM返回JSON字符串）
        if isinstance(result, str):
            import json
            try:
                return json.loads(result)
            except Exception:
                return {"result": result}

        # 兜底
        return {"result": str(result)}

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


import asyncio
import json


from fastapi import FastAPI, HTTPException, Request, File, UploadFile
from fastapi.responses import StreamingResponse
from fastapi.middleware.cors import CORSMiddleware
from src.rag import RagService
from src.knowledge_base import KnowledgeBaseService
from utils.data_cleaner import DataCleanerService
from utils.file_parser import parse_file_to_text

app = FastAPI()

# ⭐ 解决跨域
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],   # 生产环境建议写具体域名
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# 全局初始化（避免每次请求都加载模型）
rag_service = RagService()
kb_service = KnowledgeBaseService()
data_cleaner_service = DataCleanerService()


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


@app.post("/analyze-alert-stream")
async def analyze_alert_stream(request: Request):
    """
    流式返回接口
    """
    try:
        body = await request.json()
        alert = str(body)

        async def event_generator():

            try:
                # LangChain stream
                for chunk in rag_service.chain.stream(alert):

                    if isinstance(chunk, dict):
                        yield json.dumps(chunk, ensure_ascii=False)

                    else:
                        yield str(chunk)

                    await asyncio.sleep(0.01)

            except Exception as e:
                yield f"\n[ERROR]{str(e)}"

        return StreamingResponse(
            event_generator(),
            media_type="text/plain"
        )

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/kb/upload/prepare")
async def prepare_kb_upload(file: UploadFile = File(...)):
    try:
        file_bytes = await file.read()
        text = parse_file_to_text(file_bytes, file.filename)
        llm_result = data_cleaner_service.chain.invoke({"raw_text": text})
        chunks = [
            chunk.strip()
            for chunk in llm_result.split("----------")
            if chunk.strip()
        ]
        return {
            "filename": file.filename,
            "llm_result": llm_result,
            "chunks": chunks,
            "chunk_count": len(chunks)
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/kb/upload/confirm")
async def confirm_kb_upload(request: Request):
    try:
        body = await request.json()
        filename = body.get("filename")
        chunks = body.get("chunks")

        if not filename or chunks is None:
            raise HTTPException(status_code=400, detail="Missing filename or chunks")

        result = kb_service.upload_by_chunks(chunks, filename)
        return {"result": result}
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
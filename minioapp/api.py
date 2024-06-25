from fastapi.responses import JSONResponse
from fastapi import APIRouter, Depends, HTTPException, UploadFile, File
from auth.auth import get_current_bot
from minioapp.minio_class import MinioClass
from db import get_database

app = APIRouter()


def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() == 'zip'


@app.post("/upload_userdata/")
async def upload_zip_file(current_user: dict = Depends(get_current_bot), file: UploadFile = File(...)):
    
    if not allowed_file(file.filename):
        raise HTTPException(status_code=400, detail="Only zip files are allowed.")
    db = await get_database()
    minio_obj=MinioClass()
    try:
        file_url = await minio_obj.upload_file(file)
        user_data =  await db.user_data.insert_one({'status': 0,'path': file_url})
        if not user_data.acknowledged:
            JSONResponse(content="cannot create userdata", status_code=500)        
        return {"message": f"File '{file.filename}' uploaded successfully."}
    except Exception as err:
        JSONResponse(content={"error": str(err)}, status_code=500)

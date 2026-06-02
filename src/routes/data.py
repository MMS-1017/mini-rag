from fastapi import FastAPI, APIRouter, Depends, UploadFile, status, Request
from fastapi.responses import JSONResponse
from helpers.config import get_settings, Settings
from controllers import DataController, ProjectController, ProcessController
from models import ResponseSignal
import aiofiles
import logging
from .schemas.data import ProcessRequest
from models.ProjectModel import ProjectModel
from models.ChunkModel import ChunkModel
from models.AssetModel import AssetModel
from models.db_schemas import DataChunk, Asset
from models.enums.AssetFileEnum import AssetTypeEnum
import os

logger = logging.getLogger('uvicorn.error')

data_router = APIRouter(
    prefix="/api/v1/data",
    tags=["api_v1", "data"],
)

@data_router.post("/upload/{project_id}")
async def upload_data(request: Request, project_id: str, file: UploadFile,
                      app_settings: Settings = Depends(get_settings)):
    
    project_model = await ProjectModel.create_instance(
        db_client=request.app.db_client
        )
    project = await project_model.get_project_or_create_one(project_id=project_id)

    # validate the file properties
    data_controller = DataController()

    is_valid, signal = data_controller.validate_uploaded_file(file=file)
    if not is_valid:
        return JSONResponse(status_code=status.HTTP_400_BAD_REQUEST, 
                            content={"signal": signal})
    
    project_dir_path = ProjectController().get_project_path(project_id=project_id)
    file_path, file_id = data_controller.generate_unique_filepath(
        orig_filename=file.filename, 
        project_id=project_id
    )
    try: # system could fail due to a huge file size, a full disk, file removed, permission problems, or connection failed
    
        async with aiofiles.open(file_path, 'wb') as f: # do not stop the event loop during writing, wb because files such as PDFs, images, and videos are handled as bytes not text
            while chunk := await file.read(app_settings.FILE_DEFAULT_CHUNK_SIZE): # read the file chunk by chunk not all at once, because if the file is too large, it will be saved all in the RAM which may cause huge memory consumption, server slowness, or a crash. := (walrus operator) reads the chunk and saves it in the variable 'chunk'
                await f.write(chunk)
    
    except Exception as e:

        logger.error(f"Error while uploading file: {str(e)}")
        
        return JSONResponse(
            status_code=status.HTTP_400_BAD_REQUEST, 
            content={"signal": ResponseSignal.FILE_UPLOAD_FAILED.value, 
            "error": str(e)}
            )
    
    # store the file as an asset into the database
    asset_model = await AssetModel.create_instance(
        db_client=request.app.db_client
    )
    asset_resource = Asset(
        asset_project_id = project.id,
        asset_type = AssetTypeEnum.FILE.value,
        asset_name = file_id, 
        asset_size = os.path.getsize(file_path),
    )

    asset_record = await asset_model.create_asset(asset=asset_resource)


    return JSONResponse(
        content={
            "signal": ResponseSignal.FILE_UPLOAD_SUCCESS.value,
            "file_id": str(asset_record.id)
            }
        )

@data_router.post("/process/{project_id}")
async def process_endpoint(request: Request, project_id: str, process_request: ProcessRequest):
    
    chunk_size = process_request.chunk_size
    overlap = process_request.overlap
    do_reset = process_request.do_reset

    project_model = await ProjectModel.create_instance(
        db_client=request.app.db_client
    )
    
    project = await project_model.get_project_or_create_one(
        project_id=project_id
    )
    
    asset_model = await AssetModel.create_instance(
            db_client=request.app.db_client
    )

    project_file_ids = {} # to have the mapping of _id : file_id(I used to search with)

    if process_request.file_id: # Case1: user is specifying one file
        asset_record = await asset_model.get_asset_record(
            asset_project_id=project.id,
            asset_name=process_request.file_id
        )

        if asset_record is None: # if it does not exist, raise error
            return JSONResponse(
                status_code=status.HTTP_400_BAD_REQUEST,
                content={
                    "signal": ResponseSignal.FILE_ID_ERROR.value,
                }
            )

        project_files_ids = {
            asset_record.id: asset_record.asset_name
        }
    
    else: # Case2: if the user is not specific, process all projects' files

        project_files = await asset_model.get_all_project_assets(
            asset_project_id=project.id,
            asset_type=AssetTypeEnum.FILE.value,
        )

        project_files_ids = {
            record.id: record.asset_name
            for record in project_files
        }

    if len(project_files_ids) == 0: # if there is no files
        return JSONResponse(
            status_code=status.HTTP_400_BAD_REQUEST,
            content={
                "signal": ResponseSignal.NO_FILES_ERROR.value,
            }
        )
    
    # Processing 

    process_controller = ProcessController(project_id=project_id)
    no_records = 0
    no_files = 0
    
    chunk_model = await ChunkModel.create_instance(
            db_client=request.app.db_client
            )

    if do_reset==1:    
        _ = await chunk_model.delete_chunks_by_project_id(project_id=project.id)

    for asset_id, file_id in project_file_ids.items(): # asset_id = _id created by mongo
        
        file_content = process_controller.get_file_content(file_id=file_id)
        if file_content is None:
            logger.error(f"Failed to load content for file_id: {file_id} in project_id: {project_id}")
            continue

        file_chunks = process_controller.process_file_content(
            file_content=file_content,
            file_id=file_id,
            chunk_size=chunk_size,
            overlap_size=overlap
        )
        if file_chunks is None or len(file_chunks)==0:
            return JSONResponse(
                status_code=status.HTTP_400_BAD_REQUEST, 
                content = {
                    "signal": ResponseSignal.FILE_PROCESSING_FAILED.value
                }
            )
        file_chunks_records = [
            DataChunk(
                chunk_text = chunk.page_content,
                chunk_meta = chunk.metadata,
                chunk_order = i+1,
                chunk_project_id = project.id,
                chunk_asset_id = asset_id 
            )
            for i, chunk in enumerate(file_chunks)
        ]
        
        no_records += await chunk_model.insert_many_chunks(chunks=file_chunks_records)
        no_files += 1

    return JSONResponse(
        content = {
                "signal": ResponseSignal.PROCESSING_SUCCESS.value,
                "inserted_chunks": no_records,
                "processed_files": no_files
        }
    )
from fastapi import APIRouter, status, Header, HTTPException
from .schemas import AnswerSchema, ModelSchema
from .dependencies import RAGDep, GenerationDep, DbDep
from database.db_utils import (
    save_user_model_architecture, 
    insert_chat_log, 
    get_user_model_architecture, 
    get_user_model_architectures,
    create_session,
    get_session,
    update_session,
    delete_user_model)
import logging
import uuid
import asyncio 
logger = logging.getLogger(__name__)

router = APIRouter(prefix='/api/v1/nn', tags=['NN generation by architecture'])

@router.post('/gen_model', response_model=AnswerSchema, status_code=status.HTTP_201_CREATED)
async def generate_model_code(
    arch: ModelSchema, 
    rag: RAGDep, 
    gen: GenerationDep,
    db: DbDep,
    session_id: str = Header(None, alias="session_id"),
):
    # Generate session ID if not provided
    if not session_id:
        session_id = str(uuid.uuid4())
        logger.info(f"Generated new session_id for model generation: {session_id}")
    session_data = get_session(session_id)
    if not session_data:
        create_session(
            session_id=session_id, 
            category='model_generation', 
            original_query=f'Generate model: {arch.model_name}',
            title=f"Model {arch.model_name}"
        )
    else:
        update_session(session_id=session_id)
    logger.info(f"Model generation request - Session: {session_id}, Model: {arch.model_name}")
    
    try:
        # Extract layers info
        layers_types = [layer['type'] for layer in arch.layers]
        query = f"Описание архитектуры: {arch.model_name}, слои: {', '.join(layers_types)}"
        
        # Search similar code using RAG
        context = rag.search_similar_code(query)
        
        # Generate model code
        generated_answer = gen.generate(
            architecture_json=arch.model_dump_json(), 
            context=context
        )
        
        try:
            save_user_model_architecture(
                user_id=session_id,
                model_name=arch.model_name,
                architecture=arch.model_dump(),
                generated_code=generated_answer
            )
            logger.info(f"Model architecture saved for user: {session_id}")
        except Exception as e:
            logger.error(f"Failed to save model architecture: {e}")
        
        insert_chat_log(
            session_id=session_id, 
            user_query=f"Generate model: {arch.model_name}", 
            agent_response=generated_answer, 
            category="model_generation"
        )
        return AnswerSchema(
            session_id=session_id,
            status="success",
            comments="",
            model_name=arch.model_name,
            generated_code=generated_answer
        )
        
    except Exception as e:
        logger.error(f"Error in model generation: {e}", exc_info=True)

@router.get('/get_models/{session_id}')
async def get_user_models(
    session_id: str
):
    try:
        models = await asyncio.to_thread(get_user_model_architectures, session_id)
        return models
    except Exception as e:
        logger.error(f"Failed to retrieve models: {e}")
        raise HTTPException(status_code=500, detail="Failed to retrieve models")
    
@router.get('/get_model/{session_id}/{model_id}')
async def get_specific_model(
    session_id: str,
    model_id: int
):
    try:
        model = await asyncio.to_thread(get_user_model_architecture, session_id, model_id)
        if not model:
            raise HTTPException(status_code=404, detail="Model not found")
        return model
    except Exception as e:
        logger.error(f"Failed to retrieve model: {e}")
        raise HTTPException(status_code=500, detail="Failed to retrieve model")

@router.delete('/delete_model/{model_id}')
async def delete_model(
    model_id: int,
    session_id: str = Header(None, alias="session_id"),
):
    if not session_id:
        raise HTTPException(status_code=400, detail="session_id header is required")

    try:
        deleted = delete_user_model(model_id, session_id)
        if not deleted:
            raise HTTPException(status_code=404, detail="Model not found or access denied")
        return {"success": True, "message": "Model deleted successfully"}
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to delete model: {e}")
        raise HTTPException(status_code=500, detail="Failed to delete model")
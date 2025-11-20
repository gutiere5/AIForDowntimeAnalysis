from fastapi import APIRouter

router = APIRouter()


@router.head('/health')
@router.get('/health')
def health_check():
    return 'ok'

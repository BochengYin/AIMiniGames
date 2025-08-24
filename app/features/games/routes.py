"""
Games Routes
CRUD operations for games with mobile optimization
"""

from typing import Any, List, Optional
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.core.security import get_current_user
from app.features.auth.models import User
from app.features.games.models import Game
from app.features.games.schemas import (
    GameCreate,
    GameUpdate,
    GameResponse,
    GameListResponse,
    GameStats
)

router = APIRouter()


@router.get("/", response_model=GameListResponse)
async def get_games(
    page: int = Query(1, ge=1, description="Page number"),
    limit: int = Query(20, ge=1, le=100, description="Items per page"),
    category: Optional[str] = Query(None, description="Filter by category"),
    search: Optional[str] = Query(None, description="Search in title and description"),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
) -> Any:
    """
    Get user's games with pagination and filtering
    Optimized for mobile infinite scroll
    """
    games, total = await Game.get_user_games(
        db,
        user_id=current_user.id,
        page=page,
        limit=limit,
        category=category,
        search=search
    )
    
    game_responses = [GameResponse.from_orm(game) for game in games]
    
    return GameListResponse(
        games=game_responses,
        total=total,
        page=page,
        limit=limit,
        has_more=len(games) == limit
    )


@router.get("/{game_id}", response_model=GameResponse)
async def get_game(
    game_id: str,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
) -> Any:
    """
    Get a specific game by ID
    """
    game = await Game.get_by_id(db, game_id)
    if not game:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Game not found"
        )
    
    # Check if user owns the game or it's public
    if game.creator_id != current_user.id and not game.is_public:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Access denied"
        )
    
    return GameResponse.from_orm(game)


@router.post("/", response_model=GameResponse)
async def create_game(
    game_data: GameCreate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
) -> Any:
    """
    Create a new game
    Mobile apps can upload game data directly
    """
    # Check user's game limit
    user_game_count = await Game.count_user_games(db, current_user.id)
    if user_game_count >= 100:  # TODO: Get from settings
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Maximum number of games reached"
        )
    
    # Create game
    game = await Game.create(
        db,
        creator_id=current_user.id,
        title=game_data.title,
        description=game_data.description,
        category=game_data.category,
        game_data=game_data.game_data,
        assets=game_data.assets,
        is_public=game_data.is_public
    )
    
    return GameResponse.from_orm(game)


@router.put("/{game_id}", response_model=GameResponse)
async def update_game(
    game_id: str,
    game_data: GameUpdate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
) -> Any:
    """
    Update an existing game
    """
    game = await Game.get_by_id(db, game_id)
    if not game:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Game not found"
        )
    
    # Check ownership
    if game.creator_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You can only edit your own games"
        )
    
    # Update game
    updated_game = await game.update(db, **game_data.dict(exclude_unset=True))
    
    return GameResponse.from_orm(updated_game)


@router.delete("/{game_id}")
async def delete_game(
    game_id: str,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
) -> Any:
    """
    Delete a game
    """
    game = await Game.get_by_id(db, game_id)
    if not game:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Game not found"
        )
    
    # Check ownership
    if game.creator_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You can only delete your own games"
        )
    
    await game.delete(db)
    
    return {"message": "Game deleted successfully"}


@router.post("/{game_id}/play")
async def record_play_session(
    game_id: str,
    session_data: dict,  # TODO: Create proper schema
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
) -> Any:
    """
    Record a play session for analytics
    Mobile apps can send play data for statistics
    """
    game = await Game.get_by_id(db, game_id)
    if not game:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Game not found"
        )
    
    # TODO: Store play session data
    # This would include score, duration, achievements, etc.
    
    return {"message": "Play session recorded"}


@router.get("/{game_id}/stats", response_model=GameStats)
async def get_game_stats(
    game_id: str,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
) -> Any:
    """
    Get game statistics
    """
    game = await Game.get_by_id(db, game_id)
    if not game:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Game not found"
        )
    
    # Check access permissions
    if game.creator_id != current_user.id and not game.is_public:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Access denied"
        )
    
    # TODO: Get actual stats from database
    stats = GameStats(
        total_plays=0,
        unique_players=0,
        average_session_duration=0,
        highest_score=0,
        total_playtime_hours=0
    )
    
    return stats


@router.get("/categories/list")
async def get_categories() -> Any:
    """
    Get list of available game categories
    """
    categories = [
        {"id": "puzzle", "name": "Puzzle", "icon": "extension"},
        {"id": "action", "name": "Action", "icon": "flash_on"},
        {"id": "casual", "name": "Casual", "icon": "sports_esports"},
        {"id": "strategy", "name": "Strategy", "icon": "psychology"},
        {"id": "educational", "name": "Educational", "icon": "school"},
        {"id": "arcade", "name": "Arcade", "icon": "videogame_asset"},
    ]
    
    return {"categories": categories}
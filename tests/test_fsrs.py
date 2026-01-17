import pytest
from datetime import datetime
from domain.entities.card import FSRSState
from application.services.fsrs_service import FSRSService


def test_first_review():
    """Тест первого повторения карточки"""
    service = FSRSService()
    state = FSRSState()
    
    # Первое повторение с хорошим результатом (quality=4)
    updated_state = service.review_card(state, quality=4)
    
    assert updated_state.review_count == 1
    assert updated_state.stability > 0
    assert updated_state.due_date is not None
    assert updated_state.last_review is not None


def test_subsequent_review():
    """Тест последующих повторений"""
    service = FSRSService()
    
    # Первое повторение
    state = FSRSState()
    state = service.review_card(state, quality=4)
    
    # Второе повторение
    previous_stability = state.stability
    state = service.review_card(state, quality=5)
    
    assert state.review_count == 2
    assert state.stability > previous_stability  # Стабильность должна увеличиться
    assert state.interval > 0


def test_poor_review():
    """Тест плохого повторения"""
    service = FSRSService()
    
    # Первое повторение с плохим результатом
    state = FSRSState()
    state = service.review_card(state, quality=1)
    
    assert state.review_count == 1
    assert state.stability < 1.0  # Стабильность должна быть низкой
    assert state.interval == 1  # Интервал должен быть 1 день

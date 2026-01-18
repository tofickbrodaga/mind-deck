from datetime import datetime, timedelta
from domain.entities.card import FSRSState


class FSRSService:
    """
    FSRS (Free Spaced Repetition Scheduler) - улучшенный алгоритм интервального повторения
    Упрощенная версия алгоритма для демонстрации
    """
    
    def __init__(self):
        # Начальные параметры FSRS
        self.initial_stability = 0.4
        self.min_stability = 0.1
        self.max_stability = 365.0
        self.forgetting_curve = 0.9
    
    def review_card(self, state: FSRSState, quality: int) -> FSRSState:
        """
        Обработать повторение карточки
        
        Args:
            state: Текущее состояние карточки
            quality: Оценка качества ответа (0-5)
                - 0: Забыл
                - 1: Плохо (с подсказкой)
                - 2: Хорошо (с усилием)
                - 3: Отлично (легко)
                - 4: Очень легко
                - 5: Слишком легко
            
        Returns:
            Обновленное состояние карточки
        """
        now = datetime.utcnow()
        
        # Если карточка новая (первое повторение)
        if state.review_count == 0:
            return self._first_review(state, quality, now)
        
        # Последующие повторения
        return self._subsequent_review(state, quality, now)
    
    def _first_review(self, state: FSRSState, quality: int, now: datetime) -> FSRSState:
        """Первое повторение карточки"""
        if quality >= 3:
            stability = self.initial_stability * (1 + quality - 3)
        else:
            stability = self.initial_stability * 0.5

        interval = self._calculate_interval(stability, quality)
        
        state.stability = stability
        state.difficulty = max(0.1, min(1.0, (4 - quality) / 4))
        state.ease_factor = 2.5
        state.interval = interval
        state.review_count = 1
        state.last_review = now
        state.due_date = now + timedelta(days=interval)
        
        return state
    
    def _subsequent_review(self, state: FSRSState, quality: int, now: datetime) -> FSRSState:
        """Последующие повторения карточки"""
        # Вычисляем новый интервал в зависимости от качества
        if quality >= 3:
            # Хороший ответ - увеличиваем стабильность
            if state.review_count == 1:
                stability = state.stability * 1.5
            else:
                stability = state.stability * (1 + (quality - 3) * 0.3)
        else:
            # Плохой ответ - уменьшаем стабильность
            stability = state.stability * 0.8
        
        # Ограничиваем стабильность
        stability = max(self.min_stability, min(self.max_stability, stability))
        
        # Обновляем сложность
        difficulty = state.difficulty - 0.2 + (4 - quality) * 0.1
        difficulty = max(0.1, min(1.0, difficulty))
        ease_factor = state.ease_factor + (0.1 - (5 - quality) * (0.08 + (5 - quality) * 0.02))
        ease_factor = max(1.3, min(2.5, ease_factor))

        interval = self._calculate_interval(stability, quality)
        
        state.stability = stability
        state.difficulty = difficulty
        state.ease_factor = ease_factor
        state.interval = interval
        state.review_count += 1
        state.last_review = now
        state.due_date = now + timedelta(days=interval)
        
        return state
    
    def _calculate_interval(self, stability: float, quality: int) -> int:
        """Вычислить интервал до следующего повторения (в днях)"""
        if quality >= 3:
            # Хороший ответ
            base_interval = stability * 2
            return max(1, int(base_interval))
        else:
            # Плохой ответ - повторяем завтра
            return 1

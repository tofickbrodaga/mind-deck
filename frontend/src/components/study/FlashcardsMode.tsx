import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { useState } from 'react';
import { studyAPI, cardsAPI } from '@/services/api';
import { ArrowLeft, RotateCcw, Check, X } from 'lucide-react';
import { useNavigate } from 'react-router-dom';

interface FlashcardsModeProps {
  deckId: string;
}

export default function FlashcardsMode({ deckId }: FlashcardsModeProps) {
  const [currentIndex, setCurrentIndex] = useState(0);
  const [isFlipped, setIsFlipped] = useState(false);
  const navigate = useNavigate();
  const queryClient = useQueryClient();

  const { data, isLoading } = useQuery({
    queryKey: ['study-flashcards', deckId],
    queryFn: () => studyAPI.getFlashcards(deckId, 20),
  });

  const reviewMutation = useMutation({
    mutationFn: ({ cardId, quality }: { cardId: string; quality: number }) =>
      cardsAPI.review(cardId, { quality }),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['cards', deckId] });
    },
  });

  const cards = data?.cards || [];

  if (isLoading) {
    return (
      <div className="flex justify-center items-center h-64">
        <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-primary-600"></div>
      </div>
    );
  }

  if (cards.length === 0) {
    return (
      <div className="card text-center py-12">
        <h2 className="text-2xl font-bold text-gray-900 mb-2">Нет карточек для изучения</h2>
        <button
          onClick={() => navigate(`/decks/${deckId}`)}
          className="btn btn-primary mt-4"
        >
          Вернуться к колоде
        </button>
      </div>
    );
  }

  const currentCard = cards[currentIndex];
  const isLastCard = currentIndex === cards.length - 1;

  const handleQuality = async (quality: number) => {
    await reviewMutation.mutateAsync({ cardId: currentCard.id, quality });
    
    if (isLastCard) {
      navigate(`/decks/${deckId}`);
    } else {
      setCurrentIndex(currentIndex + 1);
      setIsFlipped(false);
    }
  };

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <button
          onClick={() => navigate(`/decks/${deckId}`)}
          className="flex items-center space-x-2 text-gray-600 hover:text-gray-900"
        >
          <ArrowLeft className="h-5 w-5" />
          <span>Выход</span>
        </button>
        <div className="text-sm text-gray-600">
          {currentIndex + 1} / {cards.length}
        </div>
      </div>

      <div className="relative h-96">
        <div
          className="card absolute inset-0 cursor-pointer transition-all duration-300"
          onClick={() => setIsFlipped(!isFlipped)}
        >
          {!isFlipped ? (
            <div className="h-full flex items-center justify-center">
              <div className="text-center">
                <div className="text-sm text-gray-500 mb-2">Лицевая сторона</div>
                <div className="text-2xl font-medium text-gray-900">{currentCard.front}</div>
              </div>
            </div>
          ) : (
            <div className="h-full flex items-center justify-center">
              <div className="text-center">
                <div className="text-sm text-gray-500 mb-2">Обратная сторона</div>
                <div className="text-2xl font-medium text-gray-900">{currentCard.back}</div>
              </div>
            </div>
          )}
        </div>
      </div>

      <div className="flex items-center justify-center space-x-4">
        <button
          onClick={() => setIsFlipped(!isFlipped)}
          className="btn btn-secondary flex items-center space-x-2"
        >
          <RotateCcw className="h-4 w-4" />
          <span>Перевернуть</span>
        </button>
      </div>

      {isFlipped && (
        <div className="flex justify-center space-x-3">
          <button
            onClick={() => handleQuality(0)}
            className="px-6 py-3 bg-red-500 text-white rounded-lg hover:bg-red-600 transition-colors flex items-center space-x-2"
          >
            <X className="h-5 w-5" />
            <span>Снова</span>
          </button>
          <button
            onClick={() => handleQuality(1)}
            className="px-6 py-3 bg-orange-500 text-white rounded-lg hover:bg-orange-600 transition-colors"
          >
            Сложно
          </button>
          <button
            onClick={() => handleQuality(3)}
            className="px-6 py-3 bg-yellow-500 text-white rounded-lg hover:bg-yellow-600 transition-colors"
          >
            Хорошо
          </button>
          <button
            onClick={() => handleQuality(5)}
            className="px-6 py-3 bg-green-500 text-white rounded-lg hover:bg-green-600 transition-colors flex items-center space-x-2"
          >
            <Check className="h-5 w-5" />
            <span>Легко</span>
          </button>
        </div>
      )}
    </div>
  );
}

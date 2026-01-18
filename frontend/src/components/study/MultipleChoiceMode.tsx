import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { useState, useEffect } from 'react';
import { studyAPI, cardsAPI } from '@/services/api';
import { ArrowLeft } from 'lucide-react';
import { useNavigate } from 'react-router-dom';

interface MultipleChoiceModeProps {
  deckId: string;
}

export default function MultipleChoiceMode({ deckId }: MultipleChoiceModeProps) {
  const [currentCardId, setCurrentCardId] = useState<string | null>(null);
  const [selectedIndex, setSelectedIndex] = useState<number | null>(null);
  const [showResult, setShowResult] = useState(false);
  const navigate = useNavigate();
  const queryClient = useQueryClient();

  const { data: cards } = useQuery({
    queryKey: ['cards', deckId],
    queryFn: () => cardsAPI.getByDeck(deckId),
  });

  const { data: questionData, refetch } = useQuery({
    queryKey: ['study-multiple-choice', deckId, currentCardId],
    queryFn: () => {
      if (!currentCardId) return null;
      return studyAPI.getMultipleChoice(deckId, currentCardId);
    },
    enabled: !!currentCardId,
  });

  const reviewMutation = useMutation({
    mutationFn: ({ cardId, quality }: { cardId: string; quality: number }) =>
      cardsAPI.review(cardId, { quality }),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['cards', deckId] });
    },
  });

  useEffect(() => {
    if (cards && cards.length > 0 && !currentCardId) {
      setCurrentCardId(cards[0].id);
    }
  }, [cards, currentCardId]);

  if (!cards || cards.length === 0) {
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

  if (!questionData || !currentCardId) {
    return (
      <div className="flex justify-center items-center h-64">
        <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-primary-600"></div>
      </div>
    );
  }

  const isCorrect = selectedIndex === questionData.correct_index;
  const currentCardIndex = cards.findIndex((c) => c.id === currentCardId);
  const isLastCard = currentCardIndex === cards.length - 1;

  const handleAnswer = (index: number) => {
    if (showResult) return;
    setSelectedIndex(index);
    setShowResult(true);
    
    const quality = index === questionData.correct_index ? 5 : 1;
    reviewMutation.mutate({ cardId: currentCardId, quality });
  };

  const handleNext = () => {
    if (isLastCard) {
      navigate(`/decks/${deckId}`);
    } else {
      setCurrentCardId(cards[currentCardIndex + 1].id);
      setSelectedIndex(null);
      setShowResult(false);
      refetch();
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
          {currentCardIndex + 1} / {cards.length}
        </div>
      </div>

      <div className="card text-center py-12">
        <h2 className="text-3xl font-bold text-gray-900 mb-8">{questionData.card.front}</h2>
        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
          {questionData.options.map((option, index) => {
            let buttonClass = 'btn btn-secondary';
            if (showResult) {
              if (index === questionData.correct_index) {
                buttonClass = 'btn bg-green-500 text-white hover:bg-green-600';
              } else if (index === selectedIndex && index !== questionData.correct_index) {
                buttonClass = 'btn bg-red-500 text-white hover:bg-red-600';
              }
            }

            return (
              <button
                key={index}
                onClick={() => handleAnswer(index)}
                className={buttonClass}
                disabled={showResult}
              >
                {option}
              </button>
            );
          })}
        </div>
      </div>

      {showResult && (
        <div className="text-center">
          <div className={`text-xl font-semibold mb-4 ${isCorrect ? 'text-green-600' : 'text-red-600'}`}>
            {isCorrect ? 'Правильно! ✓' : 'Неправильно ✗'}
          </div>
          <button onClick={handleNext} className="btn btn-primary">
            {isLastCard ? 'Завершить' : 'Следующий вопрос'}
          </button>
        </div>
      )}
    </div>
  );
}

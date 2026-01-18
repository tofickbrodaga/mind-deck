import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { useState } from 'react';
import { cardsAPI, studyAPI } from '@/services/api';
import { ArrowLeft } from 'lucide-react';
import { useNavigate } from 'react-router-dom';

interface WriteModeProps {
  deckId: string;
}

export default function WriteMode({ deckId }: WriteModeProps) {
  const [currentIndex, setCurrentIndex] = useState(0);
  const [answer, setAnswer] = useState('');
  const [showResult, setShowResult] = useState(false);
  const [result, setResult] = useState<{ is_correct: boolean; correct_answer: string } | null>(null);
  const navigate = useNavigate();
  const queryClient = useQueryClient();

  const { data: cards, isLoading } = useQuery({
    queryKey: ['cards-due', deckId],
    queryFn: () => cardsAPI.getDueCards(deckId, 20),
  });

  const checkMutation = useMutation({
    mutationFn: ({ cardId, answer }: { cardId: string; answer: string }) =>
      studyAPI.checkWrite({ card_id: cardId, answer }),
    onSuccess: (data) => {
      setResult(data);
      setShowResult(true);
      queryClient.invalidateQueries({ queryKey: ['cards', deckId] });
    },
  });

  if (isLoading) {
    return (
      <div className="flex justify-center items-center h-64">
        <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-primary-600"></div>
      </div>
    );
  }

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

  const currentCard = cards[currentIndex];
  const isLastCard = currentIndex === cards.length - 1;

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    if (!answer.trim()) return;
    checkMutation.mutate({ cardId: currentCard.id, answer });
  };

  const handleNext = () => {
    if (isLastCard) {
      navigate(`/decks/${deckId}`);
    } else {
      setCurrentIndex(currentIndex + 1);
      setAnswer('');
      setShowResult(false);
      setResult(null);
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

      <div className="card">
        <h2 className="text-3xl font-bold text-gray-900 mb-6 text-center">
          {currentCard.front}
        </h2>

        {!showResult ? (
          <form onSubmit={handleSubmit} className="space-y-4">
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                Ваш ответ:
              </label>
              <textarea
                value={answer}
                onChange={(e) => setAnswer(e.target.value)}
                className="input"
                rows={4}
                placeholder="Введите ответ..."
                autoFocus
              />
            </div>
            <button type="submit" className="btn btn-primary w-full">
              Проверить
            </button>
          </form>
        ) : (
          <div className="space-y-4">
            <div className={`p-4 rounded-lg ${result?.is_correct ? 'bg-green-50 border border-green-200' : 'bg-red-50 border border-red-200'}`}>
              <div className={`text-lg font-semibold mb-2 ${result?.is_correct ? 'text-green-800' : 'text-red-800'}`}>
                {result?.is_correct ? 'Правильно! ✓' : 'Неправильно ✗'}
              </div>
              <div className="text-gray-700">
                <div className="mb-2">Ваш ответ: <span className="font-medium">{answer}</span></div>
                <div>Правильный ответ: <span className="font-medium">{result?.correct_answer}</span></div>
              </div>
            </div>
            <button onClick={handleNext} className="btn btn-primary w-full">
              {isLastCard ? 'Завершить' : 'Следующий вопрос'}
            </button>
          </div>
        )}
      </div>
    </div>
  );
}

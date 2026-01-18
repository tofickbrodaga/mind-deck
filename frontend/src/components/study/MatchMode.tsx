import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { useState } from 'react';
import { studyAPI, cardsAPI } from '@/services/api';
import { ArrowLeft } from 'lucide-react';
import { useNavigate } from 'react-router-dom';

interface MatchModeProps {
  deckId: string;
}

export default function MatchMode({ deckId }: MatchModeProps) {
  const [selectedTerm, setSelectedTerm] = useState<string | null>(null);
  const [selectedDefinition, setSelectedDefinition] = useState<string | null>(null);
  const [matchedPairs, setMatchedPairs] = useState<Set<string>>(new Set());
  const navigate = useNavigate();
  const queryClient = useQueryClient();

  const { data: matchData, isLoading } = useQuery({
    queryKey: ['study-match', deckId],
    queryFn: () => studyAPI.getMatch(deckId, 10),
  });

  const reviewMutation = useMutation({
    mutationFn: ({ cardId, quality }: { cardId: string; quality: number }) =>
      cardsAPI.review(cardId, { quality }),
    onSuccess: () => {
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

  if (!matchData) {
    return (
      <div className="card text-center py-12">
        <h2 className="text-2xl font-bold text-gray-900 mb-2">Нет данных для изучения</h2>
        <button
          onClick={() => navigate(`/decks/${deckId}`)}
          className="btn btn-primary mt-4"
        >
          Вернуться к колоде
        </button>
      </div>
    );
  }

  const handleTermClick = (term: string) => {
    if (matchedPairs.has(term)) return;
    
    if (selectedTerm === term) {
      setSelectedTerm(null);
    } else {
      setSelectedTerm(term);
      if (selectedDefinition) {
        checkMatch(term, selectedDefinition);
      }
    }
  };

  const handleDefinitionClick = (definition: string) => {
    if (matchedPairs.has(definition)) return;
    
    if (selectedDefinition === definition) {
      setSelectedDefinition(null);
    } else {
      setSelectedDefinition(definition);
      if (selectedTerm) {
        checkMatch(selectedTerm, definition);
      }
    }
  };

  const checkMatch = (term: string, definition: string) => {
    const isCorrect = matchData.pairs.some(
      ([t, d]) => t === term && d === definition
    );

    if (isCorrect) {
      setMatchedPairs(new Set([...matchedPairs, term, definition]));
      setSelectedTerm(null);
      setSelectedDefinition(null);
      
      // Находим карточку и обновляем её
      const pair = matchData.pairs.find(([t, d]) => t === term && d === definition);
      if (pair) {
        // Здесь нужно найти cardId по паре, но у нас нет этой информации
        // Можно использовать качество 5 для успешного сопоставления
      }
    } else {
      setTimeout(() => {
        setSelectedTerm(null);
        setSelectedDefinition(null);
      }, 1000);
    }
  };

  const allMatched = matchData.pairs.every(
    ([term, definition]) => matchedPairs.has(term) && matchedPairs.has(definition)
  );

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
        {allMatched && (
          <div className="text-green-600 font-semibold">Все сопоставлены! ✓</div>
        )}
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
        <div>
          <h3 className="text-lg font-semibold text-gray-900 mb-4">Термины</h3>
          <div className="space-y-2">
            {matchData.terms.map((term, index) => {
              const isMatched = matchedPairs.has(term);
              const isSelected = selectedTerm === term;
              
              return (
                <button
                  key={index}
                  onClick={() => handleTermClick(term)}
                  disabled={isMatched}
                  className={`w-full p-4 text-left rounded-lg transition-colors ${
                    isMatched
                      ? 'bg-green-100 text-green-800 line-through'
                      : isSelected
                      ? 'bg-primary-100 border-2 border-primary-500'
                      : 'bg-white border border-gray-200 hover:border-primary-300'
                  }`}
                >
                  {term}
                </button>
              );
            })}
          </div>
        </div>

        <div>
          <h3 className="text-lg font-semibold text-gray-900 mb-4">Определения</h3>
          <div className="space-y-2">
            {matchData.definitions.map((definition, index) => {
              const isMatched = matchedPairs.has(definition);
              const isSelected = selectedDefinition === definition;
              
              return (
                <button
                  key={index}
                  onClick={() => handleDefinitionClick(definition)}
                  disabled={isMatched}
                  className={`w-full p-4 text-left rounded-lg transition-colors ${
                    isMatched
                      ? 'bg-green-100 text-green-800 line-through'
                      : isSelected
                      ? 'bg-primary-100 border-2 border-primary-500'
                      : 'bg-white border border-gray-200 hover:border-primary-300'
                  }`}
                >
                  {definition}
                </button>
              );
            })}
          </div>
        </div>
      </div>

      {allMatched && (
        <div className="text-center">
          <button
            onClick={() => navigate(`/decks/${deckId}`)}
            className="btn btn-primary"
          >
            Завершить
          </button>
        </div>
      )}
    </div>
  );
}

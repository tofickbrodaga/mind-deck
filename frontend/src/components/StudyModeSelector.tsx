import { useNavigate } from 'react-router-dom';
import { BookOpen, List, PenTool, Link as LinkIcon, ArrowLeft } from 'lucide-react';
import type { StudyMode } from '@/types';

interface StudyModeSelectorProps {
  deckId: string;
  onSelectMode: (mode: StudyMode) => void;
}

export default function StudyModeSelector({ deckId, onSelectMode }: StudyModeSelectorProps) {
  const navigate = useNavigate();

  const modes = [
    {
      id: 'flashcards' as StudyMode,
      name: 'Флэшкарты',
      description: 'Классический режим изучения с переворачиванием карточек',
      icon: BookOpen,
      color: 'bg-blue-500',
    },
    {
      id: 'multiple_choice' as StudyMode,
      name: 'Множественный выбор',
      description: 'Выберите правильный ответ из предложенных вариантов',
      icon: List,
      color: 'bg-green-500',
    },
    {
      id: 'write' as StudyMode,
      name: 'Письмо',
      description: 'Напишите ответ самостоятельно',
      icon: PenTool,
      color: 'bg-purple-500',
    },
    {
      id: 'match' as StudyMode,
      name: 'Подбор',
      description: 'Сопоставьте термины с определениями',
      icon: LinkIcon,
      color: 'bg-orange-500',
    },
  ];

  return (
    <div className="space-y-6">
      <div className="flex items-center space-x-4">
        <button
          onClick={() => navigate(`/decks/${deckId}`)}
          className="p-2 hover:bg-gray-100 rounded-lg transition-colors"
        >
          <ArrowLeft className="h-5 w-5" />
        </button>
        <h1 className="text-3xl font-bold text-gray-900">Выберите режим изучения</h1>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
        {modes.map((mode) => {
          const Icon = mode.icon;
          return (
            <button
              key={mode.id}
              onClick={() => onSelectMode(mode.id)}
              className="card hover:shadow-lg transition-all hover:scale-105 text-left"
            >
              <div className={`${mode.color} w-12 h-12 rounded-lg flex items-center justify-center mb-4`}>
                <Icon className="h-6 w-6 text-white" />
              </div>
              <h3 className="text-xl font-semibold text-gray-900 mb-2">{mode.name}</h3>
              <p className="text-gray-600">{mode.description}</p>
            </button>
          );
        })}
      </div>
    </div>
  );
}

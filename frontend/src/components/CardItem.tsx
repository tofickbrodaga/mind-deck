import { Card } from '@/types';
import { Edit, Trash2 } from 'lucide-react';

interface CardItemProps {
  card: Card;
  onEdit: (id: string) => void;
  onDelete: (id: string) => void;
}

export default function CardItem({ card, onEdit, onDelete }: CardItemProps) {
  return (
    <div className="card hover:shadow-lg transition-shadow">
      <div className="flex justify-between items-start mb-3">
        <div className="flex-1">
          <div className="text-sm font-medium text-gray-500 mb-1">Лицевая сторона</div>
          <div className="text-gray-900 mb-3">{card.front}</div>
          <div className="text-sm font-medium text-gray-500 mb-1">Обратная сторона</div>
          <div className="text-gray-700">{card.back}</div>
        </div>
        <div className="flex space-x-1 ml-2">
          <button
            onClick={() => onEdit(card.id)}
            className="p-2 text-gray-600 hover:text-primary-600 hover:bg-gray-100 rounded-lg transition-colors"
            title="Редактировать"
          >
            <Edit className="h-4 w-4" />
          </button>
          <button
            onClick={() => onDelete(card.id)}
            className="p-2 text-gray-600 hover:text-red-600 hover:bg-gray-100 rounded-lg transition-colors"
            title="Удалить"
          >
            <Trash2 className="h-4 w-4" />
          </button>
        </div>
      </div>
      <div className="pt-3 border-t border-gray-200 text-xs text-gray-500">
        Повторений: {card.fsrs_state.review_count} | Интервал: {card.fsrs_state.interval} дн.
      </div>
    </div>
  );
}

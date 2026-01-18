import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { useParams, useNavigate } from 'react-router-dom';
import { decksAPI, cardsAPI, importAPI } from '@/services/api';
import { Plus, ArrowLeft, Edit, Trash2, Upload } from 'lucide-react';
import { useState } from 'react';
import Layout from '@/components/Layout';
import CardItem from '@/components/CardItem';

export default function DeckDetail() {
  const { id } = useParams<{ id: string }>();
  const navigate = useNavigate();
  const [showCreateModal, setShowCreateModal] = useState(false);
  const [front, setFront] = useState('');
  const [back, setBack] = useState('');
  const [showImportModal, setShowImportModal] = useState(false);
  const queryClient = useQueryClient();

  const { data: deck, isLoading: deckLoading } = useQuery({
    queryKey: ['deck', id],
    queryFn: () => decksAPI.getById(id!),
    enabled: !!id,
  });

  const { data: cards, isLoading: cardsLoading } = useQuery({
    queryKey: ['cards', id],
    queryFn: () => cardsAPI.getByDeck(id!),
    enabled: !!id,
  });

  const createMutation = useMutation({
    mutationFn: (data: { front: string; back: string }) =>
      cardsAPI.create(id!, data),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['cards', id] });
      setShowCreateModal(false);
      setFront('');
      setBack('');
    },
  });

  const deleteMutation = useMutation({
    mutationFn: cardsAPI.delete,
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['cards', id] });
    },
  });

  const handleCreate = (e: React.FormEvent) => {
    e.preventDefault();
    createMutation.mutate({ front, back });
  };

  const handleDelete = (cardId: string) => {
    if (confirm('Вы уверены, что хотите удалить эту карточку?')) {
      deleteMutation.mutate(cardId);
    }
  };

  if (deckLoading || cardsLoading) {
    return (
      <Layout>
        <div className="flex justify-center items-center h-64">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-primary-600"></div>
        </div>
      </Layout>
    );
  }

  if (!deck) {
    return (
      <Layout>
        <div className="text-center py-12">
          <h2 className="text-2xl font-bold text-gray-900 mb-2">Колода не найдена</h2>
          <button onClick={() => navigate('/')} className="btn btn-primary mt-4">
            Вернуться к колодам
          </button>
        </div>
      </Layout>
    );
  }

  return (
    <Layout>
      <div className="space-y-6">
        <div className="flex items-center space-x-4 mb-6">
          <button
            onClick={() => navigate('/')}
            className="p-2 hover:bg-gray-100 rounded-lg transition-colors"
          >
            <ArrowLeft className="h-5 w-5" />
          </button>
          <div className="flex-1">
            <h1 className="text-3xl font-bold text-gray-900">{deck.title}</h1>
            {deck.description && (
              <p className="text-gray-600 mt-1">{deck.description}</p>
            )}
          </div>
        </div>

        <div className="flex space-x-3">
          <button
            onClick={() => setShowCreateModal(true)}
            className="btn btn-primary flex items-center space-x-2"
          >
            <Plus className="h-5 w-5" />
            <span>Добавить карточку</span>
          </button>
          <button
            onClick={() => setShowImportModal(true)}
            className="btn btn-secondary flex items-center space-x-2"
          >
            <Upload className="h-5 w-5" />
            <span>Импорт</span>
          </button>
          <button
            onClick={() => navigate(`/decks/${id}/edit`)}
            className="btn btn-secondary flex items-center space-x-2"
          >
            <Edit className="h-5 w-5" />
            <span>Редактировать</span>
          </button>
        </div>

        {cards && cards.length === 0 ? (
          <div className="card text-center py-12">
            <h3 className="text-xl font-semibold text-gray-900 mb-2">Нет карточек</h3>
            <p className="text-gray-600 mb-4">Добавьте карточки в эту колоду</p>
            <button
              onClick={() => setShowCreateModal(true)}
              className="btn btn-primary"
            >
              Добавить карточку
            </button>
          </div>
        ) : (
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
            {cards?.map((card) => (
              <CardItem
                key={card.id}
                card={card}
                onDelete={handleDelete}
                onEdit={(cardId) => navigate(`/cards/${cardId}/edit`)}
              />
            ))}
          </div>
        )}

        {showCreateModal && (
          <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
            <div className="bg-white rounded-lg p-6 max-w-md w-full mx-4">
              <h2 className="text-2xl font-bold mb-4">Добавить карточку</h2>
              <form onSubmit={handleCreate} className="space-y-4">
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1">
                    Лицевая сторона
                  </label>
                  <textarea
                    value={front}
                    onChange={(e) => setFront(e.target.value)}
                    className="input"
                    rows={3}
                    required
                    placeholder="Вопрос или термин"
                  />
                </div>
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1">
                    Обратная сторона
                  </label>
                  <textarea
                    value={back}
                    onChange={(e) => setBack(e.target.value)}
                    className="input"
                    rows={3}
                    required
                    placeholder="Ответ или определение"
                  />
                </div>
                <div className="flex space-x-3">
                  <button
                    type="button"
                    onClick={() => {
                      setShowCreateModal(false);
                      setFront('');
                      setBack('');
                    }}
                    className="btn btn-secondary flex-1"
                  >
                    Отмена
                  </button>
                  <button
                    type="submit"
                    disabled={createMutation.isPending}
                    className="btn btn-primary flex-1"
                  >
                    {createMutation.isPending ? 'Добавление...' : 'Добавить'}
                  </button>
                </div>
              </form>
            </div>
          </div>
        )}

        {showImportModal && (
          <ImportModal
            deckId={id!}
            onClose={() => setShowImportModal(false)}
            onSuccess={() => {
              queryClient.invalidateQueries({ queryKey: ['cards', id] });
              setShowImportModal(false);
            }}
          />
        )}
      </div>
    </Layout>
  );
}

function ImportModal({
  deckId,
  onClose,
  onSuccess,
}: {
  deckId: string;
  onClose: () => void;
  onSuccess: () => void;
}) {
  const [file, setFile] = useState<File | null>(null);
  const [importType, setImportType] = useState<'word' | 'excel' | 'image'>('word');
  const [isImporting, setIsImporting] = useState(false);

  const handleImport = async () => {
    if (!file) return;

    setIsImporting(true);
    try {
      if (importType === 'word') {
        await importAPI.importFromWord(deckId, file);
      } else if (importType === 'excel') {
        await importAPI.importFromExcel(deckId, file);
      } else {
        await importAPI.importFromImage(deckId, file);
      }
      onSuccess();
      alert('Карточки успешно импортированы!');
    } catch (error: any) {
      alert(error.response?.data?.detail || 'Ошибка импорта');
    } finally {
      setIsImporting(false);
    }
  };

  return (
    <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
      <div className="bg-white rounded-lg p-6 max-w-md w-full mx-4">
        <h2 className="text-2xl font-bold mb-4">Импорт карточек</h2>
        <div className="space-y-4">
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">
              Тип файла
            </label>
            <select
              value={importType}
              onChange={(e) => setImportType(e.target.value as any)}
              className="input"
            >
              <option value="word">Word (.doc, .docx)</option>
              <option value="excel">Excel (.xls, .xlsx)</option>
              <option value="image">Изображение (OCR)</option>
            </select>
          </div>
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">
              Файл
            </label>
            <input
              type="file"
              onChange={(e) => setFile(e.target.files?.[0] || null)}
              className="input"
              accept={
                importType === 'word'
                  ? '.doc,.docx'
                  : importType === 'excel'
                  ? '.xls,.xlsx'
                  : 'image/*'
              }
            />
          </div>
          <div className="flex space-x-3">
            <button onClick={onClose} className="btn btn-secondary flex-1">
              Отмена
            </button>
            <button
              onClick={handleImport}
              disabled={!file || isImporting}
              className="btn btn-primary flex-1"
            >
              {isImporting ? 'Импорт...' : 'Импортировать'}
            </button>
          </div>
        </div>
      </div>
    </div>
  );
}

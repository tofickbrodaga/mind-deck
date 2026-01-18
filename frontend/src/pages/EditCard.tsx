import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { useParams, useNavigate } from 'react-router-dom';
import { cardsAPI } from '@/services/api';
import { ArrowLeft } from 'lucide-react';
import { useState, useEffect } from 'react';
import Layout from '@/components/Layout';

export default function EditCard() {
  const { id } = useParams<{ id: string }>();
  const navigate = useNavigate();
  const [front, setFront] = useState('');
  const [back, setBack] = useState('');
  const queryClient = useQueryClient();

  const { data: card, isLoading } = useQuery({
    queryKey: ['card', id],
    queryFn: () => cardsAPI.getById(id!),
    enabled: !!id,
  });

  useEffect(() => {
    if (card) {
      setFront(card.front);
      setBack(card.back);
    }
  }, [card]);

  const updateMutation = useMutation({
    mutationFn: (data: { front?: string; back?: string }) =>
      cardsAPI.update(id!, data),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['cards'] });
      queryClient.invalidateQueries({ queryKey: ['card', id] });
      navigate(`/decks/${card?.deck_id}`);
    },
  });

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    updateMutation.mutate({
      front: front || undefined,
      back: back || undefined,
    });
  };

  if (isLoading) {
    return (
      <Layout>
        <div className="flex justify-center items-center h-64">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-primary-600"></div>
        </div>
      </Layout>
    );
  }

  return (
    <Layout>
      <div className="max-w-2xl mx-auto">
        <div className="flex items-center space-x-4 mb-6">
          <button
            onClick={() => navigate(`/decks/${card?.deck_id}`)}
            className="p-2 hover:bg-gray-100 rounded-lg transition-colors"
          >
            <ArrowLeft className="h-5 w-5" />
          </button>
          <h1 className="text-3xl font-bold text-gray-900">Редактировать карточку</h1>
        </div>

        <form onSubmit={handleSubmit} className="card space-y-6">
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">
              Лицевая сторона
            </label>
            <textarea
              value={front}
              onChange={(e) => setFront(e.target.value)}
              className="input"
              rows={4}
              required
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
              rows={4}
              required
            />
          </div>

          <div className="flex space-x-3">
            <button
              type="button"
              onClick={() => navigate(`/decks/${card?.deck_id}`)}
              className="btn btn-secondary"
            >
              Отмена
            </button>
            <button
              type="submit"
              disabled={updateMutation.isPending}
              className="btn btn-primary"
            >
              {updateMutation.isPending ? 'Сохранение...' : 'Сохранить'}
            </button>
          </div>
        </form>
      </div>
    </Layout>
  );
}

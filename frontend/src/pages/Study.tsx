import { useParams, useNavigate } from 'react-router-dom';
import { useState } from 'react';
import Layout from '@/components/Layout';
import StudyModeSelector from '@/components/StudyModeSelector';
import FlashcardsMode from '@/components/study/FlashcardsMode';
import MultipleChoiceMode from '@/components/study/MultipleChoiceMode';
import WriteMode from '@/components/study/WriteMode';
import MatchMode from '@/components/study/MatchMode';
import type { StudyMode } from '@/types';

export default function Study() {
  const { id } = useParams<{ id: string }>();
  const [mode, setMode] = useState<StudyMode | null>(null);

  if (!mode) {
    return (
      <Layout>
        <StudyModeSelector deckId={id!} onSelectMode={setMode} />
      </Layout>
    );
  }

  return (
    <Layout>
      <div className="max-w-4xl mx-auto">
        {mode === 'flashcards' && <FlashcardsMode deckId={id!} />}
        {mode === 'multiple_choice' && <MultipleChoiceMode deckId={id!} />}
        {mode === 'write' && <WriteMode deckId={id!} />}
        {mode === 'match' && <MatchMode deckId={id!} />}
      </div>
    </Layout>
  );
}

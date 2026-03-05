"use client";

type ProgressBarProps = {
  passo: number;
  total: number;
};

export default function ProgressBar({ passo, total }: ProgressBarProps) {
  const progresso = total > 0 ? (passo / total) * 100 : 0;

  return (
    <div className="w-full max-w-xl mb-8">
      <div className="h-1.5 bg-slate-700 rounded-full">
        <div
          className="h-1.5 bg-teal-500 rounded-full transition-all duration-300"
          style={{ width: `${progresso}%` }}
        />
      </div>
      <p className="text-slate-400 text-sm mt-2">
        Pergunta {passo + 1} de {total}
      </p>
    </div>
  );
}

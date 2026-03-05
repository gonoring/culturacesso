"use client";

import { useState, useEffect } from "react";
import { useRouter } from "next/navigation";
import ProgressBar from "@/components/ProgressBar";
import QuestionCard from "@/components/QuestionCard";

type Pergunta = {
  id: string;
  texto: string;
  tipo: "single_choice" | "multi_choice" | "boolean";
  opcoes: { valor: any; label: string }[];
};

export default function TrilhaPage() {
  const router = useRouter();
  const [perguntas, setPerguntas] = useState<Pergunta[]>([]);
  const [passo, setPasso] = useState(0);
  const [respostas, setRespostas] = useState<Record<string, any>>({});
  const [multiSelecionados, setMultiSelecionados] = useState<any[]>([]);
  const [erro, setErro] = useState<string | null>(null);

  useEffect(() => {
    fetch(`${process.env.NEXT_PUBLIC_API_URL}/trilha/perguntas`)
      .then((r) => r.json())
      .then((data) => setPerguntas(data.perguntas))
      .catch(() => setErro("Erro ao carregar perguntas. Verifique se a API está rodando."));
  }, []);

  const perguntaAtual = perguntas[passo];

  function avancar(novasRespostas: Record<string, any>) {
    if (passo + 1 < perguntas.length) {
      setPasso(passo + 1);
      setMultiSelecionados([]);
    } else {
      sessionStorage.setItem("respostas", JSON.stringify(novasRespostas));
      router.push("/resultado");
    }
  }

  function responder(valor: any) {
    const novas = { ...respostas, [perguntaAtual.id]: valor };
    setRespostas(novas);
    avancar(novas);
  }

  function toggleMulti(valor: any) {
    setMultiSelecionados((prev) =>
      prev.includes(valor)
        ? prev.filter((v) => v !== valor)
        : [...prev, valor]
    );
  }

  function confirmarMulti() {
    const novas = { ...respostas, [perguntaAtual.id]: multiSelecionados };
    setRespostas(novas);
    avancar(novas);
  }

  if (erro) {
    return (
      <main className="min-h-screen bg-slate-900 text-white flex items-center justify-center px-4">
        <div className="text-center">
          <p className="text-red-400 text-lg mb-4">{erro}</p>
          <button
            onClick={() => window.location.reload()}
            className="text-teal-400 hover:text-teal-300"
          >
            Tentar novamente
          </button>
        </div>
      </main>
    );
  }

  if (!perguntaAtual) {
    return (
      <main className="min-h-screen bg-slate-900 text-white flex items-center justify-center">
        <p className="text-teal-400 text-lg">Carregando trilha...</p>
      </main>
    );
  }

  return (
    <main className="min-h-screen bg-slate-900 text-white flex flex-col items-center justify-center px-4">
      <ProgressBar passo={passo} total={perguntas.length} />

      <QuestionCard
        texto={perguntaAtual.texto}
        tipo={perguntaAtual.tipo}
        opcoes={perguntaAtual.opcoes}
        onResponder={responder}
        respostasMulti={multiSelecionados}
        onToggleMulti={toggleMulti}
        onConfirmarMulti={confirmarMulti}
      />

      {passo > 0 && (
        <button
          onClick={() => {
            setPasso(passo - 1);
            setMultiSelecionados([]);
          }}
          className="mt-6 text-slate-400 hover:text-white text-sm transition-colors"
        >
          ← Voltar
        </button>
      )}
    </main>
  );
}

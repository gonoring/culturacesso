"use client";

import { useState, useEffect } from "react";
import Link from "next/link";
import EditalCard from "@/components/EditalCard";
import CTAAssessoria from "@/components/CTAAssessoria";

type EditalResultado = {
  titulo: string;
  orgao: string;
  valor_maximo: number | null;
  dificuldade: "baixa" | "media" | "alta";
  data_encerramento: string | null;
  url: string;
  areas: string[];
};

export default function ResultadoPage() {
  const [editais, setEditais] = useState<EditalResultado[]>([]);
  const [valorTotal, setValorTotal] = useState(0);
  const [loading, setLoading] = useState(true);
  const [erro, setErro] = useState<string | null>(null);

  useEffect(() => {
    const respostasRaw = sessionStorage.getItem("respostas");
    if (!respostasRaw) {
      setErro("Nenhuma resposta encontrada. Faça a trilha primeiro.");
      setLoading(false);
      return;
    }

    let respostas;
    try {
      respostas = JSON.parse(respostasRaw);
      if (!respostas || typeof respostas !== "object") throw new Error();
    } catch {
      setErro("Dados de sessão corrompidos. Refaça a trilha.");
      setLoading(false);
      return;
    }

    fetch(`${process.env.NEXT_PUBLIC_API_URL}/trilha/resultado`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(respostas),
    })
      .then((r) => r.json())
      .then((data) => {
        setEditais(data.editais);
        setValorTotal(data.valor_potencial_total);
        setLoading(false);
      })
      .catch(() => {
        setErro("Erro ao calcular resultado. Tente novamente.");
        setLoading(false);
      });
  }, []);

  if (loading) {
    return (
      <div className="min-h-screen bg-slate-900 text-white flex items-center justify-center">
        <p className="text-teal-400 text-lg">
          Calculando seus editais compatíveis...
        </p>
      </div>
    );
  }

  if (erro) {
    return (
      <div className="min-h-screen bg-slate-900 text-white flex items-center justify-center px-4">
        <div className="text-center">
          <p className="text-red-400 text-lg mb-4">{erro}</p>
          <Link
            href="/trilha"
            className="text-teal-400 hover:text-teal-300"
          >
            Refazer a trilha
          </Link>
        </div>
      </div>
    );
  }

  return (
    <main className="min-h-screen bg-slate-900 text-white px-4 py-12">
      <div className="max-w-2xl mx-auto">
        {/* Header resultado */}
        <div className="text-center mb-10">
          <p className="text-slate-400 mb-2">
            Seu projeto pode se enquadrar em
          </p>
          <h1 className="text-5xl font-bold text-white mb-1">
            {editais.length} edital{editais.length !== 1 ? "is" : ""}
          </h1>
          {valorTotal > 0 && (
            <p className="text-teal-400 text-xl mt-3">
              Potencial de captação:{" "}
              <span className="font-bold">
                {valorTotal.toLocaleString("pt-BR", {
                  style: "currency",
                  currency: "BRL",
                })}
              </span>
            </p>
          )}
        </div>

        {/* Cards dos editais */}
        {editais.length > 0 ? (
          <div className="flex flex-col gap-4 mb-10">
            {editais.map((edital, i) => (
              <EditalCard key={i} {...edital} />
            ))}
          </div>
        ) : (
          <div className="text-center mb-10 bg-slate-800 rounded-xl p-8">
            <p className="text-slate-400 text-lg">
              Nenhum edital compatível encontrado no momento.
            </p>
            <p className="text-slate-500 text-sm mt-2">
              Novos editais são adicionados semanalmente. Cadastre-se para ser
              notificado.
            </p>
          </div>
        )}

        {/* CTA */}
        <CTAAssessoria editais={editais} />

        {/* Refazer */}
        <div className="text-center mt-8">
          <Link
            href="/trilha"
            className="text-slate-400 hover:text-white text-sm transition-colors"
          >
            ← Refazer a trilha com outras respostas
          </Link>
        </div>
      </div>
    </main>
  );
}

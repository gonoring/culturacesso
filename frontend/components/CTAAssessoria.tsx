"use client";

import { useState } from "react";

type EditalInfo = {
  titulo: string;
};

type CTAAssessoriaProps = {
  editais: EditalInfo[];
};

export default function CTAAssessoria({ editais }: CTAAssessoriaProps) {
  const [showModal, setShowModal] = useState(false);

  return (
    <>
      <div className="bg-teal-600 rounded-2xl p-8 text-center">
        <h2 className="text-2xl font-bold mb-3">Pronto para submeter?</h2>
        <p className="text-teal-100 mb-6">
          Nossa equipe estrutura o seu projeto e cuida de toda a documentação.
          Você só paga se for aprovado.
        </p>
        <button
          onClick={() => setShowModal(true)}
          className="bg-white text-teal-700 font-bold px-8 py-4 rounded-xl
                     hover:bg-teal-50 transition-colors text-lg"
        >
          Quero assessoria →
        </button>
      </div>

      {showModal && (
        <LeadModal
          onClose={() => setShowModal(false)}
          editais={editais}
        />
      )}
    </>
  );
}

function LeadModal({
  onClose,
  editais,
}: {
  onClose: () => void;
  editais: EditalInfo[];
}) {
  const [form, setForm] = useState({
    nome: "",
    email: "",
    telefone: "",
    projeto_descricao: "",
  });
  const [enviando, setEnviando] = useState(false);
  const [enviado, setEnviado] = useState(false);

  async function enviar() {
    setEnviando(true);
    try {
      await fetch(`${process.env.NEXT_PUBLIC_API_URL}/leads`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          ...form,
          editais_interesse: editais.map((e) => e.titulo),
        }),
      });
      setEnviado(true);
    } catch {
      alert("Erro ao enviar. Tente novamente.");
    } finally {
      setEnviando(false);
    }
  }

  if (enviado) {
    return (
      <div className="fixed inset-0 bg-black/70 flex items-center justify-center z-50 px-4">
        <div className="bg-slate-800 rounded-2xl p-8 w-full max-w-md text-center">
          <div className="text-4xl mb-4">✅</div>
          <h3 className="text-xl font-bold mb-3">Recebemos seu contato!</h3>
          <p className="text-slate-400 mb-6">
            Nossa equipe entrará em contato em até 24h.
          </p>
          <button
            onClick={onClose}
            className="px-6 py-3 rounded-lg bg-teal-600 font-bold"
          >
            Fechar
          </button>
        </div>
      </div>
    );
  }

  return (
    <div className="fixed inset-0 bg-black/70 flex items-center justify-center z-50 px-4">
      <div className="bg-slate-800 rounded-2xl p-8 w-full max-w-md">
        <h3 className="text-xl font-bold mb-6">Fale com nossa equipe</h3>
        {(["nome", "email", "telefone"] as const).map((campo) => (
          <input
            key={campo}
            placeholder={campo.charAt(0).toUpperCase() + campo.slice(1)}
            value={form[campo]}
            onChange={(e) => setForm({ ...form, [campo]: e.target.value })}
            className="w-full bg-slate-700 border border-slate-600 rounded-lg px-4 py-3 mb-3
                       text-white placeholder-slate-400 focus:outline-none focus:border-teal-500"
          />
        ))}
        <textarea
          placeholder="Descreva brevemente seu projeto cultural"
          value={form.projeto_descricao}
          onChange={(e) =>
            setForm({ ...form, projeto_descricao: e.target.value })
          }
          className="w-full bg-slate-700 border border-slate-600 rounded-lg px-4 py-3 mb-4
                     text-white placeholder-slate-400 focus:outline-none focus:border-teal-500 h-24 resize-none"
        />
        <div className="flex gap-3">
          <button
            onClick={onClose}
            className="flex-1 py-3 rounded-lg border border-slate-600 text-slate-300
                       hover:bg-slate-700 transition-colors"
          >
            Cancelar
          </button>
          <button
            onClick={enviar}
            disabled={enviando || !form.nome || !form.email}
            className="flex-1 py-3 rounded-lg bg-teal-600 font-bold hover:bg-teal-500
                       transition-colors disabled:opacity-40 disabled:cursor-not-allowed"
          >
            {enviando ? "Enviando..." : "Enviar"}
          </button>
        </div>
      </div>
    </div>
  );
}

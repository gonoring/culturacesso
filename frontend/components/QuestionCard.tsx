"use client";

type Opcao = {
  valor: any;
  label: string;
};

type QuestionCardProps = {
  texto: string;
  tipo: "single_choice" | "multi_choice" | "boolean";
  opcoes: Opcao[];
  onResponder: (valor: any) => void;
  respostasMulti?: any[];
  onToggleMulti?: (valor: any) => void;
  onConfirmarMulti?: () => void;
};

export default function QuestionCard({
  texto,
  tipo,
  opcoes,
  onResponder,
  respostasMulti = [],
  onToggleMulti,
  onConfirmarMulti,
}: QuestionCardProps) {
  if (tipo === "multi_choice") {
    return (
      <div className="w-full max-w-xl bg-slate-800 rounded-2xl p-8 shadow-xl">
        <h2 className="text-xl font-semibold mb-6">{texto}</h2>
        <div className="flex flex-col gap-3">
          {opcoes.map((opcao) => {
            const selecionado = respostasMulti.includes(opcao.valor);
            return (
              <button
                key={String(opcao.valor)}
                onClick={() => onToggleMulti?.(opcao.valor)}
                className={`w-full text-left px-5 py-4 rounded-xl border transition-all duration-150 ${
                  selecionado
                    ? "border-teal-500 bg-slate-700"
                    : "border-slate-600 hover:border-teal-500 hover:bg-slate-700"
                }`}
              >
                <span className="flex items-center gap-3">
                  <span
                    className={`w-5 h-5 rounded border-2 flex items-center justify-center text-xs ${
                      selecionado
                        ? "border-teal-500 bg-teal-500 text-white"
                        : "border-slate-500"
                    }`}
                  >
                    {selecionado && "✓"}
                  </span>
                  {opcao.label}
                </span>
              </button>
            );
          })}
        </div>
        <button
          onClick={onConfirmarMulti}
          disabled={respostasMulti.length === 0}
          className="w-full mt-6 py-4 rounded-xl bg-teal-600 hover:bg-teal-500
                     font-bold transition-colors disabled:opacity-40 disabled:cursor-not-allowed"
        >
          Continuar
        </button>
      </div>
    );
  }

  return (
    <div className="w-full max-w-xl bg-slate-800 rounded-2xl p-8 shadow-xl">
      <h2 className="text-xl font-semibold mb-6">{texto}</h2>
      <div className="flex flex-col gap-3">
        {opcoes.map((opcao) => (
          <button
            key={String(opcao.valor)}
            onClick={() => onResponder(opcao.valor)}
            className="w-full text-left px-5 py-4 rounded-xl border border-slate-600
                       hover:border-teal-500 hover:bg-slate-700 transition-all duration-150"
          >
            {opcao.label}
          </button>
        ))}
      </div>
    </div>
  );
}

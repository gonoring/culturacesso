"use client";

type EditalCardProps = {
  titulo: string;
  orgao: string;
  valor_minimo: number | null;
  valor_maximo: number | null;
  dificuldade: "baixa" | "media" | "alta";
  data_encerramento: string | null;
  dias_restantes: number | null;
  url: string;
  areas: string[];
};

const dificuldadeCor = {
  baixa: "text-green-400",
  media: "text-yellow-400",
  alta: "text-red-400",
};

const dificuldadeLabel = {
  baixa: "Baixa",
  media: "Média",
  alta: "Alta",
};

const formatCurrency = (v: number) =>
  v.toLocaleString("pt-BR", { style: "currency", currency: "BRL", maximumFractionDigits: 0 });

function StatusBadge({ dias_restantes }: { dias_restantes: number | null }) {
  if (dias_restantes === null) {
    return (
      <span className="inline-flex items-center gap-1 text-xs font-medium px-2 py-0.5 rounded-full bg-teal-900/50 text-teal-400 border border-teal-800">
        <span className="w-1.5 h-1.5 rounded-full bg-teal-400" />
        Aberto
      </span>
    );
  }
  if (dias_restantes <= 7) {
    return (
      <span className="inline-flex items-center gap-1 text-xs font-medium px-2 py-0.5 rounded-full bg-red-900/50 text-red-400 border border-red-800">
        <span className="w-1.5 h-1.5 rounded-full bg-red-400 animate-pulse" />
        {dias_restantes <= 0 ? "Encerrado" : `${dias_restantes} dia${dias_restantes !== 1 ? "s" : ""} restante${dias_restantes !== 1 ? "s" : ""}`}
      </span>
    );
  }
  if (dias_restantes <= 30) {
    return (
      <span className="inline-flex items-center gap-1 text-xs font-medium px-2 py-0.5 rounded-full bg-yellow-900/50 text-yellow-400 border border-yellow-800">
        <span className="w-1.5 h-1.5 rounded-full bg-yellow-400" />
        {dias_restantes} dias restantes
      </span>
    );
  }
  return (
    <span className="inline-flex items-center gap-1 text-xs font-medium px-2 py-0.5 rounded-full bg-teal-900/50 text-teal-400 border border-teal-800">
      <span className="w-1.5 h-1.5 rounded-full bg-teal-400" />
      {dias_restantes} dias restantes
    </span>
  );
}

export default function EditalCard({
  titulo,
  orgao,
  valor_minimo,
  valor_maximo,
  dificuldade,
  data_encerramento,
  dias_restantes,
  url,
  areas,
}: EditalCardProps) {
  // Monta texto de faixa de valor
  let valorTexto: string | null = null;
  if (valor_minimo && valor_maximo) {
    valorTexto = `${formatCurrency(valor_minimo)} — ${formatCurrency(valor_maximo)}`;
  } else if (valor_maximo) {
    valorTexto = `Até ${formatCurrency(valor_maximo)}`;
  } else if (valor_minimo) {
    valorTexto = `A partir de ${formatCurrency(valor_minimo)}`;
  }

  return (
    <div className="bg-slate-800 rounded-xl p-5 border border-slate-700 hover:border-slate-600 transition-colors">
      {/* Header: titulo + status */}
      <div className="flex items-start justify-between gap-3">
        <div className="flex-1 min-w-0">
          <h3 className="font-semibold text-white leading-snug">{titulo}</h3>
          <p className="text-slate-400 text-sm mt-1">{orgao}</p>
        </div>
        <StatusBadge dias_restantes={dias_restantes} />
      </div>

      {/* Valor */}
      {valorTexto && (
        <div className="mt-3 bg-slate-900/50 rounded-lg px-3 py-2">
          <p className="text-xs text-slate-500 uppercase tracking-wide">Valor de captação</p>
          <p className="text-amber-400 font-bold text-lg">{valorTexto}</p>
        </div>
      )}

      {/* Info row: dificuldade + prazo */}
      <div className="flex items-center gap-4 mt-3 text-sm flex-wrap">
        <span className={dificuldadeCor[dificuldade]}>
          Dificuldade: {dificuldadeLabel[dificuldade]}
        </span>
        {data_encerramento && (
          <span className="text-slate-400">
            Encerra:{" "}
            {new Date(data_encerramento).toLocaleDateString("pt-BR")}
          </span>
        )}
      </div>

      {/* Link */}
      <a
        href={url.startsWith("http://") || url.startsWith("https://") ? url : "#"}
        target="_blank"
        rel="noopener noreferrer"
        className="inline-block mt-3 text-teal-400 text-sm hover:text-teal-300 transition-colors"
      >
        Ver edital completo →
      </a>
    </div>
  );
}

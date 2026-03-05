"use client";

type EditalCardProps = {
  titulo: string;
  orgao: string;
  valor_maximo: number | null;
  dificuldade: "baixa" | "media" | "alta";
  data_encerramento: string | null;
  url: string;
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

export default function EditalCard({
  titulo,
  orgao,
  valor_maximo,
  dificuldade,
  data_encerramento,
  url,
}: EditalCardProps) {
  return (
    <div className="bg-slate-800 rounded-xl p-5 border border-slate-700">
      <div className="flex items-start justify-between">
        <div className="flex-1 min-w-0">
          <h3 className="font-semibold text-white">{titulo}</h3>
          <p className="text-slate-400 text-sm mt-1">{orgao}</p>
        </div>
        {valor_maximo && (
          <span className="text-amber-400 font-bold text-lg ml-4 whitespace-nowrap">
            {valor_maximo.toLocaleString("pt-BR", {
              style: "currency",
              currency: "BRL",
            })}
          </span>
        )}
      </div>
      <div className="flex items-center gap-4 mt-3 text-sm">
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

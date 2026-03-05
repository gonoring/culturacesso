import Link from "next/link";

export default function Home() {
  return (
    <main className="min-h-screen bg-slate-900 text-white">
      {/* Hero */}
      <div className="flex flex-col items-center justify-center min-h-screen px-4 text-center">
        <div className="max-w-2xl">
          <p className="text-teal-400 font-medium mb-4 text-sm uppercase tracking-wider">
            Editais culturais do Espírito Santo
          </p>
          <h1 className="text-4xl md:text-6xl font-bold mb-6 leading-tight">
            Descubra quais editais{" "}
            <span className="text-teal-400">combinam com o seu projeto</span>
          </h1>
          <p className="text-slate-400 text-lg md:text-xl mb-10 leading-relaxed">
            Responda algumas perguntas rápidas e descubra os editais culturais
            abertos compatíveis com o seu perfil. Gratuito, sem cadastro.
          </p>

          <Link
            href="/trilha"
            className="inline-block bg-teal-600 hover:bg-teal-500 text-white font-bold
                       px-8 py-4 rounded-xl text-lg transition-colors"
          >
            Descobrir meus editais
          </Link>

          {/* Como funciona */}
          <div className="mt-20 grid grid-cols-1 md:grid-cols-3 gap-8 text-left">
            <div className="bg-slate-800 rounded-xl p-6">
              <div className="text-teal-400 text-2xl font-bold mb-2">1</div>
              <h3 className="font-semibold mb-2">Responda a trilha</h3>
              <p className="text-slate-400 text-sm">
                6 perguntas rápidas sobre seu projeto, natureza jurídica e área
                cultural.
              </p>
            </div>
            <div className="bg-slate-800 rounded-xl p-6">
              <div className="text-teal-400 text-2xl font-bold mb-2">2</div>
              <h3 className="font-semibold mb-2">Veja seus editais</h3>
              <p className="text-slate-400 text-sm">
                Receba uma lista dos editais abertos compatíveis com o seu
                perfil, com valores e prazos.
              </p>
            </div>
            <div className="bg-slate-800 rounded-xl p-6">
              <div className="text-teal-400 text-2xl font-bold mb-2">3</div>
              <h3 className="font-semibold mb-2">Submeta com assessoria</h3>
              <p className="text-slate-400 text-sm">
                Nossa equipe estrutura seu projeto e cuida da documentação. Você
                só paga se for aprovado.
              </p>
            </div>
          </div>
        </div>
      </div>
    </main>
  );
}

import React, { Fragment } from 'react';
import { Link } from 'react-router-dom';
import { LogoutButton } from '../components/Navigation';

import { truthy } from '../utils';

export default function AlunoDisciplina({ data }) {
    const { aluno = {}, atividades = [], disciplina = {} } = data;
    return <>

    <aside className="w-72 glass-sidebar h-screen sticky top-0 flex flex-col p-6">
        <div className="mb-10 text-center">
            <h2 className="text-xl font-bold tracking-tighter text-cyan-400">SECRETARIA DF</h2>
            <p className="text-[10px] text-gray-500 uppercase tracking-widest">Portal do Aluno</p>
        </div>

        <nav className="flex-1 space-y-2">
            <div className="text-[10px] font-bold text-gray-500 mb-2 ml-4">MINHA ÁREA</div>
            <Link to={"/aluno"} className="flex items-center px-4 py-3 rounded-xl hover:bg-white/5 transition-all text-gray-300 hover:text-white">
                Voltar
            </Link>
            <Link to={"/aluno"} className="flex items-center px-4 py-3 rounded-xl bg-cyan-500/10 text-cyan-400 border border-cyan-500/20">
                Disciplinas
            </Link>
        </nav>

        <div className="mt-auto pt-6 border-t border-white/10">
            <LogoutButton  className="flex items-center px-4 py-3 rounded-xl text-red-400 hover:bg-red-500/10 transition-all">
                Sair do Sistema
            </LogoutButton>
        </div>
    </aside>

    <main className="flex-1 p-10 overflow-y-auto">
        <header className="flex justify-between items-center mb-10">
            <div>
                <p className="text-sm text-cyan-400 font-bold">Disciplina</p>
                <h1 className="text-3xl font-bold">{disciplina.nome}</h1>
                <p className="text-gray-400">Código {disciplina.codigo} · {disciplina.carga_horaria}h</p>
            </div>
            <div className="flex items-center gap-4">
                <div className="text-right">
                    <p className="text-sm font-bold">{aluno.nome}</p>
                    <p className="text-[10px] text-cyan-400">Matrícula {aluno.matricula}</p>
                </div>
                {truthy(aluno.foto_perfil) ? <> 
                <img src={`/arquivos/perfil/${encodeURIComponent(aluno.foto_perfil)}`} alt={`Foto de ${aluno.nome}`} className="w-12 h-12 rounded-full border-2 border-white/20 object-cover" />
                 </> : <> 
                <div className="w-12 h-12 rounded-full bg-gradient-to-r from-cyan-500 to-blue-500 border-2 border-white/20"></div>
                 </>}
            </div>
        </header>

        <section className="glass-card aluno-card rounded-[32px] p-8 mb-8">
            <div className="flex justify-between items-center mb-6">
                <h2 className="text-xl font-bold">Professores</h2>
                <span className="text-sm text-gray-400">Vinculados à sua turma</span>
            </div>
            <div className="flex flex-wrap gap-2">
                {disciplina.professores.length ? <>{disciplina.professores.map((professor, index24) => <Fragment key={professor?.id ?? index24}>
                <span className="aluno-chip">{professor}</span>
                </Fragment>)}</> : <>
                <span className="text-sm text-gray-400">Nenhum professor associado.</span>
                </>}
            </div>
        </section>

        <section className="glass-card aluno-card rounded-[32px] p-8">
            <div className="flex justify-between items-center mb-6">
                <h2 className="text-xl font-bold">Atividades e Arquivos</h2>
                <span className="text-sm text-gray-400">Materiais enviados pelo professor</span>
            </div>

            <div className="aluno-exclusive-activities">
                {atividades.length ? <>{atividades.map((atividade, index25) => <Fragment key={atividade?.id ?? index25}>
                <article className="aluno-exclusive-activity">
                    <div>
                        <strong>{atividade.titulo}</strong>
                        <span>{atividade.professor} · Entrega: {atividade.data_entrega}</span>
                        <p>{atividade.descricao}</p>
                        <small>{atividade.data}</small>
                    </div>
                    {truthy(atividade.arquivo) ? <> 
                    <a href={`/arquivos/download/${encodeURIComponent(atividade.arquivo)}`}>Baixar arquivo</a>
                     </> : <>  </>}
                </article>
                </Fragment>)}</> : <>
                <div className="aluno-activity-empty">Nenhuma atividade lançada nesta disciplina.</div>
                </>}
            </div>
        </section>
    </main>

    
    </>;
}
